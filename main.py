from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
import os
from services.speech_service import speech_to_text, text_to_speech
from services.message_service import handle_message

app = FastAPI(title="Unified Transport Chatbot API")

@app.get("/")
async def root():
    return {"message": "Transport Bot is running"}


@app.post("/sms")
async def sms_handler(user_id: str, message: str):
    reply = handle_message(user_id, message, channel="sms")
    return {"reply": reply}

@app.post("/whatsapp")
async def whatsapp_handler(user_id: str, message: str):
    reply = handle_message(user_id, message, channel="whatsapp")
    return {"reply": reply}

@app.post("/call")
async def call_handler(audio: UploadFile = File(...)):
    """
    Simulates a call: user uploads audio → we transcribe, process, reply, return audio reply.
    """
    # Save uploaded audio
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(tmpfile.name, "wb") as f:
        f.write(await audio.read())

    # Step 1: Speech → Text
    user_text = speech_to_text(tmpfile.name, language="pa-IN")  # panjabi default
    print(f"👤 User said: {user_text}")

    # Step 2: Process via Gemini + DB
    reply = handle_message("call_user", user_text, channel="call")
    print(f"🤖 Bot reply: {reply}")

    # Step 3: Text → Speech
    reply_wav = text_to_speech(reply, language="pa-IN")

    # Step 4: Return audio file as response
    return FileResponse(reply_wav, media_type="audio/wav", filename="reply.wav")
