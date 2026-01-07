from supabase import create_client, Client
from app.models.session import SetupSession, SessionStatus
from datetime import datetime
from typing import Optional
import os
import uuid

# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

async def create_session(project_id: Optional[str] = None) -> SetupSession:
    """Create a new setup session"""
    session = SetupSession(
        id=f"ssn_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        status=SessionStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Store in Supabase
    supabase.table("setup_sessions").insert(session.dict()).execute()
    
    return session

async def get_session(session_id: str) -> Optional[SetupSession]:
    """Get session by ID"""
    result = supabase.table("setup_sessions").select("*").eq("id", session_id).execute()
    
    if result.data:
        return SetupSession(**result.data[0])
    return None

async def update_session(session: SetupSession) -> SetupSession:
    """Update session"""
    session.updated_at = datetime.utcnow()
    
    supabase.table("setup_sessions").update(session.dict()).eq("id", session.id).execute()
    
    return session
