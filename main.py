from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
import os
from fastapi import Form
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from twilio.twiml.messaging_response import MessagingResponse

from services.speech_service import speech_to_text, text_to_speech
from services.message_service import handle_message

class ChatRequest(BaseModel):
    user_id: int
    message: str
app = FastAPI(title="Unified Transport Chatbot API")

@app.get("/")
async def root():
    return {"message": "Transport Bot is running"}



@app.post("/chat")
async def chat_webhook(request: ChatRequest):
    # Pass user_id first, then message, default channel to e.g. "web"
    print(request.message)
    result = handle_message(request.user_id, request.message, channel="web")

    response = {
        "user_message": request.message,
        "bot_response": None,
        "results": []
    }

    if isinstance(result, dict):
        response["bot_response"] = result.get("bot_response") or result.get("response")
        response["results"] = result.get("results", [])
    else:
        response["bot_response"] = str(result)

    return JSONResponse(content=response)


@app.post("/sms")
async def sms_handler(user_id: str, message: str):
    reply = handle_message(user_id, message, channel="sms")
    return {"reply": reply}


@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Handle incoming WhatsApp messages via the Twilio webhook.
    `Body` is the content of the message, and `From` is the sender's phone number.
    """
    # Handle the incoming message based on the 'From' (user) and 'Body' (message)
    response_text = handle_message(From, Body, channel="whatsapp")

    # Beautify the message for the user (Optional formatting)
    beautified_response = (
        f"🚌 *Punjab Bus Assistant*\n\n"
        f"{response_text}\n\n"
        f"🚏 Reply anytime for more help!"
    )

    # Return the response as a message in a TwiML format
    twilio_response = MessagingResponse()
    twilio_response.message(beautified_response)
    

    return PlainTextResponse(content=str(twilio_response), media_type="text/xml")
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
