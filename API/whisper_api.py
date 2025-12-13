import soundfile as sf
import sounddevice as sd
from faster_whisper import WhisperModel
import API.modules.voice_detect as detector
# ---------------------------
# Audio recording function
# ---------------------------
# def record_audio(file_path="input.wav", duration=5, samplerate=16000):
#     """
#     Records audio from microphone and saves as WAV
#     """
#     print(f"Recording {duration} seconds...")
#     audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
#     sd.wait()  # wait until recording is finished
#     sf.write(file_path, audio_data, samplerate)
#     print(f"Saved recording to {file_path}")
#     return file_path

# ---------------------------
# Whisper API class
# ---------------------------
class WhisperAPI:
    def __init__(self, model_name="tiny"):
        """
        model_name: "tiny", "small", "medium", "large" (tiny is best for Pi)
        """
        print("Loading Whisper tiny.en model...")
        self.model = WhisperModel(
            "tiny.en",
            device="cpu",
            compute_type="int8"
        )
        self.detector = detector
        self.recording_file = "input.wav"

    #def transcribe(self, audio_path):
    #    """
    #    Transcribes audio file to text
    #    """
    #    segments, _ = self.model.transcribe(audio_path)
    #    text = " ".join([segment.text for segment in segments])
    #    return text.strip()

    def record_and_transcribe(self):
        """
        Records audio and immediately transcribes it
        """
        # i done this so that i can put custom message during debeg in this text var...
        text = ""
        while not text:
            print("initizalising voice to text----------------")
            audio = self.detector.listen_for_voice()
            audio = audio.astype("float32")


            segments, _ = self.model.transcribe(
                audio,
                language="en",
                task="transcribe",
                beam_size=1,
                best_of=1,
                temperature=0.0,
                vad_filter=False
            )
            text = " ".join(s.text for s in segments).strip(" ")
        print("Transcribed:", text)
        return text
        # for debug perpose.. to check what is recording...
        # sf.write(self.recording_file, audio, 16000)
        # print('written...')
        
