import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import threading
import time
from groq import Groq
from pynput import mouse
from pynput.keyboard import Controller, Key

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

SAMPLE_RATE = 16000
recording = False
audio_chunks = []
record_thread = None


def record_audio():
    global audio_chunks
    audio_chunks = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        while recording:
            data, _ = stream.read(1024)
            audio_chunks.append(data.copy())


def transcribe_and_copy():
    if not audio_chunks:
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name

    with wave.open(tmp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(np.concatenate(audio_chunks).tobytes())

    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=f,
                language="ru",
            )
        print(f"✓ Вставляю: {result.text}")
        time.sleep(0.1)
        kb = Controller()
        kb.type(result.text)
    finally:
        os.unlink(tmp_path)


def on_click(x, y, button, pressed):
    global recording, record_thread

    if button != mouse.Button.x2:
        return

    if pressed:
        if not recording:
            recording = True
            print("🎙  Запись... (Mouse5 — остановить)")
            record_thread = threading.Thread(target=record_audio, daemon=True)
            record_thread.start()
        else:
            recording = False
            if record_thread:
                record_thread.join()
            print("⏳ Транскрибирую...")
            threading.Thread(target=transcribe_and_copy, daemon=True).start()


print("Голосовой ввод запущен. Mouse5 — начать/закончить запись.")
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
