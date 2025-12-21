#wake word detection

import sounddevice as sd
import numpy as np
from collections import deque
import openwakeword

SAMPLE_RATE = 16000
FRAME_SIZE = 320              # 20 ms
BUFFER_SECONDS = 1.2
BUFFER_FRAMES = int(BUFFER_SECONDS * SAMPLE_RATE / FRAME_SIZE)

# Load wake word model
oww = openwakeword.Model(
    wakeword_models=["hey_jarvis"]  # example
)

ring_buffer = deque(maxlen=BUFFER_FRAMES)
activated = False

def audio_callback(indata, frames, time, status):
    global activated

    pcm = indata[:, 0].copy()   # mono
    pcm_int16 = (pcm * 32767).astype(np.int16)

    # store for rewind
    ring_buffer.append(pcm_int16)

    # wake word detection
    prediction = oww.predict(pcm_int16)
    score = prediction["hey_jarvis"]

    if score > 0.7 and not activated:
        activated = True
        print("WAKE WORD DETECTED")

        # send buffered audio to Whisper
        send_to_whisper(list(ring_buffer))

    if activated:
        send_to_whisper(pcm_int16)

def send_to_whisper(pcm_chunk):
    """
    This should PUSH audio to Whisper server via queue/socket.
    DO NOT BLOCK HERE.
    """
    pass

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    blocksize=FRAME_SIZE,
    callback=audio_callback
):
    print("Mic server running...")
    while True:
        pass
