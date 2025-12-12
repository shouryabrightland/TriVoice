import wave
from piper.voice import PiperVoice
import sounddevice as sd
import soundfile as sf

def play_wav(file_path):
    data, samplerate = sf.read(file_path, dtype='float32')
    sd.play(data, samplerate)
    sd.wait()

class PiperTTS:
    def __init__(self, model_path):
        self.model_path = model_path
        # Load the voice model
        self.voice = PiperVoice.load(model_path)

    def speak(self, text, output_file="output.wav"):
        # Open a WAV file and write audio
        with wave.open(output_file, "w") as wf:
            # Configure WAV format
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.voice.config.sample_rate)

            # Generate audio raw PCM frames
            self.voice.synthesize_wav(text, wf)
            play_wav(output_file)

        return output_file
