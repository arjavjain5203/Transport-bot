import requests
import sounddevice as sd
import wavio
import tempfile
import os
import numpy as np
import platform
import subprocess

API_URL = "https://transport-bot-8651.onrender.com/call"  # API URL

def record_audio(duration=5, fs=16000):
    print("🎙️ Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()
    return recording, fs

def save_wav(recording, fs):
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavio.write(tmpfile.name, recording, fs, sampwidth=2)
    return tmpfile.name

def play_audio(file_path):
    system = platform.system()
    if system == "Linux":
        os.system(f"aplay {file_path}")
    elif system == "Darwin":  # macOS
        os.system(f"afplay {file_path}")
    elif system == "Windows":
        import winsound
        winsound.PlaySound(file_path, winsound.SND_FILENAME)
    else:
        print(f"❌ Unsupported OS for playback: {system}")

if __name__ == "__main__":
    while True:
        audio, fs = record_audio(duration=5)
        wav_file = save_wav(audio, fs)

        # Send to API
        with open(wav_file, "rb") as f:
            files = {"audio": f}
            response = requests.post(API_URL, files=files)

        # Clean up the recorded wav file after sending
        os.remove(wav_file)

        if response.status_code == 200:
            # Save bot reply audio
            bot_reply_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            with open(bot_reply_file.name, "wb") as f:
                f.write(response.content)
            print("🤖 Bot reply received, playing audio...")
            play_audio(bot_reply_file.name)

            # Optionally delete bot reply file after playing
            os.remove(bot_reply_file.name)
        else:
            print("❌ API error:", response.text)
