import requests

class OllamaAPI:
    def __init__(self, model="gemma3:1b"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def ask(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        res = requests.post(self.url, json=payload)
        data = res.json()

        return data["message"]["content"]
