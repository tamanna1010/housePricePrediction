from app.services.llm_service import LLMService

class MemorySummarizer:
    def __init__(self):
        self.llm_service = LLMService()

    def summarize_conversation(self, messages):

        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])

        prompt = f"""
        Summarize the following conversation.
        Keep important user preferences and key details.

        Conversation:
        {conversation}
        """

        return self.llm_service.generate_response(prompt)