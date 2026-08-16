from pydantic import BaseModel

class ChatRequest(BaseModel): 
    session_id: str
    user_id: str
    message: str

class ChatResponse(BaseModel): 
    response: str
    short_term_context_used: bool
    long_term_context_used: bool