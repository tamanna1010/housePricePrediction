import uuid

from app.memory.short_term_memory import ShortTermMemory 
from app.memory.long_term_memory import LongTermMemory 
from app.memory.summarizer import MemorySummarizer 
from app.services.llm_service import LLMService

class MemoryOrchestrator:
    def __init__(self):

        self.short_memory = ShortTermMemory()
        self.long_memory = LongTermMemory()
        self.summarizer = MemorySummarizer()
        self.llm_service = LLMService()

    def process_query(
        self,
        session_id: str,
        user_id: str,
        user_query: str
    ):

        short_term_messages = self.short_memory.get_messages(session_id)

        retrieved_memories = self.long_memory.retrieve_memory(user_query)

        memory_context = ""

        if retrieved_memories and retrieved_memories.get("documents"):
            docs = retrieved_memories["documents"][0]
            memory_context = "\n".join(docs)

        short_context = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in short_term_messages
        ])

        final_prompt = f"""
        You are an intelligent AI assistant.

        Relevant Long-Term Memory:
        {memory_context}

        Recent Conversation:
        {short_context}

        User Query:
        {user_query}
        """

        response = self.llm_service.generate_response(final_prompt)

        self.short_memory.add_message(
            session_id,
            "user",
            user_query
        )

        self.short_memory.add_message(
            session_id,
            "assistant",
            response
        )

        if len(short_term_messages) > 8:

            summary = self.summarizer.summarize_conversation(
                short_term_messages
            )

            self.long_memory.store_memory(
                memory_id=str(uuid.uuid4()),
                text=summary,
                metadata={
                    "user_id": user_id,
                    "type": "conversation_summary"
                }
            )

        return {
            "response": response,
            "short_term_context_used": bool(short_context),
            "long_term_context_used": bool(memory_context)
        }