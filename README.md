# 🤖 Transport Bot API

This project is a powerful, multi-channel conversational API built to handle dynamic user interactions across **SMS**, **WhatsApp**, and simulated **Voice Calls**. It leverages the power of Gemini AI for intelligent conversation and integrates popular communication platforms like Twilio.

## 🚀 Features

* **Multi-Channel Support:** Dedicated endpoints for handling SMS, WhatsApp, and Voice Call interactions.
* **Intelligent Conversational AI:** Powered by **Gemini AI** for generating contextual and relevant responses.
* **Contextual Memory:** Maintains conversation history and context for seamless multi-turn dialogue.
* **Speech Integration:** Uses **Google Speech-to-Text** and **Text-to-Speech** services for realistic call simulation.
* **Multilingual Capability:** Designed to support conversations in multiple languages, including English, **Punjabi** (`pa-IN`), and **Hindi**.
* **Robust Backend:** Built on a fast and modern **FastAPI** framework.

## ⚙️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3.9+** & **FastAPI** | High-performance API foundation |
| **Conversational AI** | **Gemini AI** | Core intelligence for responses |
| **Messaging/Calls** | **Twilio** | SMS and WhatsApp integration |
| **Voice Processing** | **Google Speech/TTS** | Call simulation and audio handling |
| **Database (Config)** | **MySQL (Aiven)** | Configuration suggests external database capability |

## 📂 Project Structure
```bash
transport-bot/
├── main.py # FastAPI entry point & API routing
├── testing.py # Utility for call simulation setup
├── services/
│ ├── gemini_service.py # Wrapper for Gemini API calls
│ ├── message_service.py # Logic for handling message flow and intent
│ ├── memory_service.py # Manages user conversation history (e.g., memory.json)
│ └── speech_service.py # Handles Speech-to-Text & Text-to-Speech
├── data/
│ └── memory.json # Stores persistent conversation history
├── requirements.txt # Python dependencies
└── .env # Environment variables
bash
```

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash 
git clone [https://github.com/arjavjain5203/Transport-bot.git](https://github.com/arjavjain5203/Transport-bot.git)
cd Transport-bot
2. Install Dependencies
pip install -r requirements.txt
3. Environment Variables
Create a file named .env in the root directory and populate it with your credentials:

# Gemini API Key
GEMINI_API=your-gemini-api-key

# Twilio Credentials (if using SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token

# MySQL (Aiven) / Database configuration
DB_HOST=your-db-host
DB_PORT=your-db-port
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
4. Run Locally
Start the FastAPI server:


uvicorn main:app --reload --port 8000
The API will be live at: http://127.0.0.1:8000
```

# 📞 API Endpoints
```bash
#Endpoint	Method	Function
/chat	POST	General text-based chatbot interaction.
/sms	POST	Handles incoming SMS messages via Twilio webhook.
/whatsapp	POST	Handles incoming WhatsApp messages via Twilio webhook.
/call	POST	Simulates a phone call: takes a .wav file, processes via AI, and returns an audio response.

```

## 👨‍💻 Author 
Arjav Jain
