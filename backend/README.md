# BetterHeap Backend - Conversational AI

Simple FastAPI backend with LangGraph for guided analytics setup.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OPENAI_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## API

- `POST /api/v1/sessions/create` - Start new setup session
- `POST /api/v1/chat/message` - Send chat message
- `GET /health` - Health check

## Test

```bash
# Create session
curl -X POST http://localhost:8000/api/v1/sessions/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'

# Send message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "ssn_xxx", "message": "I have an e-commerce site"}'
```

## LangGraph Flow

```
greeting → product_discovery → goal_understanding → labeling_ready → END
```

State persists in memory (add Supabase later).
