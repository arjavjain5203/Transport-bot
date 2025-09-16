from collections import defaultdict, deque

# In-memory dict: user_id → deque of last N messages
conversation_memory = defaultdict(lambda: deque(maxlen=5))

def add_to_memory(user_id: str, user_msg: str, bot_reply: str):
    conversation_memory[user_id].append({"user": user_msg, "bot": bot_reply})

def get_memory(user_id: str):
    """
    Returns formatted memory for Gemini prompt.
    """
    history = conversation_memory[user_id]
    memory_text = "\n".join(
        [f"User: {h['user']}\nBot: {h['bot']}" for h in history]
    )
    return memory_text
