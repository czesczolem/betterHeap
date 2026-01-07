from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from app.conversation import create_conversation_graph, run_conversation

load_dotenv()

app = FastAPI(title="BetterHeap Conversation API")

# CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class CreateSessionRequest(BaseModel):
    user_id: str
    project_name: Optional[str] = None

class CreateSessionResponse(BaseModel):
    session_id: str
    first_message: str

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

class ChatMessageResponse(BaseModel):
    reply: str
    next_action: Optional[str] = None  # "start_labeling", "review_taxonomy", etc.

# Endpoints
@app.post("/api/v1/sessions/create", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Initialize a new setup session"""
    # Generate session ID
    import uuid
    session_id = f"ssn_{uuid.uuid4().hex[:8]}"
    
    # Initialize conversation graph state
    from app.state import ConversationState
    initial_state = ConversationState(
        session_id=session_id,
        user_id=request.user_id,
        project_name=request.project_name,
        messages=[],
        current_stage="greeting",
        product_type=None,
        user_goals=[],
    )
    
    # Save to DB (TODO: implement)
    # For now, store in memory or skip
    
    first_message = "Hi! I'm here to help you set up analytics. What type of product or app are you building?"
    
    return CreateSessionResponse(
        session_id=session_id,
        first_message=first_message
    )

@app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest):
    """Process a chat message and return AI response"""
    try:
        # Load state from DB (TODO: implement)
        # For now, create fresh or use session storage
        
        # Run conversation graph
        result = await run_conversation(request.session_id, request.message)
        
        return ChatMessageResponse(
            reply=result["reply"],
            next_action=result.get("next_action")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
