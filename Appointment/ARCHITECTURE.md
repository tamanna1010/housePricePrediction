# CareFlow — System Architecture

This document describes the architecture of the **Agentic Medical Appointment Workflow** prototype. Diagrams use [Mermaid](https://mermaid.js.org/); they render on GitHub and in many IDEs.

---

## 1. High-level system context

```mermaid
flowchart TB
    subgraph Users
        OPS[Operations / Demo User]
        HUMAN[Human Concierge]
    end

    subgraph CareFlow["CareFlow Application (Render — single URL)"]
        UI[React Dashboard<br/>CareFlow UI]
        API[FastAPI REST API]
        subgraph Agents["Agent Layer"]
            ORCH[Orchestrator Agent]
            GRAPH[LangGraph Pipeline]
            STAGE[Stage Agents x6]
        end
        DB[(SQLite)]
    end

    subgraph External["External Services"]
        HF[Hugging Face<br/>Inference API]
    end

    OPS --> UI
    HUMAN --> UI
    UI --> API
    API --> ORCH
    API --> GRAPH
    ORCH --> HF
    STAGE --> HF
    GRAPH --> STAGE
    API --> DB
    ORCH --> DB
    GRAPH --> DB
```

---

## 2. Layered architecture

```mermaid
flowchart LR
    subgraph Presentation["Presentation Layer"]
        FE[React + Vite<br/>frontend/src/]
    end

    subgraph API["API Layer"]
        MAIN[main.py<br/>REST endpoints]
        SCHEMAS[schemas.py<br/>Pydantic models]
    end

    subgraph Services["Service Layer"]
        ORCH_SVC[orchestrator_service.py]
        WF_SVC[workflow_service.py]
        STG_SVC[stage_service.py]
        EXC_SVC[exception_service.py]
    end

    subgraph Agents["Agent Layer"]
        ORCH_A[orchestrator.py]
        GRAPH_A[graph.py]
        STAGE_A[stage_agent.py]
        LLM[llm.py]
    end

    subgraph Data["Data Layer"]
        MODELS[models.py]
        DB_FILE[(appointments.db)]
    end

    FE --> MAIN
    MAIN --> ORCH_SVC
    MAIN --> WF_SVC
    MAIN --> EXC_SVC
    MAIN --> STG_SVC
    ORCH_SVC --> ORCH_A
    WF_SVC --> GRAPH_A
    STG_SVC --> STAGE_A
    EXC_SVC --> WF_SVC
    ORCH_A --> LLM
    STAGE_A --> LLM
    GRAPH_A --> STG_SVC
    ORCH_SVC --> MODELS
    WF_SVC --> MODELS
    STG_SVC --> MODELS
    EXC_SVC --> MODELS
    MODELS --> DB_FILE
```

---

## 3. Deployment architecture (single URL)

```mermaid
flowchart TB
    USER[Browser] -->|HTTPS| RENDER[Render Web Service<br/>your-app.onrender.com]

    subgraph RENDER["Render Container"]
        UVICORN[uvicorn<br/>app.main:app]
        STATIC[frontend/dist<br/>served by FastAPI]
        API_ROUTES[/api routes at /<br/>health, appointments, etc./]
        UVICORN --> STATIC
        UVICORN --> API_ROUTES
        API_ROUTES --> SQLITE[(SQLite file<br/>ephemeral on free tier)]
    end

    API_ROUTES -.->|optional| HF[Hugging Face API]
```

**Build pipeline:** `scripts/build.sh` → `npm run build` (frontend) + `pip install` (backend) → start `uvicorn`.

---

## 4. Frontend component architecture

```mermaid
flowchart TB
    APP[App.jsx]
    HOOK[useWorkflow.js<br/>state + API calls]
    API_JS[api.js]

    APP --> HOOK
    HOOK --> API_JS

    APP --> HEADER[Header]
    APP --> STATS[StatsBar]
    APP --> FEED[AppointmentFeed]
    APP --> PIPE[StagePipeline]
    APP --> EXC[ExceptionQueue]
    APP --> TOAST[Toast]

    API_JS -->|fetch same origin| FASTAPI[FastAPI Backend]
```

| Panel | Component | Backend endpoints used |
|-------|-----------|-------------------------|
| Feed | `AppointmentFeed` | `GET /appointments` |
| Pipeline | `StagePipeline` | `GET /appointments/{id}`, `POST .../process` |
| Exceptions | `ExceptionQueue` | `GET /exceptions`, `POST .../resolve` |
| Header | `Header` | `POST /orchestrator/run`, `POST /seed` |

---

## 5. Backend API map

```mermaid
flowchart LR
    subgraph Endpoints["FastAPI (main.py)"]
        E1[GET /health]
        E2[GET /config]
        E3[GET /appointments]
        E4[POST /orchestrator/run]
        E5[POST /appointments/id/process]
        E6[GET /exceptions]
        E7[POST /exceptions/id/resolve]
        E8[POST /seed]
    end

    E4 --> OS[orchestrator_service]
    E5 --> WS[workflow_service]
    E7 --> ES[exception_service]
    E5 --> LG[pipeline_graph]
    OS --> OA[orchestrator agent]
    LG --> SS[stage_service]
    ES --> WS
```

---

## 6. Intelligent orchestrator flow

```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as FastAPI
    participant OS as orchestrator_service
    participant OA as orchestrator.py
    participant LLM as Hugging Face
    participant DB as SQLite

    UI->>API: POST /orchestrator/run
    API->>OS: run_orchestrator()
    OS->>DB: Load pending/cleared appointments
    OS->>OA: rank_appointments()
    OA->>LLM: Priority prompt (or fallback rules)
    LLM-->>OA: JSON rankings
    OA-->>OS: Sorted list + scores
    OS->>DB: Update priority_score
    OS->>API: process_appointment(top id)
    Note over API,DB: LangGraph pipeline (see §7)
    API-->>UI: rankings + processed result
```

---

## 7. LangGraph processing pipeline

```mermaid
stateDiagram-v2
    [*] --> RunStage: process_appointment()

    RunStage --> RunStage: complete, more stages remain
    RunStage --> Escalated: escalate
    RunStage --> Completed: all stages complete
    RunStage --> [*]: escalate → exception queue

    Escalated --> [*]
    Completed --> [*]

    note right of RunStage
        Each iteration calls
        run_single_stage() → stage_agent
    end note
```

```mermaid
flowchart TB
    subgraph Node["LangGraph node: run_stage"]
        A[Set stage = processing] --> B[stage_agent LLM]
        B --> C{state?}
        C -->|complete| D{more stages?}
        C -->|escalate| E[handle_escalation]
        D -->|yes| F[current_stage++]
        D -->|no| G[status = completed]
        E --> H[status = escalated<br/>insert exception]
        F --> Node
    end
```

**Stage names (configurable via `STAGE_COUNT`):**

1. Intake Validation  
2. Insurance Check  
3. Clinical Review  
4. Scheduling  
5. Provider Assignment  
6. Final Confirmation  

---

## 8. Stage agent decision flow

```mermaid
flowchart TD
    START[run_stage_agent] --> PROMPT[Build prompt<br/>patient, client, specialty, notes, stage]
    PROMPT --> LLM{HF API available?}
    LLM -->|yes| PARSE[Parse JSON<br/>complete or escalate]
    LLM -->|no / error| FALLBACK[Rule-based fallback]
    PARSE -->|valid| OUT[Return state + reason]
    PARSE -->|invalid| FALLBACK
    FALLBACK --> OUT
```

---

## 9. Human-in-the-loop (escalation & resume)

```mermaid
sequenceDiagram
    participant SA as Stage Agent
    participant LG as LangGraph
    participant DB as SQLite
    participant UI as Exception Queue UI
    participant H as Human Concierge
    participant EX as exception_service

    SA->>LG: escalate
    LG->>DB: status=escalated, exceptions row
    LG-->>UI: Show in Exception Queue

    H->>UI: Enter resolution note
    UI->>EX: POST /exceptions/{id}/resolve
    EX->>DB: resolved=true, status=cleared<br/>reset stage, append Human approved
    EX->>LG: process_appointment() resume
    LG->>SA: continue from cleared stage
    SA-->>UI: completed or escalate again
```

---

## 10. Data model

```mermaid
erDiagram
    APPOINTMENTS ||--o{ STAGE_RESULTS : has
    APPOINTMENTS ||--o{ EXCEPTIONS : may_have

    APPOINTMENTS {
        int id PK
        string patient_name
        string client
        string specialty
        string status
        int current_stage
        float priority_score
        text notes
    }

    STAGE_RESULTS {
        int id PK
        int appointment_id FK
        int stage_number
        string state
    }

    EXCEPTIONS {
        int id PK
        int appointment_id FK
        int stage_number
        text reason
        bool resolved
        text resolution_note
    }
```

**Appointment statuses:** `pending` → `in_progress` → `completed` | `escalated` → `cleared` → `in_progress` → …

**Stage states:** `not_started` | `processing` | `complete` | `escalate`

---

## 11. End-to-end request flows

### A. Run orchestrator (happy path)

```mermaid
flowchart LR
    A[UI: Run Orchestrator] --> B[POST /orchestrator/run]
    B --> C[Rank all pending cases]
    C --> D[Process highest priority]
    D --> E[LangGraph: stages 1..6]
    E --> F[UI: refresh feed + pipeline]
```

### B. Escalate → resolve → resume

```mermaid
flowchart LR
    A[UI: Process Eva Patel] --> B[Stage 2: escalate]
    B --> C[Exception Queue]
    C --> D[UI: Resolve and Resume]
    D --> E[status = cleared]
    E --> F[LangGraph resumes]
    F --> G[status = completed]
```

---

## 12. Repository structure (module map)

```
Appoinment-Management/
│
├── frontend/                    # Presentation
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── hooks/useWorkflow.js
│       └── components/          # Feed, Pipeline, ExceptionQueue, UI
│
├── backend/
│   └── app/
│       ├── main.py                # HTTP entry, mounts React dist
│       ├── static_files.py        # Single-URL static serving
│       ├── config.py              # STAGE_COUNT, env settings
│       ├── models.py              # SQLAlchemy entities
│       ├── database.py
│       ├── seed.py
│       ├── agents/
│       │   ├── llm.py             # HuggingFaceEndpoint wrapper
│       │   ├── orchestrator.py    # Master priority agent
│       │   ├── stage_agent.py     # Per-stage complete/escalate
│       │   └── graph.py           # LangGraph pipeline
│       └── services/
│           ├── orchestrator_service.py
│           ├── workflow_service.py
│           ├── stage_service.py
│           └── exception_service.py
│
├── scripts/build.sh             # Production build (Render)
└── render.yaml                  # Render Blueprint
```

---

## 13. Technology matrix

| Concern | Technology | Role |
|---------|------------|------|
| UI | React 18, Vite | Dashboard facade |
| API | FastAPI | REST + serve SPA |
| Persistence | SQLite, SQLAlchemy | Appointments, stages, exceptions |
| Orchestration | LangGraph | Sequential stage loop with branch on escalate |
| LLM integration | LangChain, langchain-huggingface | Prompt → JSON decisions |
| Inference | Hugging Face API | Optional; fallback rules if unavailable |
| Hosting | Render (free) | Single web service, one public URL |

---

## 14. Design principles (prototype)

| Principle | How it shows up |
|-----------|------------------|
| Facade over production | No auth, HIPAA, or real EHR integrations |
| Separation of concerns | Agents decide; services enforce DB/state |
| Human-in-the-loop as first-class | Exception queue + Cleared + auto-resume |
| Demo reliability | Rule-based fallbacks when LLM fails |
| Single deployable unit | FastAPI serves UI + API for interviews |

---

## Related docs

- [README.md](./README.md) — setup, demo script, deployment steps
