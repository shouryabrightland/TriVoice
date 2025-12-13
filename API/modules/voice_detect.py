import torch
import numpy as np
import sounddevice as sd

# Load via Torch Hub
vad_model, _ = torch.hub.load(
    repo_or_dir="models/snakers4_silero-vad_master",
    model="silero_vad",
    source="local"
)
vad = vad_model


THRESHOLD = 0.2  # reduce if mic is quiet
SR = 16000
PastBuffer_Size = 100 #10 sec 
BUFFER_SIZE = 8000  # 0.5 sec
CHUNK = 512        # 0.1 sec
SILENCE_FRAMES = 40

def listen_for_voice():
    print("Waiting for voice...")

    with sd.InputStream(samplerate=SR, channels=1, blocksize=CHUNK) as stream:
        buffer = []
        PastBuffer = []
        started = False
        recording = []
        silence_count = 0
        while True:
            if silence_count>SILENCE_FRAMES:
                print("recording ended")
                break

            audio, _ = stream.read(CHUNK)
            audio = np.squeeze(audio).astype(np.float32)
            if started:
                recording.extend(audio)


            #will store pre-roll
            if not started:
                buffer.extend(audio)
                if len(buffer) > BUFFER_SIZE:
                    buffer = buffer[-BUFFER_SIZE:]

            # threshold / fast pre-check
            level = np.abs(audio).mean()
            PastBuffer.append(level)
            if len(PastBuffer) > PastBuffer_Size:
                    PastBuffer = PastBuffer[-PastBuffer_Size:]
            meanenv = np.abs(PastBuffer).mean()
            #print(meanenv,THRESHOLD,level,meanenv-level)

            #dynamic audio check!!!
            if not ((meanenv-level)<-0.1):
                if started:
                    silence_count+=1
                continue
            print("level reached! triggered main check!")

            #is voice??
            audio_tensor = torch.from_numpy(audio).unsqueeze(0)
            prob = vad(audio_tensor, 16000).item()
            print(prob,"prob")
            if (not started) and (prob > 0.7):
                print("Voice detected, starting record...")
                started = True
                recording.extend(buffer.copy())   # add pre-roll
                continue
            # If already recording:
            if prob > 0.5:
                silence_count = 0

    return np.array(recording, dtype=np.float32)
                
            