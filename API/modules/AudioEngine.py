import threading
import queue
import sounddevice as sd
import soundfile as sf
import numpy as np

class AudioEngine:
    def __init__(self, samplerate=16000):
        self.SR = samplerate
        self.q = queue.Queue()
        self.running = True

        self.bg_stop_flag = False

        print("opening output stream...")
        self.stream = sd.OutputStream(
            samplerate=self.SR,
            channels=1,
            dtype="float32",
            blocksize=1024
        )
        self.stream.start()
        print("opened output stream...")

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self.thread.start()

    # ─────────────────────────────
    # PUBLIC API
    # ─────────────────────────────

    def play_bg_file(self, file_path, volume=0.6):
        self.q.put(("bg_file", file_path, volume))

    def play_tts_file(self, file_path, volume=1.0):
        self.stop_bg()
        self.q.put(("tts_file", file_path, volume))

    def play_samples(self, samples: np.ndarray):
        self.stop_bg()
        self.q.put(("samples", samples, None))

    def stop_bg(self):
        self.bg_stop_flag = True
        sd.stop()

    def shutdown(self):
        self.running = False
        self.q.put(("exit", None, None))

    # ─────────────────────────────
    # WORKER LOOP
    # ─────────────────────────────

    def _run(self):
        while self.running:
            job, a, b = self.q.get()

            if job == "exit":
                self.q.task_done()
                break

            if job == "bg_file":
                self._play_bg_file(a, b)

            elif job == "tts_file":
                self._play_tts_file(a, b)

            elif job == "samples":
                self._play_samples(a)
            self.q.task_done()
            

    # ─────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────

    def _play_bg_file(self, file_path, volume):
        data, sr = sf.read(file_path, dtype="float32")
        if sr != self.SR:
            data = self._resample(data, sr)

        data *= volume
        self.bg_stop_flag = False

        chunk = 1024
        for i in range(0, len(data), chunk):
            if self.bg_stop_flag:
                break
            self.stream.write(data[i:i+chunk])

    def _play_tts_file(self, file_path, volume):
        self.bg_stop_flag = True
        sd.stop()

        data, sr = sf.read(file_path, dtype="float32")
        if sr != self.SR:
            data = self._resample(data, sr)

        self.stream.write(data * volume)

    def _play_samples(self, samples):
        self.bg_stop_flag = True
        self.stream.write(samples)

    def _resample(self, data, sr):
        if data.ndim > 1:
            data = data.mean(axis=1)

        ratio = self.SR / sr
        x_old = np.arange(len(data))
        x_new = np.linspace(0, len(data) - 1, int(len(data) * ratio))
        return np.interp(x_new, x_old, data).astype(np.float32)
