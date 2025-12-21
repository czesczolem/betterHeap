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


