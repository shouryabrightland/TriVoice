import torch
import numpy as np
import sounddevice as sd
from API.modules.speaker import Speaker
# Load via Torch Hub
vad_model, _ = torch.hub.load(
    repo_or_dir="models/snakers4_silero-vad_master",
    model="silero_vad",
    source="local"
)
vad = vad_model


SR = 16000
PastBuffer_Size = 500 #16 sec 
BUFFER_SIZE = 8000  # 0.5sec
CHUNK = 512        # ~0.032 sec
SILENCE_FRAMES = 50 #~1.6sec
MAX_AUDIO_LENGTH = 15 #15sec

def listen_for_voice(speaker: Speaker):
    print("Waiting for voice...")
    once = False
    with sd.InputStream(samplerate=SR, channels=1, blocksize=CHUNK) as stream:
        #to check if flow reaching this or not..
        if not once:
            print("started getting buffer...")
            speaker.play("effects/mic.mp3",volume=1,wait=False)
            once = True
        
        #variables
        buffer = []
        PastBuffer = []
        started = False
        recording = []
        silence_count = 0

        #main loop
        while True:
            #single itration = 1 chunk

            if silence_count > SILENCE_FRAMES:
                print("recording ended")
                break

            audio, _ = stream.read(CHUNK)
            audio = np.squeeze(audio).astype(np.float32)

            if started:
                recording.extend(audio)
                if len(recording) > SR*MAX_AUDIO_LENGTH:
                    print("[warning] crossing max audio context length!!")
                    #we will fix this while last polishing!!

            #will store pre-roll
            if not started:
                buffer.extend(audio)
                if len(buffer) > BUFFER_SIZE:
                    buffer = buffer[-BUFFER_SIZE:]


            # threshold / fast pre-check + background energy

            #storing bg energy
            level = np.abs(audio).mean()
            PastBuffer.append(level)
            if len(PastBuffer) > PastBuffer_Size:
                    PastBuffer = PastBuffer[-PastBuffer_Size:]
            
            #dynamic threshold
            meanenv = max(sum(PastBuffer)/len(PastBuffer),1e-3) if PastBuffer else 1e-3
            vol = ((level/meanenv)*100) -100
            #delta(in silence) if meanenv < (noise amount) else delta(in noise)
            before_start = 190 if meanenv < 0.05 else 60 # delta is more if silence and less if too noise
            after_start = 40
            if not (vol > (before_start if not started else after_start)): #40-----
                #nothing found as activity
                if started: #increase silent count when recording and no activity detected
                    silence_count+=1
                continue
            print(vol,meanenv)
            #if we reach here means we detected activity!!
            #runing VAD
            audio_tensor = torch.from_numpy(audio).unsqueeze(0)
            prob = vad(audio_tensor, 16000).item()
            print(prob,"probability of speech")
            if (prob > 0.7):
                 #finally detect voice

                if (not started):
                    #started recording
                    started = True
                    recording.extend(buffer.copy())   # add pre-roll
                    print("Voice detected, started recording...")
                    continue
                else:
                    #already recording so we reset silent count
                    silence_count = 0
            else:
                #if low probability
                #then also increase silent count
                if started:
                    silence_count+=1

    return np.array(recording, dtype=np.float32)
                
            