import chromadb 
from app.config import settings 
from app.services.embedding_service import EmbeddingService

class LongTermMemory:
    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name="agent_memory"
        )

    def store_memory(self, memory_id: str, text: str, metadata: dict):

        embedding = self.embedding_service.get_embedding(text)

        self.collection.add(
            ids=[memory_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )


    def retrieve_memory(self, query: str, top_k: int = 3):

        query_embedding = self.embedding_service.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results