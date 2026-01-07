from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from app.graphs.states import ConversationState
from app.models.session import Domain

# LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)

# Output parsers
class DomainClassification(BaseModel):
    domain: Domain = Field(description="Classified domain")
    reasoning: str = Field(description="Brief reasoning")

class ExtractedActions(BaseModel):
    actions: List[str] = Field(description="List of key actions mentioned")

class ExtractedSegments(BaseModel):
    segments: List[str] = Field(description="List of user segments/types")

class ExtractedGoals(BaseModel):
    goals: List[str] = Field(description="List of business goals/metrics")

# Node functions
def greeting_node(state: ConversationState) -> ConversationState:
    """Initial greeting"""
    message = {
        "role": "assistant",
        "content": "Hi! I'm here to help you set up analytics for your site. What type of product or app are you building?"
    }
    state["messages"].append(message)
    state["current_step"] = "classify_domain"
    return state

def classify_domain_node(state: ConversationState) -> ConversationState:
    """Classify the product domain"""
    last_user_message = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), "")
    
    parser = PydanticOutputParser(pydantic_object=DomainClassification)
    prompt = ChatPromptTemplate.from_template(
        """Classify this product into a domain:
        
Product description: {description}

Domains:
- ecommerce: Online stores, marketplaces, retail
- saas: B2B/B2C software products, platforms
- content: Media, publishing, social networks
- other: Everything else

{format_instructions}"""
    )
    
    chain = prompt | llm | parser
    result = chain.invoke({
        "description": last_user_message,
        "format_instructions": parser.get_format_instructions()
    })
    
    state["product_description"] = last_user_message
    state["domain"] = result.domain
    state["current_step"] = "ask_actions"
    
    return state

def ask_actions_node(state: ConversationState) -> ConversationState:
    """Ask about key actions based on domain"""
    domain = state.get("domain", Domain.OTHER)
    
    prompts = {
        Domain.ECOMMERCE: "Great! What user actions are most important to track? For example: product views, add to cart, checkout, purchases, etc.",
        Domain.SAAS: "Perfect! What features or actions do you want to track? For example: sign-ups, feature usage, upgrades, invites, etc.",
        Domain.CONTENT: "Excellent! What engagement actions matter most? For example: article views, video plays, comments, shares, etc.",
        Domain.OTHER: "Got it! What are the key user actions you want to track on your site?"
    }
    
    message = {
        "role": "assistant",
        "content": prompts.get(domain, prompts[Domain.OTHER])
    }
    state["messages"].append(message)
    state["current_step"] = "extract_actions"
    
    return state

def extract_actions_node(state: ConversationState) -> ConversationState:
    """Extract key actions from user response"""
    last_user_message = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), "")
    
    parser = PydanticOutputParser(pydantic_object=ExtractedActions)
    prompt = ChatPromptTemplate.from_template(
        """Extract key actions/events from this response:

User response: {response}

Extract specific, actionable events. Convert to snake_case past tense where possible.
Example: "add to cart" -> "added_to_cart"

{format_instructions}"""
    )
    
    chain = prompt | llm | parser
    result = chain.invoke({
        "response": last_user_message,
        "format_instructions": parser.get_format_instructions()
    })
    
    state["key_actions"] = result.actions
    state["current_step"] = "ask_segments"
    
    return state

def ask_segments_node(state: ConversationState) -> ConversationState:
    """Ask about user segments"""
    message = {
        "role": "assistant",
        "content": "Do you have different types of users? For example: free/paid, buyer/seller, admin/member, etc. (or just say 'no' if everyone is the same)"
    }
    state["messages"].append(message)
    state["current_step"] = "extract_segments"
    
    return state

def extract_segments_node(state: ConversationState) -> ConversationState:
    """Extract user segments"""
    last_user_message = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), "")
    
    # Check if user said no/none
    if any(word in last_user_message.lower() for word in ["no", "none", "same", "everyone"]):
        state["user_segments"] = []
        state["current_step"] = "ask_goals"
        return state
    
    parser = PydanticOutputParser(pydantic_object=ExtractedSegments)
    prompt = ChatPromptTemplate.from_template(
        """Extract user segments/types from this response:

User response: {response}

{format_instructions}"""
    )
    
    chain = prompt | llm | parser
    result = chain.invoke({
        "response": last_user_message,
        "format_instructions": parser.get_format_instructions()
    })
    
    state["user_segments"] = result.segments
    state["current_step"] = "ask_goals"
    
    return state

def ask_goals_node(state: ConversationState) -> ConversationState:
    """Ask about business goals"""
    message = {
        "role": "assistant",
        "content": "What metrics or goals are most important to you? For example: conversion rate, retention, revenue, engagement, etc."
    }
    state["messages"].append(message)
    state["current_step"] = "extract_goals"
    
    return state

def extract_goals_node(state: ConversationState) -> ConversationState:
    """Extract business goals"""
    last_user_message = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "user"), "")
    
    parser = PydanticOutputParser(pydantic_object=ExtractedGoals)
    prompt = ChatPromptTemplate.from_template(
        """Extract business goals/metrics from this response:

User response: {response}

{format_instructions}"""
    )
    
    chain = prompt | llm | parser
    result = chain.invoke({
        "response": last_user_message,
        "format_instructions": parser.get_format_instructions()
    })
    
    state["business_goals"] = result.goals
    state["current_step"] = "complete"
    state["ready_for_labeling"] = True
    
    return state

def complete_node(state: ConversationState) -> ConversationState:
    """Final message"""
    actions_summary = ", ".join(state["key_actions"][:3])
    message = {
        "role": "assistant",
        "content": f"Perfect! I understand you want to track: {actions_summary}. Now let's identify the specific elements on your site. Click 'Start Labeling' to begin marking the buttons and elements you want to track."
    }
    state["messages"].append(message)
    
    return state

# Routing function
def route_conversation(state: ConversationState) -> str:
    """Route to next node based on current step"""
    step = state.get("current_step", "greeting")
    
    routes = {
        "greeting": "classify_domain",
        "classify_domain": "ask_actions",
        "ask_actions": "extract_actions",
        "extract_actions": "ask_segments",
        "ask_segments": "extract_segments",
        "extract_segments": "ask_goals",
        "ask_goals": "extract_goals",
        "extract_goals": "complete",
        "complete": END
    }
    
    return routes.get(step, END)

# Build graph
def create_conversation_graph():
    graph = StateGraph(ConversationState)
    
    # Add nodes
    graph.add_node("greeting", greeting_node)
    graph.add_node("classify_domain", classify_domain_node)
    graph.add_node("ask_actions", ask_actions_node)
    graph.add_node("extract_actions", extract_actions_node)
    graph.add_node("ask_segments", ask_segments_node)
    graph.add_node("extract_segments", extract_segments_node)
    graph.add_node("ask_goals", ask_goals_node)
    graph.add_node("extract_goals", extract_goals_node)
    graph.add_node("complete", complete_node)
    
    # Set entry point
    graph.set_entry_point("greeting")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "greeting",
        route_conversation
    )
    graph.add_conditional_edges(
        "classify_domain",
        route_conversation
    )
    graph.add_conditional_edges(
        "ask_actions",
        route_conversation
    )
    graph.add_conditional_edges(
        "extract_actions",
        route_conversation
    )
    graph.add_conditional_edges(
        "ask_segments",
        route_conversation
    )
    graph.add_conditional_edges(
        "extract_segments",
        route_conversation
    )
    graph.add_conditional_edges(
        "ask_goals",
        route_conversation
    )
    graph.add_conditional_edges(
        "extract_goals",
        route_conversation
    )
    graph.add_conditional_edges(
        "complete",
        route_conversation
    )
    
    return graph.compile()

# Export compiled graph
conversation_workflow = create_conversation_graph()
