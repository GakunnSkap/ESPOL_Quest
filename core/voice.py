# core/voice.py
import threading, time
from collections import deque

class VoiceListener:
    def __init__(self, language="es-ES", wake_words=None, device_index=None, backend_preference=None):
        self.language = language
        self.wake_words = set(w.lower() for w in (wake_words or []))
        self.device_index = device_index
        self.backend_preference = backend_preference
        self.queue = deque()
        self._stop = False
        self._thread = None
        self._backend = None

        # Dispositivos disponibles y puntero actual
        self._devices = self._enumerate_devices()  # [(idx, name, kind)]
        self._device_pos = self._find_pos_by_index(device_index)

    # ---------- APIs públicas ----------
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join(timeout=1.0)

    def restart(self):
        """Reinicia el hilo con el device_index actual."""
        self.stop()
        self.start()

    def get_commands(self):
        out = []
        while self.queue:
            out.append(self.queue.popleft())
        return out

    def list_devices(self):
        """Devuelve lista [(idx, name, kind)]"""
        return list(self._devices)

    def set_device_index(self, new_index: int):
        """Setea por índice absoluto (sounddevice/speech_recognition) y reinicia."""
        pos = self._find_pos_by_index(new_index)
        if pos is None:
            return False
        self._device_pos = pos
        self.device_index = self._devices[pos][0]
        self.restart()
        return True

    def refresh_devices(self):
        """Re-escanea dispositivos y reposiciona el puntero si es posible."""
        self._devices = self._enumerate_devices()
        self._device_pos = self._find_pos_by_index(self.device_index)

    def current_device(self):
        """(idx, name) o (None, 'Sin micrófonos')."""
        if not self._devices:
            return (None, "Sin micrófonos")
        if self._device_pos is None:
            self._device_pos = 0
            self.device_index = self._devices[0][0]
        idx, name, _ = self._devices[self._device_pos]
        return (idx, name)

    def next_device(self):
        if not self._devices:
            self.refresh_devices()
            return self.current_device()
        self._device_pos = 0 if self._device_pos is None else (self._device_pos + 1) % len(self._devices)
        self.device_index = self._devices[self._device_pos][0]
        self.restart()
        return self.current_device()

    def prev_device(self):
        if not self._devices:
            self.refresh_devices()
            return self.current_device()
        self._device_pos = 0 if self._device_pos is None else (self._device_pos - 1) % len(self._devices)
        self.device_index = self._devices[self._device_pos][0]
        self.restart()
        return self.current_device()

    # ---------- Internos ----------
    def _enumerate_devices(self):
        out = []
        # sounddevice
        try:
            import sounddevice as sd
            for i, dev in enumerate(sd.query_devices()):
                if dev.get("max_input_channels", 0) > 0:
                    out.append((i, f"{dev['name']}", "sd"))
        except Exception:
            pass
        # speech_recognition
        try:
            import speech_recognition as sr
            for i, name in enumerate(sr.Microphone.list_microphone_names()):
                if (i, name, "sr") not in out:
                    out.append((i, name, "sr"))
        except Exception:
            pass
        return out

    def _find_pos_by_index(self, idx):
        if idx is None:
            return None
        for pos, (i, _name, _k) in enumerate(self._devices):
            if i == idx:
                return pos
        return None

    # ---------- Loop & backends ----------
    def _run(self):
        if self.backend_preference in (None, "vosk"):
            if self._run_vosk():
                return
        if self.backend_preference in (None, "sr"):
            if self._run_sr():
                return
        self._backend = None
        while not self._stop:
            time.sleep(0.25)

    def _run_vosk(self):
        try:
            import vosk, json, sounddevice as sd
            self._backend = "vosk"

            model = vosk.Model(lang="es")

            samplerate = 16000
            try:
                dev = sd.query_devices(self.device_index) if self.device_index is not None else sd.query_devices(kind='input')
                sr = int(dev.get("default_samplerate") or 16000)
                samplerate = sr
            except Exception:
                pass

            rec = vosk.KaldiRecognizer(model, samplerate)
            rec.SetWords(True)

            def callback(indata, frames, time_, status):
                data = indata.tobytes()
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    self._maybe_push(self._extract_text_vosk(res))

            dev_arg = self.device_index if isinstance(self.device_index, int) else None
            with sd.InputStream(samplerate=samplerate, blocksize=4096, dtype='int16', channels=1, device=dev_arg, callback=callback):
                import time
                while not self._stop:
                    time.sleep(0.05)
            return True
        except Exception:
            return False

    def _run_sr(self):
        try:
            import speech_recognition as sr
            self._backend = "sr"
            r = sr.Recognizer()
            mic = sr.Microphone(device_index=self.device_index)
            with mic as source:
                r.adjust_for_ambient_noise(source)
            while not self._stop:
                with mic as source:
                    audio = r.listen(source, phrase_time_limit=3)
                try:
                    txt = r.recognize_google(audio, language=self.language)
                    self._maybe_push(txt)
                except Exception:
                    pass
            return True
        except Exception:
            return False

    def _extract_text_vosk(self, res_json):
        import json
        try:
            data = json.loads(res_json)
            return (data.get("text") or "").strip()
        except Exception:
            return ""

    def _maybe_push(self, txt):
        if not txt:
            return
        s = txt.lower().strip()
        if self.wake_words and not any(w in s for w in self.wake_words):
            return
        self.queue.append(s)
