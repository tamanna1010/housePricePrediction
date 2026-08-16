from langchain_openai import AzureChatOpenAI

from app.config import settings

class LLMService:

    def __init__(self):

        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_API_BASE,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0.3
        )

    def generate_response(self, prompt: str):

        response = self.llm.invoke(prompt)

        return response.content
    
# llm = LLMService()

# response = llm.generate_response(
#     "Tell me about Agentic AI"
# )

# print(response)
    
