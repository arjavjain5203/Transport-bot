from services.gemini_service import process_input, format_reply
from services.db_service import run_query
from services.memory_service import add_to_memory, get_memory

def handle_message(user_id: str, message: str, channel: str):
    # Step 1: Get user’s memory for context
    memory_context = get_memory(user_id)

    # Step 2: Send to Gemini
    gemini_resp = process_input(message, memory_context)

    intent = gemini_resp.get("intent")
    language = gemini_resp.get("language", "pa-IN")
    reply = gemini_resp.get("reply")

    # Step 3: Handle based on intent
    if intent == "Query":
        db_result = run_query(reply)
        final_reply = format_reply(message, db_result, language)
    else:
        final_reply = reply

    # Step 4: Save exchange in memory
    add_to_memory(user_id, message, final_reply)

    return final_reply
