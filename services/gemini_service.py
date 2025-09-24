import os
import json
import google.generativeai as genai
from core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API)

# Database schema description (to include in prompt)
DB_SCHEMA = """
Database Schema with Keys:

buses (
  bus_id INT PK,
  bus_number VARCHAR(50),
  capacity INT,
  status ENUM('available','running','maintenance','alternate'),
  current_driver_id INT FK → drivers.driver_id
)

driver_sessions (
  session_id INT PK,
  driver_id INT FK → drivers.driver_id,
  bus_id INT FK → buses.bus_id,
  route_id INT FK → routes.route_id,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  performance_rating DECIMAL(3,2)
)

drivers (
  driver_id INT PK,
  name VARCHAR(100),
  mobile VARCHAR(15),
  license_no VARCHAR(50),
  assigned_bus_id INT FK → buses.bus_id,
  created_at TIMESTAMP
)

eta_predictions (
  eta_id INT PK,
  bus_id INT FK → buses.bus_id,
  stop_id INT FK → stops.stop_id,
  predicted_arrival TIMESTAMP,
  minutes_remaining INT,
  last_updated TIMESTAMP
)

location_updates (
  location_id INT PK,
  bus_id INT FK → buses.bus_id,
  latitude DECIMAL(10,6),
  longitude DECIMAL(10,6),
  timestamp TIMESTAMP
)

reports (
  report_id INT PK,
  user_id INT FK → users.user_id,
  bus_id INT FK → buses.bus_id,
  report_type ENUM('accident','delay','other'),
  location_lat DECIMAL(10,6),
  location_lon DECIMAL(10,6),
  description TEXT,
  media_url VARCHAR(255),
  created_at TIMESTAMP
)

route_progress (
  progress_id INT PK,
  session_id INT FK → driver_sessions.session_id,
  stop_id INT FK → stops.stop_id,
  arrival_time TIMESTAMP,
  departure_time TIMESTAMP
)

routes (
  route_id INT PK,
  source_name VARCHAR(100),
  source_lat DECIMAL(10,6),
  source_lon DECIMAL(10,6),
  destination_name VARCHAR(100),
  destination_lat DECIMAL(10,6),
  destination_lon DECIMAL(10,6),
  total_distance_km DECIMAL(8,2)
)

stops (
  stop_id INT PK,
  route_id INT FK → routes.route_id,
  stop_name VARCHAR(100),
  stop_lat DECIMAL(10,6),
  stop_lon DECIMAL(10,6),
  sequence_no INT
)

users (
  user_id INT PK,
  name VARCHAR(100),
  password_hash VARCHAR(255),
  age INT,
  email VARCHAR(150),
  mobile VARCHAR(15),
  region VARCHAR(100),
  created_at TIMESTAMP
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
SELECT b.bus_number, r.source_name, r.destination_name, b.status
FROM buses b
JOIN routes r ON b.bus_id = (
    SELECT bus_id FROM driver_sessions 
    WHERE route_id = r.route_id 
    AND end_time IS NULL 
    LIMIT 1
)
WHERE r.source_name LIKE '%Chandigarh%'
  AND r.destination_name LIKE '%Ludhiana%';

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
