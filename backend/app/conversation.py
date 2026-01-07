from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

from app.state import ConversationState, Message

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

# Node functions (each is a step in conversation)

def greeting_node(state: ConversationState) -> ConversationState:
    """Initial greeting - ask about product type"""
    if len(state["messages"]) == 0:
        # First interaction
        response = "Hi! I'm here to help you set up analytics. What type of product or app are you building?"
        state["messages"].append(Message(role="assistant", content=response))
        state["current_stage"] = "product_discovery"
    return state

def product_discovery_node(state: ConversationState) -> ConversationState:
    """Classify product type and ask follow-up questions"""
    last_user_message = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), "")
    
    # Use LLM to classify product type
    system_prompt = """You are helping set up web analytics. 
    Classify the user's product into one of: ecommerce, saas, marketplace, content, other.
    Extract key information and ask relevant follow-up questions.
    
    Be conversational and helpful. Keep responses under 3 sentences."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User said: {last_user_message}\n\nClassify their product type and ask a relevant follow-up question.")
    ]
    
    ai_response = llm.invoke(messages)
    
    # Parse product type (simplified - in production use structured output)
    content = ai_response.content.lower()
    if "ecommerce" in content or "selling" in content:
        state["product_type"] = "ecommerce"
    elif "saas" in content or "software" in content:
        state["product_type"] = "saas"
    elif "marketplace" in content:
        state["product_type"] = "marketplace"
    elif "content" in content or "blog" in content:
        state["product_type"] = "content"
    else:
        state["product_type"] = "other"
    
    state["product_description"] = last_user_message
    state["messages"].append(Message(role="assistant", content=ai_response.content))
    state["current_stage"] = "goal_understanding"
    
    return state

def goal_understanding_node(state: ConversationState) -> ConversationState:
    """Ask about analytics goals"""
    last_user_message = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), "")
    
    # Extract goals mentioned
    goals = []
    goal_keywords = {
        "conversion": "conversion_rate",
        "purchase": "conversion_rate",
        "signup": "signups",
        "engagement": "engagement",
        "retention": "retention",
        "funnel": "funnel_analysis",
    }
    
    for keyword, goal in goal_keywords.items():
        if keyword in last_user_message.lower():
            goals.append(goal)
    
    state["user_goals"] = goals if goals else ["general_tracking"]
    
    # Generate response asking about key actions
    system_prompt = f"""You're helping set up analytics for a {state['product_type']} product.
    The user mentioned: {last_user_message}
    
    Ask them what specific user actions they want to track (e.g., button clicks, purchases, signups).
    Keep it conversational and under 2 sentences."""
    
    ai_response = llm.invoke([SystemMessage(content=system_prompt)])
    state["messages"].append(Message(role="assistant", content=ai_response.content))
    state["current_stage"] = "labeling_ready"
    
    return state

def labeling_ready_node(state: ConversationState) -> ConversationState:
    """User has provided enough context, ready to start labeling"""
    response = "Perfect! Now let's identify the key elements on your site. Click 'Start Labeling' in the extension to mark the buttons and elements you want to track."
    
    state["messages"].append(Message(role="assistant", content=response))
    state["next_action"] = "start_labeling"
    state["current_stage"] = "complete"
    
    return state

# Routing logic
def route_conversation(state: ConversationState) -> str:
    """Decide which node to go to next based on current stage"""
    stage = state["current_stage"]
    
    if stage == "greeting":
        return "product_discovery"
    elif stage == "product_discovery":
        return "goal_understanding"
    elif stage == "goal_understanding":
        return "labeling_ready"
    elif stage == "labeling_ready":
        return "complete"
    else:
        return END

# Build the graph
def create_conversation_graph() -> StateGraph:
    """Create the LangGraph state machine for conversation flow"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("product_discovery", product_discovery_node)
    workflow.add_node("goal_understanding", goal_understanding_node)
    workflow.add_node("labeling_ready", labeling_ready_node)
    workflow.add_node("complete", lambda state: state)
    
    # Set entry point
    workflow.set_entry_point("greeting")
    
    # Add conditional edges based on stage
    workflow.add_conditional_edges(
        "greeting",
        route_conversation,
        {
            "product_discovery": "product_discovery",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "product_discovery",
        route_conversation,
        {
            "goal_understanding": "goal_understanding",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "goal_understanding",
        route_conversation,
        {
            "labeling_ready": "labeling_ready",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "labeling_ready",
        route_conversation,
        {
            "complete": "complete",
            END: END
        }
    )
    
    workflow.add_edge("complete", END)
    
    return workflow.compile()

# In-memory state storage (replace with Supabase later)
_state_store = {}

async def run_conversation(session_id: str, user_message: str) -> dict:
    """Run one turn of conversation"""
    # Load or create state
    if session_id not in _state_store:
        _state_store[session_id] = ConversationState(
            session_id=session_id,
            user_id="temp",
            project_name=None,
            messages=[],
            current_stage="greeting",
            product_type=None,
            product_description=None,
            user_goals=[],
            user_types=None,
            next_action=None,
        )
    
    state = _state_store[session_id]
    
    # Add user message
    state["messages"].append(Message(role="user", content=user_message))
    
    # Run graph
    graph = create_conversation_graph()
    result = graph.invoke(state)
    
    # Save state
    _state_store[session_id] = result
    
    # Return last assistant message
    last_assistant_msg = next((m["content"] for m in reversed(result["messages"]) if m["role"] == "assistant"), "")
    
    return {
        "reply": last_assistant_msg,
        "next_action": result.get("next_action")
    }
