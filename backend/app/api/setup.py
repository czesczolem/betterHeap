from fastapi import APIRouter, HTTPException
from app.models.session import CreateSessionRequest, SetupSession
from app.services import storage

router = APIRouter()

@router.post("/sessions", response_model=SetupSession)
async def create_setup_session(request: CreateSessionRequest):
    """Create a new setup session"""
    session = await storage.create_session(request.project_id)
    return session

@router.get("/sessions/{session_id}", response_model=SetupSession)
async def get_setup_session(session_id: str):
    """Get session by ID"""
    session = await storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
