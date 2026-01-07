from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    READY_FOR_LABELING = "ready_for_labeling"
    COMPLETE = "complete"

class Domain(str, Enum):
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    CONTENT = "content"
    OTHER = "other"

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class SetupSession(BaseModel):
    id: str
    project_id: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    
    # Extracted information
    product_description: Optional[str] = None
    domain: Optional[Domain] = None
    key_actions: List[str] = []
    user_segments: List[str] = []
    business_goals: List[str] = []
    
    # Conversation
    messages: List[Message] = []
    
    created_at: datetime
    updated_at: datetime

class CreateSessionRequest(BaseModel):
    project_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: SessionStatus
    ready_for_labeling: bool = False
