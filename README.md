# 🎙️ TryVoice v2

A local, offline-first voice assistant built in Python.
Designed for low-resource systems like Raspberry Pi.
No cloud. No spying. Full control.

---

### new ARCH- [Building - incomplete]

## 🖥️ Requirements

### 1. Python

* Version: **Python 3.9+**
* Download:
  [https://www.python.org/downloads/](https://www.python.org/downloads/)

Check installation:

```bash
python --version
```

---

### 2. Ollama (Local LLM Backend)

* Download:
  [https://ollama.com/download](https://ollama.com/download)

After installing, pull a model:

```bash
ollama pull gemma3:1b
```

Start Ollama server:

```bash
ollama serve
```

⚠️ Ollama **must be running** before starting TryVoice.

---

## 📦 Installation

### Create virtual environment

```bash
python -m venv venv
```

### Activate environment

Linux / macOS:

```bash
source venv/bin/activate
```

Windows (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---





