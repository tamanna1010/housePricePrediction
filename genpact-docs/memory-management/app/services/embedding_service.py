# from sentence_transformers import SentenceTransformer

# class EmbeddingService:
#     def __init__(self):
#         self.model = SentenceTransformer("all-MiniLM-L6-v2")

#     def generate_embedding(self, text: str):
#         return self.model.encode(text).tolist()
    
    
from langchain_openai import AzureOpenAIEmbeddings
from app.config import settings


class EmbeddingService:

    def __init__(self):

        self.embedding_model = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_OPENAI_API_BASE,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_deployment="text-embedding-ada-002"
        )

    def get_embedding(self, text):

        return self.embedding_model.embed_query(text)
