from fastapi import APIRouter

from app.models.schemas import ( ChatRequest, ChatResponse )

from app.memory.memory_orchestrator import MemoryOrchestrator

router = APIRouter()

memory_orchestrator = MemoryOrchestrator()

@router.post("/chat", response_model=ChatResponse) 
def chat(request: ChatRequest):
    result = memory_orchestrator.process_query(
        session_id=request.session_id,
        user_id=request.user_id,
        user_query=request.message
    )

    return result