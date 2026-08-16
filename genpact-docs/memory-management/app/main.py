from fastapi import FastAPI 
from app.routes.chat_routes import router

app = FastAPI( title="Production Memory Management System" )

app.include_router(router)

@app.get("/") 
def health_check(): 
    return { "status": "healthy" }