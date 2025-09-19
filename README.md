# Transport Bot API

This project is a multi-channel conversational API that handles **SMS**,
**WhatsApp**, and **Call** interactions using Gemini AI, Twilio, and
Google Speech/Text-to-Speech.

## 🚀 Features

-   `/sms` → Handle SMS messages via Twilio
-   `/whatsapp` → Handle WhatsApp chatbot responses via Twilio
-   `/call` → Simulate phone call interaction (speech-to-text + AI +
    text-to-speech)
-   **Memory Support** → Keeps context of user conversations
-   Supports multiple languages (English, Punjabi, Hindi, etc.)

## 📂 Project Structure

    transport-bot/
    │── main.py              # FastAPI entry point
    │── temp_call.py         # Call simulation API
    │── services/
    │   ├── speech_service.py   # Speech-to-Text & Text-to-Speech
    │   ├── message_service.py  # Message handler (memory + intent handling)
    │   ├── gemini_service.py   # Gemini API wrapper
    │   ├── memory_service.py   # User memory storage
    │── data/
    │   ├── memory.json         # Stores conversation history
    │── .env                 # Environment variables
    │── requirements.txt     # Dependencies
    │── README.md            # Documentation

## ⚙️ Requirements

-   Python 3.9+
-   Install dependencies:

``` bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the root with:

    # Gemini API
    GEMINI_API=your-gemini-api-key

    # MySQL (Aiven)
    DB_HOST=your-db-host
    DB_PORT=your-db-port
    DB_USER=your-db-user
    DB_PASSWORD=your-db-password
    DB_NAME=your-db-name

## ▶️ Run Locally

``` bash
uvicorn main:app --reload --port 8000
```

API will be live at:\
👉 http://127.0.0.1:8000



## 📞 API Endpoints

-   `POST /sms` → Handle SMS messages\
-   `POST /whatsapp` → Handle WhatsApp chatbot responses\
-   `POST /call` → Upload `.wav` file, get AI response in audio
-   `POST /chat` → for the chatbot 

## 🛠 Debugging Punjabi Speech

If Punjabi (`pa-IN`) audio is not recognized: - Ensure audio is **16kHz
PCM WAV** - Use `ffmpeg` conversion before STT

``` bash
ffmpeg -y -i input.wav -ac 1 -ar 16000 -f wav output_16k.wav
```

## 👨‍💻 Author

Built by **Arjav Jain** 
