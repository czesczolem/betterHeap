# BetterHeap Backend - Implementation Plan (No Code)

**Date**: January 7, 2026  
**Status**: Planning Phase  
**Goal**: Build intelligent conversational AI backend for analytics setup with context-aware HTML analysis

---

## 1. System Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Chrome Extension                         │
│  - Sends chat messages                                       │
│  - Sends labeled elements with full HTML context            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI + WebSocket)                     │  │
│  │  - POST /api/v1/sessions/create                      │  │
│  │  - POST /api/v1/chat/message                         │  │
│  │  - POST /api/v1/elements/label                       │  │
│  │  - POST /api/v1/elements/analyze-context             │  │
│  │  - POST /api/v1/taxonomy/generate                    │  │
│  │  - POST /api/v1/taxonomy/approve                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LangGraph State Machine (Conversation Orchestrator) │  │
│  │  - Multi-stage conversation flow                     │  │
│  │  - Context-aware question generation                 │  │
│  │  - State transitions with checkpoints                │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AI Agents (LangChain + LLM)                         │  │
│  │  - Product Type Classifier                           │  │
│  │  - HTML Context Analyzer                             │  │
│  │  - Question Generator Agent                          │  │
│  │  - Taxonomy Builder Agent                            │  │
│  │  - Ambiguity Resolver Agent                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Layer (Supabase PostgreSQL)                    │  │
│  │  - Setup sessions & state                            │  │
│  │  - Conversation history                              │  │
│  │  - Labeled elements with HTML context                │  │
│  │  - Generated taxonomies                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostHog API Integration                    │
│  - Deploy Actions                                            │
│  - Deploy Transformations (Hog Functions)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. LangGraph State Machine Design

### Why LangGraph over Plain LangChain?

- **Multi-stage workflows**: Setup flow has 5-7 distinct stages
- **State persistence**: Can pause/resume conversations across browser sessions
- **Conditional branching**: Different paths based on product type, HTML analysis, etc.
- **Error recovery**: Retry failed steps without losing context
- **Checkpointing**: Save state at each decision point

### Conversation States (Nodes in Graph)

```
[START] → Initial Greeting
    │
    ▼
Product Discovery (Node 1)
    │ (Classify: E-commerce, SaaS, Content, Marketplace, Other)
    ▼
Goal Understanding (Node 2)
    │ (Extract: conversion tracking, engagement, retention, etc.)
    ▼
Element Labeling Guide (Node 3)
    │ (Trigger: Extension enters labeling mode)
    ▼
HTML Context Analysis (Node 4) ◄───┐
    │ (Analyze each labeled element)  │
    │                                  │
    ▼                                  │
Ambiguity Resolution (Node 5)        │
    │ (Ask clarifying questions)      │
    │                                  │
    ├─ More questions needed ─────────┘
    │
    ▼
Taxonomy Generation (Node 6)
    │ (Build event schema + rules)
    ▼
Review & Approval (Node 7)
    │ (User previews and approves)
    ▼
Deployment (Node 8)
    │ (Deploy to PostHog)
    ▼
[END] → Setup Complete
```

### State Schema (Shared across all nodes)

```python
# Conceptual schema - not actual code
SetupState = {
    "session_id": str,
    "project_id": str,
    "user_id": str,
    
    # Conversation context
    "messages": List[Message],  # Full conversation history
    "current_node": str,  # Which node we're in
    
    # Extracted information
    "product_type": str | None,  # "ecommerce", "saas", "marketplace", etc.
    "product_description": str | None,
    "user_goals": List[str],  # ["conversion_rate", "top_products", ...]
    "user_types": List[str],  # ["buyer", "seller", ...] or None
    
    # Labeled elements with context
    "labeled_elements": List[{
        "id": str,
        "intent": str,  # User-provided name
        "selector": str,
        "text_content": str,
        "page_url": str,
        "html_context": {
            "parent_elements": List[str],  # Up to 3 levels up
            "siblings": List[str],  # Adjacent elements
            "children": List[str],  # Direct children
            "data_attributes": Dict,
            "nearby_text": str,
        },
        "page_analysis": {
            "page_type": str,  # "product_detail", "listing", "checkout", etc.
            "detected_patterns": List[str],  # ["multiple_products", "price_displayed", ...]
        },
        "clarifications_needed": List[str],  # Questions to ask about this element
        "resolved": bool,
    }],
    
    # Generated artifacts
    "generated_taxonomy": Dict | None,
    "posthog_deployment_plan": Dict | None,
    
    # Flow control
    "pending_questions": List[Dict],  # Questions waiting to be asked
    "errors": List[str],
    "retry_count": int,
}
```

---

## 3. HTML Context Analysis Strategy

### Problem Statement

When user clicks a button on a product page with 20 products, we need to determine:
- Is this about THIS specific product (SKU-123)?
- Is this about ALL products generically (any "Add to Cart" button)?
- Is this about a category of products?

### Analysis Pipeline

#### Step 1: Page Type Detection
**Input**: `page_url`, `html_structure`, `labeled_element`  
**Output**: `page_type` classification

**Detection Rules**:
- **Product Detail Page**: 
  - URL contains `/product/`, `/item/`, `/p/`
  - Single dominant product with price, images, description
  - Unique product ID in URL or data attributes
  
- **Product Listing Page**:
  - Multiple product cards with similar structure
  - Pagination or infinite scroll indicators
  - Filter/sort controls
  
- **Cart/Checkout Page**:
  - Form elements for shipping/payment
  - URL contains `/cart`, `/checkout`, `/order`
  - Summary of items with quantities
  
- **Homepage**:
  - Mixed content types
  - Navigation to multiple sections

**Implementation Approach**:
1. Use LLM with structured output (JSON schema) to classify
2. Provide HTML snippet (first 2000 chars) + URL + labeled element context
3. Prompt: "Classify this page type and explain your reasoning"

#### Step 2: Element Scope Detection
**Input**: `labeled_element`, `page_type`, `html_context`  
**Output**: `scope` + `clarification_questions`

**Scope Types**:
- `specific`: Tied to a specific entity (this product, this user)
- `generic`: Applies to any instance (any product, any button of this type)
- `contextual`: Depends on user state (logged-in user's cart)

**Detection Logic**:
```
IF page_type == "product_detail":
    IF element has data-product-id or data-sku:
        → scope = "specific"
        → question = "This button is on product page for '{product_name}'. 
                      Do you want to track clicks on THIS product specifically, 
                      or ANY product's '{button_text}' button?"
    ELSE:
        → scope = "generic"
        → question = None  # It's clearly generic
        
ELSE IF page_type == "product_listing":
    IF element is inside repeated container:
        → scope = "generic"
        → question = "This button appears on multiple products in a list. 
                      Should we track all clicks on ANY '{button_text}' button?"
    ELSE:
        → scope = "specific" (might be a filter button, etc.)
        
ELSE IF page_type == "cart":
    → scope = "contextual"
    → question = "This is in the cart. Should we track this for all users 
                  or only specific user segments?"
```

#### Step 3: Property Extraction Suggestions
**Input**: `labeled_element`, `html_context`, `scope`  
**Output**: `suggested_properties`

**Examples**:

**Scenario A**: User labels "Add to Cart" button on product detail page
```
Detected context:
- <button data-product-id="SKU-123" data-price="29.99">Add to Cart</button>
- Parent: <div class="product-detail" data-category="ceramics">
- Sibling: <h1>Handmade Ceramic Mug</h1>

Generated questions:
1. "I see this product has ID 'SKU-123'. Should I capture the product_id property?"
2. "I notice a price ($29.99) nearby. Should I track the product price?"
3. "This product is in category 'ceramics'. Should I capture the category?"

Suggested properties:
{
  "product_id": "data-product-id attribute",
  "product_name": "text from <h1> sibling",
  "price": "data-price attribute",
  "category": "data-category from parent",
  "quantity": "value from quantity selector (if found)"
}
```

**Scenario B**: User labels "Checkout" button on cart page
```
Detected context:
- <a href="/checkout" class="checkout-btn">Proceed to Checkout</a>
- Parent: <div class="cart-summary" data-total="54.99" data-item-count="3">
- No product-specific attributes

Generated questions:
1. "Should I track the cart value ($54.99) when checkout starts?"
2. "Should I track how many items (3) are in the cart?"

Suggested properties:
{
  "cart_value": "data-total from parent",
  "item_count": "data-item-count from parent",
  "currency": "USD" (detected from page or inferred)
}
```

#### Step 4: Duplicate/Similar Element Detection
**Purpose**: Prevent redundant labeling

```
When user labels element #2:
  Compare with all previously labeled elements:
    - Similar selector structure?
    - Same page type?
    - Same intent/purpose?
  
  If highly similar:
    → Ask: "You already labeled '{previous_intent}' which looks similar. 
            Are these the same action or different?"
    
  If user says "same":
    → Merge into one canonical event
    
  If user says "different":
    → Ask: "How are they different? (e.g., different user types, 
            different contexts, different properties)"
```

---

## 4. Question Generation Strategy

### Principles
1. **Progressive disclosure**: Start broad, get specific
2. **Context-aware**: Questions depend on previous answers
3. **Minimize cognitive load**: Max 1-2 questions before each labeling action
4. **Validation**: Confirm understanding before generating taxonomy

### Question Types & When to Ask

#### Initial Questions (Before Any Labeling)
1. "What type of product/app are you building?"
   - **Purpose**: Determines question templates and taxonomy patterns
   - **Follow-ups depend on answer**:
     - E-commerce → "Do you have different product types or categories?"
     - SaaS → "Is this free, freemium, or paid? Subscription or one-time?"
     - Marketplace → "Are there multiple user types (buyers/sellers)?"

2. "What are your main analytics goals?"
   - **Purpose**: Prioritizes which events to focus on
   - **Examples**: "conversion tracking", "engagement metrics", "churn prediction"
   - **Limits scope**: Don't ask about retention if they only care about conversion

#### During Labeling (Context-Aware)

**When user enters an intent like "added_to_cart"**:
```
Questions to ask before they click:
1. "Is this for a specific product or any product?"
2. "Should I track who added it (user/session ID)?"
3. "Do you care about quantity added?"

→ User clicks element →

Questions to ask after analyzing HTML:
1. "I found a product_id and price. Should I include these?"
2. "This product is in category 'ceramics'. Track category too?"
```

**When ambiguity is detected**:
```
Example: Button with text "Buy Now" on a listing page

Questions:
1. "This 'Buy Now' button appears next to product 'Ceramic Mug'. 
    Should this event be:
    a) 'buy_now_clicked' (generic for any product)
    b) 'product_ceramic_mug_buy_now' (specific to this product)
    c) Something else?"
    
2. "Should I capture which product was clicked as a property?"
```

#### Before Taxonomy Generation
```
Confirmation questions:
1. "I've identified these key user actions: [list of intents]. 
    Is anything missing?"
    
2. "For tracking, I'll capture: [list of properties].
    Should I add or remove anything?"
```

---

## 5. Agent Architecture (LangChain + LLM)

### Agent 1: Product Classifier
**Input**: User's description of their product  
**Output**: Structured classification

```
LLM Prompt Template:
"User said: '{user_input}'

Classify their product into one of these categories:
- ecommerce (selling physical products)
- saas (software as service)
- marketplace (buyers + sellers)
- content (blog, media, publishing)
- other

Also extract:
- Industry (e.g., fashion, food, B2B software)
- Key characteristics (e.g., subscription model, physical goods)

Output as JSON: {
  'category': str,
  'industry': str,
  'characteristics': [str],
  'confidence': float
}"
```

**Chain Type**: Simple LLM chain with structured output parser

### Agent 2: HTML Context Analyzer
**Input**: Element HTML + surrounding context + page URL  
**Output**: Analysis with follow-up questions

```
LLM Prompt Template:
"A user is setting up analytics for their website. They labeled this element:

Element: {element_html}
Parent elements: {parent_context}
Siblings: {sibling_elements}
Page URL: {url}
Page title: {title}
User's intent name: {intent}

Analyze:
1. What type of page is this? (product detail, listing, checkout, homepage, etc.)
2. Is this element about a specific entity or generic?
3. What properties should we capture? (look for data attributes, nearby text, IDs)
4. Are there any ambiguities that need clarification?

Output as JSON: {
  'page_type': str,
  'element_scope': 'specific' | 'generic' | 'contextual',
  'suggested_properties': {key: {source: str, value: str}},
  'clarification_questions': [str],
  'confidence': float
}"
```

**Chain Type**: LLM chain with few-shot examples

### Agent 3: Ambiguity Resolver
**Input**: Analysis results + conversation history  
**Output**: Specific questions to ask user

**Triggers ambiguity questions when**:
- Multiple similar elements labeled
- Element appears in repeated structure (product cards)
- Conflicting data attributes
- User intent is vague ("button_click" instead of "purchase_completed")

### Agent 4: Taxonomy Builder
**Input**: All labeled elements (resolved) + product type + user goals  
**Output**: Complete taxonomy with canonical events, properties, normalization rules

```
LLM Prompt (Simplified):
"Build a clean analytics taxonomy for:

Product type: {product_type}
Goals: {goals}
User types: {user_types}

Labeled events:
{for each element:
  - Intent: {intent}
  - Properties: {properties}
  - Page context: {page_type}
}

Generate:
1. Canonical event names (following naming conventions)
2. Required vs optional properties for each event
3. Normalization rules (e.g., productId → product_id)
4. PII removal rules
5. Noise suppression rules

Output as structured JSON matching this schema: {schema}"
```

**Post-processing**:
- Validate against best practices (snake_case, no PII, consistent naming)
- Add PostHog-specific configuration (Actions, Transformations)

### Agent 5: Question Generator (Dynamic)
**Input**: Current state + conversation history  
**Output**: Next best question to ask

**Decision tree**:
1. If no product_type → ask about product type
2. If no goals → ask about goals
3. If no labeled elements → guide to labeling
4. If labeled elements have ambiguities → resolve ambiguities
5. If all resolved → generate taxonomy

---

## 6. Database Schema (Supabase PostgreSQL)

### Tables

#### `setup_sessions`
```sql
- id (uuid, PK)
- user_id (uuid, FK)
- project_id (text)  -- Later links to customer's project
- posthog_project_id (text, nullable)
- status (enum: 'active', 'completed', 'abandoned')
- current_node (text)  -- Which LangGraph node we're in
- state_checkpoint (jsonb)  -- Full LangGraph state
- created_at (timestamp)
- updated_at (timestamp)
```

#### `conversation_messages`
```sql
- id (uuid, PK)
- session_id (uuid, FK → setup_sessions)
- role (enum: 'user', 'assistant', 'system')
- content (text)
- metadata (jsonb)  -- attachments, tool calls, etc.
- created_at (timestamp)
```

#### `labeled_elements`
```sql
- id (uuid, PK)
- session_id (uuid, FK)
- label_id (text)  -- "lbl_001"
- intent (text)  -- User-provided name
- selector (text)
- text_content (text)
- page_url (text)
- html_context (jsonb)  -- Full context analysis
- page_analysis (jsonb)  -- Page type, patterns
- clarifications (jsonb)  -- Questions asked & answers
- resolved (boolean)
- properties_to_capture (jsonb)
- created_at (timestamp)
```

#### `generated_taxonomies`
```sql
- id (uuid, PK)
- session_id (uuid, FK)
- version (text)  -- "tax_v1", "tax_v2" if revised
- canonical_events (jsonb)
- normalization_rules (jsonb)
- pii_rules (jsonb)
- noise_rules (jsonb)
- posthog_actions_plan (jsonb)
- transformations_plan (jsonb)
- approved (boolean)
- deployed (boolean)
- created_at (timestamp)
```

---

## 7. API Endpoints Design

### Core Endpoints

#### `POST /api/v1/sessions/create`
**Purpose**: Initialize a new setup session  
**Request**:
```json
{
  "user_id": "usr_123",
  "project_name": "My E-commerce Site",
  "posthog_project_id": "14721"  // optional
}
```
**Response**:
```json
{
  "session_id": "ssn_5f3c",
  "status": "active",
  "first_message": "Hi! I'm here to help you set up analytics..."
}
```

#### `POST /api/v1/chat/message`
**Purpose**: Send a chat message, get AI response  
**Request**:
```json
{
  "session_id": "ssn_5f3c",
  "message": "I'm building a marketplace for handmade goods"
}
```
**Response**:
```json
{
  "reply": "Great! A marketplace typically has buyers and sellers...",
  "state_updated": true,
  "next_action": null | "start_labeling" | "review_taxonomy"
}
```

#### `POST /api/v1/elements/label`
**Purpose**: Submit a labeled element for analysis  
**Request**:
```json
{
  "session_id": "ssn_5f3c",
  "label": {
    "label_id": "lbl_001",
    "intent": "added_to_cart",
    "selector": "button[data-test='add-to-cart']",
    "text_content": "Add to cart",
    "page_url": "https://shop.example.com/products/ceramic-mug-123",
    "html_context": {
      "parent_elements": ["<div class='product-detail'>"],
      "data_attributes": {"data-product-id": "ceramic-mug-123"},
      ...
    }
  }
}
```
**Response**:
```json
{
  "analysis": {
    "page_type": "product_detail",
    "element_scope": "specific",
    "suggested_properties": {
      "product_id": {"source": "data-product-id", "value": "ceramic-mug-123"}
    }
  },
  "clarification_questions": [
    "This button is on a specific product page. Do you want to track clicks on THIS product specifically, or ANY product's 'Add to cart' button?"
  ],
  "requires_user_input": true
}
```

#### `POST /api/v1/elements/resolve-clarification`
**Purpose**: User answers clarification questions  
**Request**:
```json
{
  "session_id": "ssn_5f3c",
  "label_id": "lbl_001",
  "answers": {
    "scope": "generic",  // Track ANY product, not just this one
    "include_product_id": true,
    "include_price": true
  }
}
```

#### `POST /api/v1/taxonomy/generate`
**Purpose**: Generate taxonomy after all elements are labeled  
**Request**:
```json
{
  "session_id": "ssn_5f3c"
}
```
**Response**:
```json
{
  "taxonomy_id": "tax_v1",
  "preview": {
    "canonical_events": [...],
    "normalization_rules": [...],
    "pii_rules": [...],
    ...
  }
}
```

#### `POST /api/v1/taxonomy/approve`
**Purpose**: User approves generated taxonomy  
**Request**:
```json
{
  "session_id": "ssn_5f3c",
  "taxonomy_id": "tax_v1",
  "approved": true
}
```
**Response**:
```json
{
  "status": "deploying",
  "posthog_deployment": {
    "actions_created": 3,
    "transformations_created": 3,
    "status_url": "/api/v1/deployment/status/..."
  }
}
```

---

## 8. LangGraph Implementation Approach

### State Machine Construction

**Nodes** (processing functions):
1. `initial_greeting` - Welcome message, ask about product
2. `product_classification` - Call classifier agent, store result
3. `goal_extraction` - Ask about analytics goals
4. `labeling_coordinator` - Guide user through labeling process
5. `html_analyzer` - Process each labeled element
6. `ambiguity_resolver` - Ask clarifying questions
7. `taxonomy_generator` - Build final taxonomy
8. `review_collector` - Show preview, wait for approval
9. `deployer` - Deploy to PostHog

**Edges** (transitions):
- `initial_greeting` → `product_classification`
- `product_classification` → `goal_extraction`
- `goal_extraction` → `labeling_coordinator`
- `labeling_coordinator` → `html_analyzer` (when element received)
- `html_analyzer` → `ambiguity_resolver` (if clarifications needed)
- `ambiguity_resolver` → `html_analyzer` (loop until resolved)
- `html_analyzer` → `taxonomy_generator` (when all resolved)
- `taxonomy_generator` → `review_collector`
- `review_collector` → `deployer` (if approved)
- `review_collector` → `taxonomy_generator` (if changes requested)

**Conditional Edges**:
```python
# Pseudo-code
def should_ask_more_questions(state):
    if state['labeled_elements'] has unresolved items:
        return "ambiguity_resolver"
    else:
        return "taxonomy_generator"
```

### Checkpointing Strategy

**Checkpoint after each node**:
- Saves full state to database
- Allows pausing/resuming
- Enables time-travel debugging

**Recovery from errors**:
- If LLM call fails → retry with exponential backoff
- If retry exhausted → ask user to rephrase or skip
- Never lose conversation progress

---

## 9. Edge Cases & Handling

### Case 1: User Labels Same Element Twice
**Detection**: Compare selectors + page URLs  
**Action**: "You already labeled this element as '{previous_intent}'. Did you mean to label it again?"

### Case 2: User Provides Vague Intent Names
**Example**: "button1", "click_here"  
**Action**: "Could you be more specific? What happens when users click this? (e.g., 'purchase_completed', 'signup_started')"

### Case 3: No Useful HTML Attributes
**Example**: Button with no data attributes, generic class names  
**Action**: "This button doesn't have unique identifiers. We'll track it by position, but it might break if your site layout changes. Consider adding a data-test-id attribute."

### Case 4: User Abandons Mid-Setup
**Action**: Save checkpoint, send follow-up email with resume link

### Case 5: Element Selector Becomes Invalid
**Detection**: During testing phase, selector doesn't match  
**Action**: Alert user, suggest updating or using more robust selector

---

## 10. Technology Stack (Final)

### Backend
- **Framework**: FastAPI 0.109+ (async, modern Python)
- **AI/ML**:
  - **LangGraph** 0.2+ (state machine orchestration)
  - **LangChain** 0.1+ (agent framework, chains)
  - **OpenAI GPT-4** or **Anthropic Claude 3.5** (LLM)
  - **Structured output parsing** (JSON schema validation)
- **Database**: Supabase (PostgreSQL + realtime)
- **Caching**: Redis (conversation state, rate limiting)
- **Task Queue**: Celery or FastAPI BackgroundTasks (for PostHog deployment)

### Dependencies (estimated)
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
langchain>=0.1.0
langgraph>=0.2.0
openai>=1.12.0 or anthropic>=0.18.0
supabase>=2.3.0
redis>=5.0.0
pydantic>=2.5.0
httpx>=0.26.0
beautifulsoup4>=4.12.0  # HTML parsing
```

---

## 11. Development Phases

### Phase 1: Foundation (Week 1-2)
- ✅ FastAPI setup with basic endpoints
- ✅ Supabase schema creation
- ✅ Simple LangChain conversation (no LangGraph yet)
- ✅ Test with hardcoded questions
- **Goal**: Extension can send messages, get basic responses

### Phase 2: HTML Analysis (Week 3)
- ✅ HTML Context Analyzer agent
- ✅ Page type classification
- ✅ Property extraction suggestions
- **Goal**: Analyze labeled elements intelligently

### Phase 3: LangGraph Integration (Week 4)
- ✅ Build state machine with 5 core nodes
- ✅ Implement checkpointing to database
- ✅ Add conditional edges
- **Goal**: Multi-stage conversation with state persistence

### Phase 4: Ambiguity Resolution (Week 5)
- ✅ Ambiguity Resolver agent
- ✅ Question generation logic
- ✅ Handle user clarifications
- **Goal**: Smart follow-up questions based on HTML analysis

### Phase 5: Taxonomy Generation (Week 6)
- ✅ Taxonomy Builder agent
- ✅ Generate PostHog Actions & Transformations
- ✅ Preview UI for user approval
- **Goal**: Output ready-to-deploy taxonomy

### Phase 6: PostHog Integration (Week 7)
- ✅ PostHog API integration
- ✅ Deploy Actions programmatically
- ✅ Deploy Transformations (Hog Functions)
- **Goal**: Full end-to-end deployment

### Phase 7: Testing & Refinement (Week 8)
- ✅ Test with 5-10 different website types
- ✅ Refine prompts based on results
- ✅ Add error handling and edge cases
- **Goal**: Production-ready PoC

---

## 12. Success Metrics for Backend

### Performance
- **Response time**: < 2 seconds for chat messages
- **HTML analysis**: < 5 seconds per element
- **Taxonomy generation**: < 10 seconds

### Quality
- **Classification accuracy**: > 90% correct product type
- **Property suggestion accuracy**: > 85% relevant properties
- **User satisfaction with questions**: > 4/5 rating

### Reliability
- **Uptime**: 99.5%
- **Error rate**: < 2%
- **State recovery**: 100% (no lost conversations)

---

## 13. Security Considerations

### Authentication
- API keys for extension ↔ backend communication
- JWT tokens for user sessions
- PostHog API key securely stored (environment variables)

### Data Privacy
- No PII stored unless explicitly needed
- Conversation logs encrypted at rest
- Automatic deletion of abandoned sessions after 30 days

### Rate Limiting
- 100 requests/hour per user during setup
- 10 LLM calls/minute (prevent abuse)

---

## 14. Next Steps (After Plan Approval)

1. **Set up backend repository structure**
2. **Initialize FastAPI + Supabase connection**
3. **Create first endpoint**: `/sessions/create`
4. **Build simple Product Classifier agent**
5. **Test end-to-end: Extension → Backend → Response**

---

**Questions to Resolve Before Implementation:**
1. OpenAI GPT-4 vs Anthropic Claude? (Cost, performance trade-offs)
2. Host LLM locally (Llama 3) or use API? (Latency vs control)
3. Real-time (WebSocket) or polling for status updates?
4. Should we support resuming setup across multiple sessions?

**Ready to start coding once you approve this plan!** 🚀
