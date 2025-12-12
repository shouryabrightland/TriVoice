import soundfile as sf
import sounddevice as sd
from faster_whisper import WhisperModel
import API.modules.voice_detect as detector
# ---------------------------
# Audio recording function
# ---------------------------
def record_audio(file_path="input.wav", duration=5, samplerate=16000):
    """
    Records audio from microphone and saves as WAV
    """
    print(f"Recording {duration} seconds...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()  # wait until recording is finished
    sf.write(file_path, audio_data, samplerate)
    print(f"Saved recording to {file_path}")
    return file_path

# ---------------------------
# Whisper API class
# ---------------------------
class WhisperAPI:
    def __init__(self, model_name="tiny"):
        """
        model_name: "tiny", "small", "medium", "large" (tiny is best for Pi)
        """
        print(f"Loading Whisper model: {model_name} ...")
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
        self.detector = detector
        self.recording_file = "input.wav"

    def transcribe(self, audio_path):
        """
        Transcribes audio file to text
        """
        segments, _ = self.model.transcribe(audio_path)
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    def record_and_transcribe(self, duration=5):
        """
        Records audio and immediately transcribes it
        """
        sf.write(self.recording_file, self.detector.listen_for_voice(), 16000)
        text = self.transcribe(self.recording_file)
        print("we got some text:-",text)
        #audio_file = record_audio(self.recording_file, duration)
        #return self.transcribe(audio_file)
