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


THRESHOLD = 5/1000  # reduce if mic is quiet
BUFFER_SIZE = 8000  # 0.5 sec
CHUNK = 512        # 0.1 sec
SILENCE_FRAMES = 40

def listen_for_voice():
    print("Waiting for voice...")

    with sd.InputStream(samplerate=16000, channels=1, blocksize=CHUNK) as stream:
        buffer = []
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
            if level < THRESHOLD:
                if started:
                    silence_count+=1
                continue

            #print("listening..")

            #is voice??
            audio_tensor = torch.from_numpy(audio).unsqueeze(0)
            prob = vad(audio_tensor, 16000).item()
            if (not started) and (prob > 0.7):
                print("Voice detected, starting record...")
                started = True
                recording.extend(buffer.copy())   # add pre-roll
                continue
            # If already recording:
            if prob > 0.5:
                silence_count = 0

    return np.array(recording, dtype=np.float32)
                
            