import os
import json
import google.generativeai as genai
from core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API)

# Database schema description (to include in prompt)
DB_SCHEMA = """
Database Schema with Keys:

users (
  user_id INT PK,
  name VARCHAR,
  age INT,
  mobile_no VARCHAR UNIQUE,
  email VARCHAR UNIQUE,
  region_of_commute VARCHAR,
  created_at DATETIME
)

busstops (
  stop_id INT PK,
  stop_name VARCHAR,
  location VARCHAR,
  region VARCHAR
)

routes (
  route_id INT PK,
  route_name VARCHAR,
  start_stop_id INT FK → busstops.stop_id,
  end_stop_id INT FK → busstops.stop_id,
  distance_km FLOAT
)

buses (
  bus_id INT PK,
  bus_number VARCHAR,
  capacity INT,
  current_location VARCHAR,
  route_id INT FK → routes.route_id,
  status VARCHAR
)

drivers (
  driver_id INT PK,
  name VARCHAR,
  mobile_no VARCHAR UNIQUE,
  bus_id INT FK → buses.bus_id,
  location VARCHAR,
  shift_start TIME,
  shift_end TIME
)

tickets (
  ticket_id INT PK,
  user_id INT FK → users.user_id,
  bus_id INT FK → buses.bus_id,
  route_id INT FK → routes.route_id,
  source_stop_id INT FK → busstops.stop_id,
  destination_stop_id INT FK → busstops.stop_id,
  fare FLOAT,
  purchase_time DATETIME
)

notifications (
  notification_id INT PK,
  user_id INT FK → users.user_id,
  type VARCHAR,
  message TEXT,
  sent_at DATETIME
)

chatlogs (
  chat_id INT PK,
  user_id INT FK → users.user_id,
  message_text TEXT,
  response_text TEXT,
  intent VARCHAR,
  created_at DATETIME,
  correction_applied VARCHAR
)

routestops (
  id INT PK,
  route_id INT FK → routes.route_id,
  stop_id INT FK → busstops.stop_id,
  stop_order INT,
  scheduled_arrival TIME,
  scheduled_departure TIME,
  estimated_arrival DATETIME,
  estimated_departure DATETIME
)


### Example:
Find buses from Chandigarh to Ludhiana:

SELECT b.bus_number, r.route_name, b.current_location, b.status
FROM buses b
JOIN routes r ON b.route_id = r.route_id
JOIN busstops origin ON r.start_stop_id = origin.stop_id
JOIN busstops dest ON r.end_stop_id = dest.stop_id
WHERE origin.location LIKE '%Chandigarh%'
  AND dest.location LIKE '%Ludhiana%';

"""


def process_input(user_text: str, memory_context=None):
    """
    Send user input to Gemini and return structured JSON.
    """
    prompt = f"""
    You are a transport assistant chatbot. 
    User message: "{user_text}"
    User memory context: "{memory_context}"
    
    Use the following database schema to generate queries:
    {DB_SCHEMA}

    Respond in strict JSON format:
    {{
      "intent": "Query | unQuery | other",
      "language": "pa-IN | en-IN | hi-IN",
      "reply": "SQL query OR clarification OR small talk OR Error"
    }}

    Rules:
    - intent mark as Query : when user asks about buses, routes, drivers, tickets.
    - intent mark as unQuery : when user query is missing info (like no source/destination).
    - intent mark as others : for general/small talk/and any other thing.
    - If user asks about buses, routes, drivers, tickets → intent=Query → reply should be SQL query.
    - If missing info (like no source/destination) → intent=unQuery → reply=ask clarification.
    - If general/small talk → intent=others → reply=direct answer.
    - Language should match the user input language.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    text = response.text.strip()
    # ✅ Clean Markdown fences if present
    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()
    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    
    print("Gemini response:", text)
    
    try:
        return json.loads(text)  # safer than eval
    except Exception as e:
        return {"intent": "error", "language": "en-IN", "reply": f"Error: {str(e)}"}


def format_reply(user_text: str, db_result, language="pa-IN"):
    """
    Format final reply using Gemini, given DB result + original query.
    """
    prompt = f"""
    The user asked: "{user_text}"
    Database result: {db_result}
    Language: {language}

    Generate a natural reply in the user's language. 
    Example: "The next bus from Sector 10 to Civil Lines is Bus 21, arriving in 8 minutes."
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()
