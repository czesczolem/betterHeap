# BetterHeap - Implementation Plan

## System Overview

### What We're Building
**Conversational AI-first web analytics platform** built on PostHog infrastructure. Think "Heap + AI guidance" - auto-capture everything, but use conversational AI to structure data cleanly from day one and query it naturally.

### Core Hypothesis
Conversational AI can make analytics setup and usage **10x easier** than current GUI-based tools (Heap, PostHog, Mixpanel).

### How It Works
```
1. Install Chrome extension + tracking script
2. Chat with AI: "I run an e-commerce site..."
3. Label key elements (click "Add to Cart" button)
4. AI generates taxonomy + hygiene rules
5. Deploy to PostHog (Actions + Transformations)
6. Get insights via chat: "What's our conversion rate?"
```

## Architecture (PoC)

```
┌─────────────────┐
│  Chrome Ext     │──┐
│  Setup Chat UI  │  │
└─────────────────┘  │
                     ▼
┌─────────────────────────────┐
│  Setup API (Python/FastAPI) │
│  - Conversation manager      │
│  - Element labeling store    │
│  - AI Agent (LangChain)      │
└─────────────────────────────┘
            │
            ├──► LLM (OpenAI/Claude)
            │
            ▼
┌─────────────────────────────┐
│  PostHog API                │
│  - Create Actions            │
│  - Deploy Transformations    │
│  - Query via HogQL           │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  Web Dashboard (Next.js)    │
│  - Analytics chat interface  │
│  - Pre-built dashboards      │
└─────────────────────────────┘
```

## PoC Scope (8 Weeks)

### Week 1-2: Setup Chat & Labeling
**Goal**: Users can describe their product and label UI elements

**Build**:
- Chrome extension (React + TypeScript)
  - Chat interface
  - Element labeling mode (click to label)
  - CSS selector capture
- Setup API
  - Conversation state management
  - Store labeled elements
  - Basic LLM integration

**Demo**: "User chats about e-commerce site, labels 3 buttons"

---

### Week 3-4: AI Rules Generation
**Goal**: AI generates clean taxonomy and deploys to PostHog

**Build**:
- Rules generation agent
  - Analyze conversation + labels
  - Generate taxonomy (canonical events, properties)
  - Create normalization rules (productId → product_id)
  - Define PII removal rules
- PostHog API integration
  - Create Actions programmatically
  - Deploy Transformations (Hog Functions)
- Config database (PostgreSQL)
  - Store taxonomies
  - Store rules bundles

**Demo**: "AI creates 'Added to Cart' action, deploys PII filter"

---

### Week 5-6: Analytics Chat
**Goal**: Users query data via natural language

**Build**:
- Query agent
  - Parse natural language questions
  - Generate HogQL queries
  - Format responses
- Web dashboard (basic)
  - Chat interface
  - Display query results
  - Simple charts (conversion rates, counts)
- Handle 5 query types:
  - Conversion rates
  - Event counts
  - Top items (products, pages)
  - Drop-off rates
  - Time-series trends

**Demo**: "What's our checkout conversion rate today?" → "20% (84/420)"

---

### Week 7-8: Testing & Refinement
**Goal**: Validate with beta users, measure success metrics

**Build**:
- Pre-built dashboard templates
  - E-commerce funnel
  - Engagement metrics
- Onboarding flow polish
- Error handling
- Documentation

**Test**:
- 5-10 beta users (e-commerce sites)
- Measure:
  - ⏱️ Setup time (target: <30 min)
  - 📊 Data quality (naming consistency)
  - 💬 Chat query success rate
  - 😊 User satisfaction

**Deliver**: Demo video + metrics deck

---

## Tech Stack

### Frontend
- **Chrome Extension**: React + TypeScript
- **Web Dashboard**: Next.js + TypeScript
- **Tracking Script**: PostHog's native JS SDK

### Backend
- **API**: Python + FastAPI
- **AI Framework**: LangChain
- **LLM**: OpenAI GPT-4 or Anthropic Claude
- **Database**: PostgreSQL (config storage)

### Infrastructure
- **Analytics Engine**: PostHog (self-hosted or cloud)
- **Hosting**: Vercel (frontend) + Railway/Render (backend)
- **Auth**: Clerk or Auth0

## Success Criteria (Go/No-Go)

### Must Achieve (Week 8):
- ✅ Setup time: <30 minutes (vs. 4+ hours manual)
- ✅ Chat query success: >70% of questions answered correctly
- ✅ User satisfaction: >4/5 rating
- ✅ 5 beta users complete full flow

### Nice to Have:
- 📈 Users prefer chat over GUI (>60% query volume)
- 🎯 Taxonomy quality: >90% events follow conventions
- 💰 Users willing to pay (>3 LOIs)

## Post-PoC Decision Tree

### If Success (Metrics ✅)
**Option A**: Raise pre-seed ($500K)
- Build standalone platform
- Decouple from PostHog dependency
- Hire 2-3 engineers

**Option B**: Partner with PostHog
- Become official "AI layer"
- Revenue share model
- Faster go-to-market

### If Partial Success (Mixed Results)
- Pivot to one strong aspect (setup OR querying)
- Narrow to specific vertical (e-commerce only)
- Extended beta (3 more months)

### If Failure (Metrics ❌)
- Conversational UI not meaningfully better
- AI too unreliable for production
- Kill project, extract learnings

## Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **LLM unreliability** | Constrain to templates, validate outputs |
| **PostHog API limits** | Self-host PostHog for PoC |
| **Element selectors break** | Teach users to use data attributes |
| **Query generation fails** | Fallback to pre-defined query templates |
| **No beta users** | Outreach to YC companies, indie hackers |

## Resource Requirements

### Team
- 1 Full-stack engineer (you)
- 1 LLM/AI contractor (part-time, 20hrs/week)
- Optional: 1 designer (UI/UX polish, week 6-7)

### Budget (8 weeks)
- **LLM API costs**: $500-1000 (GPT-4 + embeddings)
- **PostHog hosting**: $0 (use cloud free tier)
- **Infrastructure**: $100-200/mo (Vercel + Railway)
- **Contractor**: $4000-6000 (AI engineer)
- **Total**: ~$5500-8000

### Time Commitment
- **Full-time**: 8 weeks straight
- **Part-time**: 16 weeks (20hrs/week)

## Next Actions

1. [ ] Set up PostHog instance (cloud or self-hosted)
2. [ ] Create Chrome extension boilerplate
3. [ ] Set up FastAPI backend skeleton
4. [ ] Integrate LLM (OpenAI API key)
5. [ ] Build basic chat interface
6. [ ] Implement element labeling (week 1 goal)

---

## Reference Implementation Flow

See `implementation_draft.txt` for detailed:
- Sample chat transcript
- Element labeling payload structure
- Rules bundle JSON schema
- PostHog API integration examples
- Before/after event transformation examples
- Sample analytics queries

---

**Last Updated**: Jan 7, 2026  
**Status**: PoC Planning Phase  
**Next Milestone**: Week 2 - Working setup chat
