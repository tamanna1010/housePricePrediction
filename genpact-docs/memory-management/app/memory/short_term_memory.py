import redis 
import json 
from app.config import settings

class ShortTermMemory:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

        self.memory_ttl = 3600

    def add_message(self, session_id: str, role: str, content: str):

        key = f"chat:{session_id}"

        existing = self.redis_client.get(key)

        if existing:
            messages = json.loads(existing)
        else:
            messages = []

        messages.append({
            "role": role,
            "content": content
        })

        messages = messages[-10:]

        self.redis_client.setex(
            key,
            self.memory_ttl,
            json.dumps(messages)
        )

    def get_messages(self, session_id: str):

        key = f"chat:{session_id}"

        data = self.redis_client.get(key)

        if not data:
            return []

        return json.loads(data)

    def clear_memory(self, session_id: str):
        key = f"chat:{session_id}"
        self.redis_client.delete(key)