from API.whisper_api import WhisperAPI
from API.piper_api import PiperTTS
from API.ollama_api import OllamaAPI

whisper = WhisperAPI()
tts = PiperTTS("voices/en_US-lessac-low.onnx")
ollama = OllamaAPI()


chatHistory = [
    {"role": "system", "content": "Give short answers. Use simple sentences. Avoid extra words. Do not use markdown or emojis. Talk in a normal speaking style, like you are talking to close friend. Keep replies brief unless the user clearly asks for more"}
]
# Whisper
print("Whisper...")
userMessage = whisper.record_and_transcribe(10)
chatHistory.append({"role": "user", "content": userMessage})

# # TEST 2: Ollama
# print("Ollama...")
# response = ollama.ask(chatHistory)
# chatHistory.append({"role": "assistant", "content": userMessage})
# print("Ollama says:", response)

# # TEST 3: Piper
# print("Piper...")
# tts.speak(response, "test2.wav")
