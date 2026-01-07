from typing import TypedDict, List, Optional
from app.models.session import Domain

class ConversationState(TypedDict):
    """State for the conversation graph"""
    messages: List[dict]  # [{"role": "user/assistant", "content": "..."}]
    
    # Extracted information
    product_description: Optional[str]
    domain: Optional[Domain]
    key_actions: List[str]
    user_segments: List[str]
    business_goals: List[str]
    
    # Control flow
    current_step: str  # greeting, classify_domain, ask_actions, ask_segments, ask_goals, complete
    ready_for_labeling: bool
