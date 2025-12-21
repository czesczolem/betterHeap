# Architecture Diagram - BetterHeap (MVP)

## Product Overview

### What is it?
An AI-powered web analytics platform that combines the ease of Heap's auto-tracking with intelligent data structuring through conversational AI. Unlike traditional analytics tools where data becomes messy and hard to query, BetterHeap uses an AI chatbot (via Chrome extension) to guide users through setup, understand their tracking needs, and automatically create clean, harmonized data structures that are ready to analyze.

### Business Value
**Problem**: Current web analytics tools like Heap and Mixpanel are either too complex to set up or produce messy, unstructured data. Heap auto-captures everything but the data becomes chaotic and hard to query. Mixpanel requires extensive manual setup and technical knowledge. Companies spend weeks configuring analytics, cleaning data, and still struggle to get meaningful insights because their event data is inconsistent.

**The Data Quality Gap**: Teams implement analytics quickly but realize months later that their data is unusable - inconsistent naming conventions, missing properties, duplicate events, and no clear taxonomy. This forces expensive data cleanup projects and rebuilding dashboards.

**Solution**: An analytics platform that combines automatic tracking with AI-guided data structuring. Our Chrome extension chatbot walks users through setup, understands their business goals, asks intelligent questions about what they want to track, and automatically creates a clean, harmonized data structure with filters and transformations applied at ingestion. The result: analytics-ready data from day one, with an AI assistant that helps query and visualize insights.

**Target Market**: Fast-growing startups and scale-ups (10-200 employees) who need powerful analytics but lack dedicated data engineers or extensive technical resources.

**Key Benefits**:
- **10-minute setup** - Chrome extension + conversational setup (vs. weeks of configuration)
- **Clean data from day one** - AI-structured taxonomy and automatic harmonization
- **No data engineering required** - filters and transformations handled automatically
- **Natural language queries** - ask questions, get insights without learning complex tools
- **Plug-and-play dashboards** - pre-built for common use cases
- **Cost-effective** - simpler infrastructure, faster time-to-value

### How It Works

1. **Install Chrome extension** and add tracking script to website
2. **Chat with Setup AI** - describe your product and what you want to track
3. **AI asks clarifying questions** about user flows, key actions, and business metrics
4. **System generates data structure** - event taxonomy, properties, naming conventions
5. **User approves structure** and AI configures filters/transformations
6. **Tracking begins** - script sends events, filters ensure clean data reaches database
7. **Analytics ready immediately** - pre-built dashboards populate automatically
8. **Chat with Analytics AI** for custom queries, graphs, and insights

### Core Innovation
Traditional analytics tools force you to choose: easy setup with messy data (Heap) or clean data with complex setup (Mixpanel). BetterHeap eliminates this tradeoff by using **AI-guided structuring at setup time** and **intelligent filtering at ingestion** to deliver both ease of use and data quality. Additionally, our **AI analytics assistant** makes querying data as simple as having a conversation.

---

## High-Level System Architecture

```mermaid
graph TB
    subgraph "User Touchpoints"
        User[Product User]
        Admin[Admin/PM/Analyst]
        WebApp[Client Web Application]
    end

    subgraph "Setup Layer"
        Extension[Chrome Extension<br/>Setup Chatbot UI]
        SetupChat[Setup Chat Service]
        SetupAgent[Setup AI Agent<br/>- Understand goals<br/>- Ask questions<br/>- Generate taxonomy]
    end

    subgraph "Ingestion Layer"
        TrackingScript[Tracking Script SDK<br/>Client-side]
        Gateway[Event Gateway<br/>Rate limiting & Auth]
        FilterEngine[Filter & Transform Engine<br/>- Apply rules<br/>- Harmonize data<br/>- Validate schema]
    end

    subgraph "Agent Layer"
        StructureAgent[Data Structure Agent<br/>- Generate taxonomy<br/>- Create filters<br/>- Define transforms]
        QueryAgent[Analytics Query Agent<br/>- Understand questions<br/>- Generate SQL<br/>- Create visualizations]
        InsightAgent[Insight Generation Agent<br/>- Pattern detection<br/>- Anomaly alerts<br/>- Recommendations]
    end

    subgraph "Analytics Layer"
        AnalyticsAPI[Analytics API]
        QueryService[Query Service]
        DashboardService[Dashboard Service]
        AnalyticsChat[Analytics Chat Interface]
    end

    subgraph "AI Infrastructure"
        LLM[LLM Provider<br/>OpenAI/Anthropic]
        VectorDB[(Vector Store<br/>Query patterns & context)]
    end

    subgraph "Data Layer"
        EventStream[(Event Stream<br/>Kafka/PubSub)]
        AnalyticsDB[(Analytics Database<br/>ClickHouse/TimeSeries)]
        ConfigDB[(Config Database<br/>PostgreSQL<br/>- Projects<br/>- Taxonomies<br/>- Filters<br/>- User settings)]
        CacheLayer[(Redis Cache<br/>Real-time aggregations)]
    end

    subgraph "Visualization Layer"
        WebDashboard[Web Dashboard<br/>- Pre-built dashboards<br/>- Custom graphs<br/>- Chat interface]
    end

    User --> WebApp
    WebApp --> TrackingScript
    Admin --> Extension
    Admin --> WebDashboard
    
    Extension --> SetupChat
    SetupChat --> SetupAgent
    SetupAgent --> StructureAgent
    
    TrackingScript --> Gateway
    Gateway --> EventStream
    EventStream --> FilterEngine
    
    FilterEngine --> AnalyticsDB
    FilterEngine --> ConfigDB
    
    SetupAgent --> LLM
    StructureAgent --> LLM
    QueryAgent --> LLM
    InsightAgent --> LLM
    
    QueryAgent --> VectorDB
    
    StructureAgent --> ConfigDB
    
    WebDashboard --> AnalyticsAPI
    AnalyticsAPI --> QueryService
    AnalyticsAPI --> DashboardService
    AnalyticsAPI --> AnalyticsChat
    
    AnalyticsChat --> QueryAgent
    QueryService --> QueryAgent
    QueryAgent --> AnalyticsDB
    
    DashboardService --> AnalyticsDB
    DashboardService --> CacheLayer
    
    QueryService --> CacheLayer
    QueryService --> AnalyticsDB
    QueryService --> ConfigDB
    
    InsightAgent --> AnalyticsDB
    InsightAgent --> WebDashboard
    
    style SetupAgent fill:#fff4e1
    style StructureAgent fill:#fff4e1
    style QueryAgent fill:#fff4e1
    style InsightAgent fill:#fff4e1
    style LLM fill:#ffe1e1
    style Extension fill:#e1f5ff
```

## MVP User Flow - Setup & First Insights

```mermaid
sequenceDiagram
    participant Admin as Admin/PM
    participant Ext as Chrome Extension
    participant Setup as Setup Chat Service
    participant SA as Setup AI Agent
    participant DA as Data Structure Agent
    participant Web as Web Application
    participant Script as Tracking Script
    participant Gateway as Event Gateway
    participant Filter as Filter Engine
    participant DB as Analytics Database
    participant Dashboard as Web Dashboard
    participant QA as Query Agent
    
    Admin->>Ext: Install extension & open
    Ext->>Setup: Initialize setup
    Setup->>SA: Start conversation
    
    Note over SA: "Hi! Let's set up analytics.<br/>What's your product about?"
    
    SA->>Admin: Ask about product
    Admin->>SA: "E-commerce app for handmade goods"
    
    SA->>Admin: "What user actions matter most?"
    Admin->>SA: "Purchases, add to cart, product views"
    
    SA->>Admin: "Do you have user types?"
    Admin->>SA: "Yes - buyers and sellers"
    
    Note over SA: Analyzes responses<br/>Generates questions about:<br/>- Checkout flow<br/>- Product categories<br/>- Key properties
    
    loop Clarifying Questions
        SA->>Admin: Ask specific questions
        Admin->>SA: Provide answers
    end
    
    SA->>DA: Generate data structure
    
    Note over DA: Creates:<br/>- Event taxonomy<br/>- Property schemas<br/>- Naming conventions<br/>- Filter rules
    
    DA-->>Setup: Structure proposal
    Setup-->>Ext: Show preview
    
    Ext-->>Admin: Display structure for approval
    Admin->>Ext: Approve structure
    Ext->>Setup: Confirm approval
    Setup->>DA: Deploy configuration
    DA->>DB: Save taxonomy & filters
    
    Setup-->>Ext: Provide tracking script
    Admin->>Web: Install tracking script
    
    Note over Web,Script: User interactions begin
    
    Web->>Script: User clicks "Add to Cart"
    Script->>Gateway: Send raw event
    Gateway->>Filter: Process event
    
    Note over Filter: Applies filters:<br/>- Standardize naming<br/>- Enrich properties<br/>- Validate schema<br/>- Remove noise
    
    Filter->>DB: Store clean event
    
    Note over DB: Data is structured<br/>and analytics-ready
    
    Admin->>Dashboard: Open dashboard
    Dashboard->>DB: Query events
    DB-->>Dashboard: Clean, structured data
    Dashboard-->>Admin: Show pre-built dashboard
    
    Admin->>Dashboard: Ask via chat:<br/>"What's our conversion rate today?"
    Dashboard->>QA: Process question
    
    Note over QA: Understands question<br/>Generates SQL query<br/>Formats response
    
    QA->>DB: Execute query
    DB-->>QA: Results
    QA->>Dashboard: Generate visualization
    Dashboard-->>Admin: Show graph + answer
```

## Setup Conversation Flow

```mermaid
graph TD
    Start[User Opens Extension] --> Intro[Setup AI: Introduction]
    Intro --> Q1[What type of product/app<br/>are you building?]
    Q1 --> Analyze1{AI Analyzes Response}
    
    Analyze1 --> Q2[What are the most important<br/>user actions to track?]
    Q2 --> Analyze2{AI Determines Domain}
    
    Analyze2 -->|E-commerce| E1[Questions about:<br/>- Product categories<br/>- Checkout steps<br/>- Payment methods]
    Analyze2 -->|SaaS| S1[Questions about:<br/>- Feature usage<br/>- User onboarding<br/>- Subscription events]
    Analyze2 -->|Content| C1[Questions about:<br/>- Content types<br/>- Engagement metrics<br/>- User segments]
    Analyze2 -->|Other| O1[Generic questions about:<br/>- Key workflows<br/>- Success metrics<br/>- User properties]
    
    E1 --> Q3[Property clarifications]
    S1 --> Q3
    C1 --> Q3
    O1 --> Q3
    
    Q3 --> Generate[Generate Data Structure]
    Generate --> Preview[Show Structure Preview:<br/>- Event names<br/>- Properties<br/>- Filters<br/>- Example queries]
    
    Preview --> Approve{User Approves?}
    Approve -->|No| Refine[What would you like<br/>to change?]
    Refine --> Generate
    Approve -->|Yes| Deploy[Deploy Configuration]
    Deploy --> Complete[Setup Complete!<br/>Install tracking script]
    
    style Analyze1 fill:#fff4e1
    style Analyze2 fill:#fff4e1
    style Generate fill:#fff4e1
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        UserAction[User Actions on Web]
        Setup[Setup Configuration]
    end
    
    subgraph "Ingestion Pipeline"
        Script[Tracking Script]
        Gateway[Event Gateway]
        Filter[Filter Engine]
        Stream[(Event Stream)]
    end
    
    subgraph "AI Processing"
        SetupAI[Setup AI Agent]
        StructureAI[Structure Agent]
        QueryAI[Query Agent]
    end
    
    subgraph "Storage"
        AnalyticsDB[(Analytics DB<br/>ClickHouse)]
        ConfigDB[(Config DB<br/>PostgreSQL)]
        Cache[(Redis Cache)]
    end
    
    subgraph "Output Interfaces"
        Dashboards[Pre-built Dashboards]
        CustomViz[Custom Visualizations]
        ChatInterface[AI Chat Interface]
        API[Analytics API]
    end
    
    UserAction --> Script
    Script --> Gateway
    Gateway --> Stream
    Stream --> Filter
    
    Setup --> SetupAI
    SetupAI --> StructureAI
    StructureAI --> ConfigDB
    
    ConfigDB --> Filter
    Filter --> AnalyticsDB
    
    AnalyticsDB --> Cache
    Cache --> Dashboards
    Cache --> CustomViz
    
    ChatInterface --> QueryAI
    QueryAI --> AnalyticsDB
    QueryAI --> ConfigDB
    QueryAI --> CustomViz
    
    AnalyticsDB --> API
    ConfigDB --> API
    
    style SetupAI fill:#fff4e1
    style StructureAI fill:#fff4e1
    style QueryAI fill:#fff4e1
```

## Technology Stack (MVP)

### Frontend
- **Chrome Extension**: React + TypeScript (Setup chatbot interface)
- **Web Dashboard**: Next.js + TypeScript (Analytics interface)
- **Tracking Script**: Vanilla JavaScript (Lightweight, < 10KB gzipped)
- **Charting**: Recharts or Chart.js (Visualization library)

### Backend Services
- **API Gateway**: Node.js + Express (or FastAPI)
- **Setup Chat Service**: Python + LangChain (Conversation management)
- **Analytics API**: Python + FastAPI (High-performance queries)
- **Filter Engine**: Python or Go (Real-time data transformation)

### AI/ML
- **LLM Provider**: OpenAI GPT-4 or Anthropic Claude (Setup & query agents)
- **Vector Database**: Pinecone or Weaviate (Query pattern matching)
- **Prompt Management**: LangChain or custom framework

### Data Infrastructure
- **Event Stream**: Kafka or Google Pub/Sub (Event ingestion)
- **Analytics Database**: ClickHouse (Fast time-series queries)
- **Config Database**: PostgreSQL (User settings, taxonomies, filters)
- **Cache**: Redis (Real-time aggregations)
- **Object Storage**: S3 (Raw event backup)

### Infrastructure
- **Cloud Platform**: AWS or GCP
- **Container Orchestration**: Docker + Kubernetes (or managed services)
- **Monitoring**: Prometheus + Grafana
- **Error Tracking**: Sentry

## MVP Feature Scope

### Phase 1: Core Setup & Tracking
- [ ] Chrome extension with conversational setup
- [ ] Setup AI agent (basic conversation flow)
- [ ] Data structure generation
- [ ] Tracking script SDK
- [ ] Event ingestion pipeline
- [ ] Basic filter engine
- [ ] PostgreSQL for configuration
- [ ] ClickHouse for analytics data

### Phase 2: Analytics & Visualization
- [ ] Web dashboard framework
- [ ] 3-5 pre-built dashboards (funnel, retention, engagement)
- [ ] Custom graph builder (line, bar, pie charts)
- [ ] Basic segmentation
- [ ] Date range filtering
- [ ] Export to CSV

### Phase 3: AI-Powered Insights
- [ ] Analytics chat interface
- [ ] Query generation agent
- [ ] Natural language to SQL
- [ ] Automatic visualization suggestions
- [ ] Basic anomaly detection
- [ ] Insight notifications

### Phase 4: Advanced Features (Post-MVP)
- [ ] Real-time event debugging
- [ ] A/B test analysis
- [ ] Cohort analysis
- [ ] Predictive analytics
- [ ] Data warehouse integrations
- [ ] Mobile SDK (iOS/Android)
- [ ] Team collaboration features

## Key Differentiators

| Feature | Heap | Mixpanel | BetterHeap |
|---------|------|----------|------------|
| **Setup Time** | 10 min (messy data) | Hours/days (manual) | 10 min (clean data) |
| **Data Quality** | Unstructured | Manual structuring | AI-structured |
| **Learning Curve** | Low (but messy) | High | Very low (AI-guided) |
| **Custom Queries** | Limited | Complex UI | Natural language chat |
| **Data Governance** | Weak | Manual | AI-enforced |
| **Price Point** | $$ | $$$ | $ |

## Success Metrics (MVP Goals)

**Setup Experience**:
- Average setup time: < 15 minutes
- Setup completion rate: > 85%
- User satisfaction with data structure: > 4.5/5

**Data Quality**:
- Event naming consistency: > 95%
- Schema validation pass rate: > 98%
- User-reported data issues: < 5%

**Analytics Usage**:
- Time to first insight: < 2 hours after installation
- Daily active users (of paying customers): > 60%
- AI chat queries per user per week: > 10

**Business Metrics**:
- Beta user acquisition: 50 companies in 3 months
- Conversion to paid: > 30%
- Customer satisfaction (NPS): > 50

---

## Future Vision

BetterHeap aims to become the **first truly conversational analytics platform** where setting up tracking and getting insights requires zero technical knowledge. Our long-term vision includes:

1. **Predictive Analytics**: AI proactively surfaces insights before you ask
2. **Cross-Platform Tracking**: Unified analytics across web, mobile, and backend
3. **Automated Experiments**: AI suggests and runs A/B tests automatically
4. **Data Warehouse Integration**: Sync with Snowflake, BigQuery for unified analytics
5. **Team Intelligence**: Learn from how your team queries data to improve suggestions
6. **Privacy-First**: Built-in compliance with GDPR, CCPA with AI-assisted configuration

## Getting Started

```bash
# Install dependencies
npm install

# Run development environment
docker-compose up -d

# Start frontend
cd frontend && npm run dev

# Start backend services
cd backend && python -m uvicorn main:app --reload

# Access:
# - Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

## Contributing

This is currently in private development. Contact the team for collaboration opportunities.

## License

Proprietary - All rights reserved

