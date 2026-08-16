1 Short-Term Memory Use Cases

Use short-term memory when:

Use Case	Why Short-Term Memory
Customer support chat	Need recent conversation context
AI copilot	Need active session memory
Temporary workflow execution	Memory only needed during execution
API-based agent calls	Session-specific context
ReAct agents	Keep reasoning trace temporarily

Characteristics:

Fast retrieval
Temporary storage
Session-based
Low latency
Automatically expires

Recommended Technology:

Redis
In-memory cache
Session store


2 Long-Term Memory Use Cases

Use long-term memory when:

Use Case	Why Long-Term Memory
Personalized assistant	Remember user preferences
Enterprise RAG systems	Persistent document knowledge
Research agents	Store historical findings
Multi-session copilots	Cross-session continuity
Learning agents	Retain learned patterns

Characteristics:

Persistent storage
Semantic retrieval
Historical knowledge
Cross-session access

Recommended Technology:

Vector databases
PostgreSQL
Pinecone
Weaviate
ChromaDB