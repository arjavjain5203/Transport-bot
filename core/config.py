from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Settings:
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GEMINI_API = os.getenv("GEMINI_API")
    AUDIO_API=os.getenv("AUDIO_API")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 3306))  # default 3306 if not given
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

settings = Settings()
