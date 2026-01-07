from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import add_messages

class Message(TypedDict):
    role: str  # "user" or "assistant"
    content: str

class ConversationState(TypedDict):
    """State that flows through the LangGraph conversation"""
    session_id: str
    user_id: str
    project_name: Optional[str]
    
    # Conversation flow
    messages: Annotated[List[Message], add_messages]  # LangGraph will append messages
    current_stage: str  # "greeting", "product_discovery", "goal_understanding", "labeling_ready"
    
    # Extracted information
    product_type: Optional[str]  # "ecommerce", "saas", "marketplace", etc.
    product_description: Optional[str]
    user_goals: List[str]  # ["conversion_rate", "engagement", etc.]
    user_types: Optional[List[str]]  # ["buyer", "seller"] or None
    
    # Flow control
    next_action: Optional[str]  # Signal to frontend: "start_labeling", etc.
