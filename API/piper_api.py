import wave
from piper.voice import PiperVoice
import sounddevice as sd
import soundfile as sf
import numpy as np
import time



class PiperTTS:
    def __init__(self, model_path):
        self.model_path = model_path
        # Load the voice model
        print("loading Piper voice...",model_path)
        self.voice = PiperVoice.load(model_path)
        print("loaded",model_path)
        SR = 16000

        #for streaming
        print("opening output stream...")
        self.stream = sd.OutputStream(samplerate=SR, channels=1, dtype="float32")
        self.stream.start()
        print("opened output stream...")

    def play_wav(self, file_path, volume=1.0,wait=True):
        data, samplerate = sf.read(file_path, dtype="float32")
        # safety clamp
        volume = max(0.0, min(volume, 1.0))
        data *= volume
        sd.play(data, samplerate)
        if wait:
            sd.wait()


    def speak(self, text, output_file="output.wav"):
        # Open a WAV file and write audio
        with wave.open(output_file, "w") as wf:
            # Configure WAV format
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.voice.config.sample_rate)

            # Generate audio raw PCM frames
            self.voice.synthesize_wav(text, wf)
            self.play_wav(output_file)

        return output_file

    def speak_live(self, text):
        sd.stop()
        CROSSFADE_SAMPLES = 16000   # ~20 ms at 16kHz
        DELAY = 0.055            # 55 ms

        prev_tail = None

        audio_gen = self.voice.synthesize(text)

        for chunk in audio_gen:
            samples = chunk.audio_float_array
            if samples is None:
                continue

            samples = np.asarray(samples, dtype=np.float32)

            # 🔧 simple crossfade to kill buzz
            if prev_tail is not None:
                fade_len = min(CROSSFADE_SAMPLES, len(samples), len(prev_tail))
                if fade_len > 0:
                    fade_in = np.linspace(0.0, 1.0, fade_len)
                    fade_out = 1.0 - fade_in

                    samples[:fade_len] = (
                        samples[:fade_len] * fade_in +
                        prev_tail[-fade_len:] * fade_out
                    )

            self.stream.write(samples)

            # store tail
            prev_tail = samples[-CROSSFADE_SAMPLES:].copy()

            # small breathing delay
            time.sleep(DELAY)
