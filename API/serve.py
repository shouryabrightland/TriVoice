from API.whisper_api import WhisperAPI
from API.piper_api import PiperTTS
from API.ollama_api import OllamaAPI
from API.modules.chat import Chat
from API.modules.speaker import Speaker
from types import FunctionType
class serve:
    def __init__(self,server: FunctionType):
        speaker = Speaker(samplerate=16000)
        print("It's TryVoice")
        speaker.play("effects/try.wav",wait=True)
        print("Loading Services...")
        self.tts = PiperTTS(speaker,"voices/en_US-lessac-low.onnx")
        speaker.play("effects/song.mp3",volume=0.4,wait=False)
        whisper = WhisperAPI(speaker=speaker)
        ollama = OllamaAPI()
        chat = Chat(max_messages=50)
        print("Awaking Agent..")
        Req = Request(whisper)
        Res = Response(ollama,self.tts,chat,speaker)
        Res.askAI()
        while not Res.isTerminated:
            #whisper mic
            #try:
                server(Req.__get__(),Res)
            #except:
            #    Res.exit("server issue")

class Request:
    def __init__(self,whisper: WhisperAPI):
        self.whisper = whisper
        self.message = None
    def __get__(self):
        userMessage = self.whisper.record_and_transcribe()
        self.message = userMessage
        return self

    


class Response:
    def __init__(self,ollamaAPI:OllamaAPI,tts:PiperTTS,chat:Chat,speaker:Speaker):
        self.isTerminated = False
        self.ollama = ollamaAPI
        self.tts = tts
        self.chat = chat
        self.speaker = speaker
           
    def send(self,message):
        self.tts.speak(message)
        self.chat.add("user",message)

    def exit(self,msg: str = None):
        msg = "Shut Down with no message" if not msg else "shutdown due to "+str(msg)
        print(msg)
        self.tts.writeWAV(msg)
        self.speaker.play("output.wav")

        
        self.isTerminated = True
    
    def askAI(self,message: str = None):
        #global current_expectation
        if message:
            self.chat.add("user",message)

        buffer = ""
        res = ""

        for chunk in self.ollama.ask_stream(self.chat.get()):
            if chunk.startswith("[error]"):
                print(chunk)
                self.tts.speak(chunk)
                break

            print(chunk, end="", flush=True)
            buffer += chunk.strip("\n")

            if buffer.endswith((".", "?", "!", ",")):
                self.tts.speak(buffer)
                res += buffer
                buffer = ""
        if buffer.strip():
            self.tts.speak(buffer)
            #current_expectation = detect_expectation(res)
            res += buffer
            buffer = ""
        
        self.chat.add("assistant", res)

