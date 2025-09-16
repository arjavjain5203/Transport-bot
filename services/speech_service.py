import os
import tempfile
from google.cloud import speech, texttospeech
from core.config import settings
# Load Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# 🎙️ Speech-to-Text
def speech_to_text(audio_file: str, language="pa-IN") -> str:
    client = speech.SpeechClient()

    with open(audio_file, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language,
        alternative_language_codes=["hi-IN", "en-IN"]  # fallback Hindi + English
    )

    response = client.recognize(config=config, audio=audio)

    if not response.results:
        return "Sorry, I could not understand."

    return response.results[0].alternatives[0].transcript


# 🔊 Text-to-Speech
def text_to_speech(text: str, language="pa-IN") -> str:
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save to temporary WAV file
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(tmpfile.name, "wb") as out:
        out.write(response.audio_content)

    return tmpfile.name
