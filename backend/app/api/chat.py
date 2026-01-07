from fastapi import APIRouter, HTTPException
from app.models.session import ChatRequest, ChatResponse, Message, SessionStatus
from app.services import storage
from app.graphs.conversation_graph import conversation_workflow
from app.graphs.states import ConversationState
from datetime import datetime

router = APIRouter()

@router.post("/sessions/{session_id}/message", response_model=ChatResponse)
async def send_message(session_id: str, request: ChatRequest):
    """Send a message and get AI response"""
    
    # Get session
    session = await storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Add user message
    user_message = Message(
        role="user",
        content=request.message,
        timestamp=datetime.utcnow()
    )
    session.messages.append(user_message)
    
    # Convert to graph state
    state: ConversationState = {
        "messages": [{"role": m.role, "content": m.content} for m in session.messages],
        "product_description": session.product_description,
        "domain": session.domain,
        "key_actions": session.key_actions,
        "user_segments": session.user_segments,
        "business_goals": session.business_goals,
        "current_step": "greeting" if len(session.messages) == 1 else session.messages[-2].content,
        "ready_for_labeling": False
    }
    
    # Run through graph
    result = conversation_workflow.invoke(state)
    
    # Extract assistant response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant" and m not in state["messages"]]
    if assistant_messages:
        assistant_message = Message(
            role="assistant",
            content=assistant_messages[-1]["content"],
            timestamp=datetime.utcnow()
        )
        session.messages.append(assistant_message)
    
    # Update session with extracted info
    session.product_description = result.get("product_description")
    session.domain = result.get("domain")
    session.key_actions = result.get("key_actions", [])
    session.user_segments = result.get("user_segments", [])
    session.business_goals = result.get("business_goals", [])
    
    # Update status
    if result.get("ready_for_labeling"):
        session.status = SessionStatus.READY_FOR_LABELING
    
    # Save session
    await storage.update_session(session)
    
    return ChatResponse(
        response=assistant_messages[-1]["content"] if assistant_messages else "I'm processing your response...",
        status=session.status,
        ready_for_labeling=result.get("ready_for_labeling", False)
    )
