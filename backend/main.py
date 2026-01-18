from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

from services.openai_service import OpenAIService

# Load environment variables
load_dotenv()

app = FastAPI(title="SmartKoach API", version="1.0.0")

# Configure CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI service
try:
    ai_service = OpenAIService()
except ValueError as e:
    print(f"Warning: {e}")
    ai_service = None

class ChatRequest(BaseModel):
    message: str
    domain: str = "DSA"
    difficulty: str = "Medium"

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
async def root():
    return {"message": "SmartKoach API is running", "status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests from frontend.
    
    Args:
        request: ChatRequest containing user message, domain, and difficulty
    
    Returns:
        ChatResponse with AI generated reply
    """
    if not ai_service:
        raise HTTPException(
            status_code=500,
            detail="AI service is not initialized. Please check OPENAI_API_KEY."
        )
    
    try:
        ai_reply = ai_service.generate_interview_response(
            user_message=request.message,
            domain=request.domain,
            difficulty=request.difficulty
        )
        return ChatResponse(reply=ai_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/reset")
async def reset_chat():
    """Reset the conversation history"""
    if ai_service:
        ai_service.reset_conversation()
    return {"message": "Conversation reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
