from API.modules.speaker import Speaker
speaker = Speaker(samplerate=16000)
print("It's TryVoice")
speaker.play("effects/try.wav",wait=True)
speaker.play("effects/song.mp3",volume=0.4,wait=False)
import time
from API.whisper_api import WhisperAPI
from API.piper_api import PiperTTS
from API.ollama_api import OllamaAPI
from API.modules.chat import Chat
from types import FunctionType

from IntentManager.expectation import detect_expectation
from IntentManager.intent import detect_intents
# from API.modules.intent import detect_intents
# from API.modules.expectation import detect_expectation



class serve:
    def __init__(self,server: FunctionType):
        #time.sleep(1)
        print("Loading Services...")
        tts = PiperTTS(speaker,"voices/en_US-lessac-low.onnx")
        whisper = WhisperAPI(speaker=speaker)
        ollama = OllamaAPI()
        chat = Chat(max_messages=50)
        print("Awaking Agent..")
        Req = Request(whisper,chat=chat)
        Res = Response(ollama,tts,chat,speaker)
        Res.askAI()
        while not Res.isTerminated:
            #whisper mic
            #try:
                server(Req.listen(),Res)
            #except:
            #    Res.exit("server issue")

class Request:
    def __init__(self,whisper: WhisperAPI,chat:Chat):
        self.whisper = whisper
        self.message = None
        self.intent = None
        self.chat = chat
    def listen(self):
        userMessage = self.whisper.record_and_transcribe()
        self.message = userMessage
        self.intent = detect_intents(userMessage)
        # exp = detect_expectation(self.chat.get()[-1])
        # intent = detect_intents(userMessage,exp)
        #print(intent,exp)
        #print(intent_middleware(i["user"],intent[1],intent[2],exp))
        return self

    


class Response:
    def __init__(self,ollamaAPI:OllamaAPI,tts:PiperTTS,chat:Chat,speaker:Speaker):
        self.isTerminated = False
        self.current_expectation = None
        self.ollama = ollamaAPI
        self.tts = tts
        self.chat = chat
        self.speaker = speaker
        self.payload = {}
    def expecting(self,expect: str):
        print("updating expectation" , expect)
        self.current_expectation = expect

    def send(self,message):
        self.tts.speak(message)
        self.chat.add("user",message)
        print("[Manual]",message)

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
            self.current_expectation = detect_expectation(res)
            res += buffer
            buffer = ""
        
        self.chat.add("assistant", res)
