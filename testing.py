import requests
import sounddevice as sd
import wavio
import tempfile
import os
import numpy as np


API_URL = "http://0.0.0.0:8000/call" #"https://transport-bot.onrender.com/call"

def record_audio(duration=5, fs=16000):
    print("🎙️ Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()
    return recording, fs

def save_wav(recording, fs):
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavio.write(tmpfile.name, recording, fs, sampwidth=2)
    return tmpfile.name

if __name__ == "__main__":
    # Step 1: Record voice
    audio, fs = record_audio(duration=5)
    wav_file = save_wav(audio, fs)

    # Step 2: Send to API
    with open(wav_file, "rb") as f:
        files = {"audio": f}
        response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        # Save bot reply audio
        bot_reply_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with open(bot_reply_file.name, "wb") as f:
            f.write(response.content)

        print("🤖 Bot reply received, playing audio...")
        os.system(f"mpg123 {bot_reply_file.name}")  # Linux/macOS playback
    else:
        print("❌ API error:", response.text)
