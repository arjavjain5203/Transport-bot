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

route_stops (
  id INT PK,
  route_id INT FK → driver_routes.id,
  stop_id INT FK → busstops.stop_id,
  stop_order INT,
  arrival_time TIME,
  created_at TIMESTAMP
)

driver_routes (
  id INT PK,
  route_number VARCHAR UNIQUE,
  route_name VARCHAR,
  source_stop VARCHAR,
  destination_stop VARCHAR,
  total_stops INT,
  estimated_duration INT,
  is_active TINYINT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

driver_route_stops (
  id INT PK,
  route_id INT FK → driver_routes.id,
  stop_name VARCHAR,
  stop_order INT,
  latitude DECIMAL,
  longitude DECIMAL,
  estimated_arrival_time TIME,
  created_at TIMESTAMP
)

driver_auth (
  id INT PK,
  license_number VARCHAR UNIQUE,
  password_hash VARCHAR,
  name VARCHAR,
  phone VARCHAR,
  email VARCHAR,
  is_active TINYINT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

driver_sessions (
  id INT PK,
  driver_id INT FK → drivers.driver_id,
  route_id INT FK → driver_routes.id,
  bus_number VARCHAR,
  status ENUM('offline','online','active'),
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

latest_driver_locations (
  session_id INT,
  driver_id INT,
  route_id INT,
  bus_number VARCHAR,
  session_status ENUM('offline','online','active'),
  driver_name VARCHAR,
  route_name VARCHAR,
  latitude DECIMAL,
  longitude DECIMAL,
  speed FLOAT,
  last_update TIMESTAMP,
  seconds_since_update BIGINT
)

location_updates (
  id INT PK,
  session_id INT,
  latitude DECIMAL,
  longitude DECIMAL,
  accuracy FLOAT,
  speed FLOAT,
  bearing FLOAT,
  timestamp TIMESTAMP,
  location_source ENUM('gps','network','gsm'),
  device_type ENUM('mobile_app','esp32_hardware','simulator'),
  device_id VARCHAR,
  hardware_info JSON
)

bus_realtime_status (
  id INT PK,
  bus_id INT FK → buses.bus_id,
  current_latitude DECIMAL,
  current_longitude DECIMAL,
  speed DECIMAL,
  fuel_level INT,
  passenger_count INT,
  next_stop_id INT FK → busstops.stop_id,
  eta_next_stop TIME,
  last_updated TIMESTAMP,
  driver_id INT FK → drivers.driver_id,
  is_delayed TINYINT,
  delay_minutes INT
)

stop_arrivals (
  id INT PK,
  session_id INT,
  stop_id INT FK → busstops.stop_id,
  arrival_time TIMESTAMP
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
      "language": "en-IN"(only),
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
    Most Important Note : write the Query in english and the name of source and destination should in english in the SQL query
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


def format_reply(user_text: str, db_result, language="en-IN"):
    """
    Format final reply using Gemini, given DB result + original query.
    """
    prompt = f"""
    The user asked: "{user_text}"
    Database result: {db_result}
    Language: {language}

    Generate a natural reply in the user's language. 
    Example: "The next bus from Sector 10 to Civil Lines is Bus 21, arriving in 8 minutes."
    Note : only give the best responce which is according to you 
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()
