from API.whisper_api import WhisperAPI
from API.piper_api import PiperTTS
from API.ollama_api import OllamaAPI
import API.modules.norm_msg as norm
from API.modules.intent import detect_intent


print("Loading Services...")
tts = PiperTTS("voices/en_US-lessac-low.onnx")
print("It's TryVoice")
tts.speak("It's TryVoice")
tts.play_wav("effects/song.mp3",volume=0.4,wait=False)
whisper = WhisperAPI(tts)
ollama = OllamaAPI()

chatHistory = [
    {"role": "system", "content": '''You are a friendly voice assistant.
     your name is TryVoice.
You speak in short, clear sentences.
You explain things slowly, like talking.
After explaining, you usually ask a small follow-up question to continue the conversation.
If the user seems interested or says something short, you continue explaining naturally.
No markdown. No emojis. No lists.'''}
]

def agent(chatHistory = chatHistory):
    buffer = ""
    res = ""
    for chunk in ollama.ask_stream(chatHistory):
        if chunk.startswith("[error]"):
            print(chunk)
            break

        print(chunk, end="", flush=True)
        buffer += chunk.strip("\n")

        if buffer.endswith((".", "?", "!", ",")):
            tts.speak_live(buffer)
            res += buffer
            buffer = ""
    if buffer.strip():
        tts.speak_live(buffer)
        res += buffer
        buffer = ""
    chatHistory.append({"role": "assistant", "content": res})


print("Awaking Agent..")
agent(chatHistory)

i = 0
while i<1:

    # Whisper
    print("Whisper...")
    userMessage = whisper.record_and_transcribe()
    intent = detect_intent(userMessage)

if intent == "EXIT":
    system_voice.play("goodbye.wav")
    shutdown()

elif intent == "COMMAND_MODE":
    system_voice.play("command_mode.wav")
    enter_command_mode()

elif intent == "PASSIVE":
    chatHistory.append({
        "role": "user",
        "content": "Please continue."
    })
    agent(chatHistory)

else:
    chatHistory.append({
        "role": "user",
        "content": userMessage
    })
    agent(chatHistory)

    

