# Agentic Medical Appointment Workflow

A **prototype facade** for an Agentic Workflow Management System that processes medical appointments. Built for demonstrating architectural thinking, product design, and a human-in-the-loop workflow—not as a production-ready application.

## What This Project Does so

The system simulates how medical appointments move through an AI-orchestrated pipeline:

1. **Orchestrator** — A master agent reads appointments from a database and ranks them by dynamic priority (client, specialty, notes).
2. **Stage agents** — Each appointment passes through **6 configurable stages** (e.g. Intake, Insurance, Clinical Review). Each stage is an LLM-backed agent that returns a standardized outcome.
3. **Exception queue** — If a stage returns **Escalate**, the case goes to a human concierge.
4. **Human resolution** — A human resolves the issue; the appointment becomes **Cleared** and the workflow **resumes automatically**.

## Tech Stack

| Layer    | Technology                 |
| -------- | -------------------------- |
| Frontend | React, Vite                |
| Backend  | Python, FastAPI            |
| Database | SQLite                     |
| Agents   | LangChain, LangGraph       |
| LLM      | Hugging Face Inference API |

## Architecture

See **[ARCHITECTURE.md](./ARCHITECTURE.md)** for system diagrams (Mermaid): high-level context, layers, LangGraph pipeline, orchestrator, human-in-the-loop, data model, and deployment.

## Project Structure

```
Appoinment-Management/
├── backend/                 # FastAPI + agents + SQLite
│   ├── app/
│   │   ├── agents/          # LLM, orchestrator, stage agent, LangGraph
│   │   ├── services/        # Workflow, exceptions, orchestrator
│   │   ├── models.py        # DB models
│   │   └── main.py          # API routes
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # React UI (3 panels)
│   ├── src/
│   │   ├── App.jsx
│   │   └── api.js
│   └── package.json
└── README.md
```

## Prerequisites

- **Python 3.9+**
- **Node.js 18+** and **npm** (for the frontend)
- **Hugging Face API key** (optional — rule-based fallbacks work without it)

## Getting Started

### 1. Backend setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your HF_API_KEY (optional for demo)
```

**`.env` variables:**

| Variable       | Description                 | Default                              |
| -------------- | --------------------------- | ------------------------------------ |
| `DATABASE_URL` | SQLite connection string    | `sqlite:///./appointments.db`        |
| `STAGE_COUNT`  | Number of processing stages | `6`                                  |
| `HF_API_KEY`   | Hugging Face API token      | (empty = use fallback rules)         |
| `HF_MODEL_ID`  | Model on HF Inference API   | `mistralai/Mistral-7B-Instruct-v0.2` |

**Start the API server:**

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

On first startup, the database is created and **8 demo appointments** are seeded automatically.

### 2. Frontend setup

Open a **second terminal**:

```bash
cd frontend

npm install
npm run dev
```

- UI: http://localhost:5173

The dev server proxies `/api` requests to the backend on port 8000.

## Using the UI (CareFlow)

The **CareFlow** dashboard includes:

- **Stats bar** — Total cases, in progress, completed, escalated, exception queue count
- **Appointment Feed** — Priority-ranked cards with patient avatars
- **Agentic Pipeline** — Vertical timeline of 6 stages with status colors
- **Exception Queue** — Human concierge panel for escalated cases

**Header actions:**

| Button                        | Action                                                 |
| ----------------------------- | ------------------------------------------------------ |
| **Run Orchestrator**          | Rank appointments and process the highest-priority one |
| **Run Full Pipeline**         | Process the selected appointment through all stages    |
| **Resolve & Resume Workflow** | Clear an escalated case and auto-resume                |
| **Reset Demo**                | Reset database and re-seed sample data                 |
| **Refresh**                   | Reload data from the API                               |

### Frontend structure (modular)

```
frontend/src/
├── api.js
├── constants.js
├── hooks/useWorkflow.js      # State & API logic
├── components/
│   ├── ui/                   # Button, Badge, Panel, Toast, EmptyState
│   ├── layout/               # Header, StatsBar
│   ├── AppointmentFeed.jsx
│   ├── StagePipeline.jsx
│   └── ExceptionQueue.jsx
└── App.jsx
```

## Testing the UI (step-by-step)

### 1. Start both servers

**Terminal 1 — Backend:**

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 2. Verify the dashboard loads

- You should see the **CareFlow** header (teal branding)
- Stats bar shows **8** total cases (after auto-seed)
- Appointment feed lists patients; **Grace Chen** may appear in Exception Queue (pre-seeded)

### 3. Test orchestrator

1. Click **Reset Demo** → toast confirms reset; stats refresh
2. Click **Run Orchestrator** → priority bars update; top case processes
3. Select a processed appointment → pipeline timeline shows green **Complete** on finished stages

### 4. Test escalation (Eva Patel)

1. Click **Reset Demo**
2. Click **Eva Patel** in the feed (Neurology · Metro Health Plan)
3. Click **Run Full Pipeline**
4. Pipeline stops at **Insurance Check** with red **Escalate**
5. Stats bar **Exception Queue** count increases
6. Eva appears in the right panel with escalation reason

### 5. Test human-in-the-loop

1. In Exception Queue, type: `Prior auth approved by payer`
2. Click **Resolve & Resume Workflow**
3. Toast shows `Cleared & resumed → completed`
4. Eva disappears from queue; pipeline shows all stages **Complete**
5. Eva’s status badge → **Completed**

### 6. Test Grace Chen (pre-escalated)

1. **Reset Demo** — Grace is escalated at Clinical Review without running pipeline
2. Resolve with any note → workflow resumes and can complete

### 7. Quick API check (optional)

If UI actions fail, open http://localhost:8000/docs and test endpoints directly.

## Demo Walkthrough

1. Click **Reset Demo**.
2. Click **Run Orchestrator** — appointments are re-ranked; the top one is processed.
3. Select **Eva Patel** and click **Process** — she escalates at **Insurance Check** (prior auth in notes).
4. In **Exception Queue**, enter a note (e.g. `Prior auth approved`) and click **Resolve & Resume**.
5. The pipeline resumes; Eva’s appointment should reach **completed**.

Grace Chen is pre-seeded as escalated so the exception queue is never empty on a fresh start.

## API Endpoints (summary)

| Method | Endpoint                           | Description                       |
| ------ | ---------------------------------- | --------------------------------- |
| `GET`  | `/appointments`                    | List appointments (by priority)   |
| `GET`  | `/appointments/{id}`               | Single appointment + stage states |
| `POST` | `/appointments/{id}/process`       | Run full LangGraph pipeline       |
| `POST` | `/appointments/{id}/run-stage/{n}` | Run one stage (debug)             |
| `POST` | `/orchestrator/run`                | Rank feed and process top item    |
| `GET`  | `/exceptions`                      | List exception queue              |
| `POST` | `/exceptions/{id}/resolve`         | Human resolve → Cleared + resume  |
| `POST` | `/seed`                            | Reset demo data                   |
| `GET`  | `/config`                          | Stage count, names, valid states  |

## How Requirements Are Met

| Requirement                   | Implementation                                                    |
| ----------------------------- | ----------------------------------------------------------------- |
| Intelligent orchestrator      | `agents/orchestrator.py` + `POST /orchestrator/run`               |
| Agentic processing (6 stages) | `agents/stage_agent.py` + `agents/graph.py` (LangGraph)           |
| Standardized outputs          | `not_started`, `processing`, `complete`, `escalate` on each stage |
| Exception queue               | `exceptions` table + `GET /exceptions`                            |
| Human concierge               | `POST /exceptions/{id}/resolve` → `cleared` + pipeline resume     |

## Where the LLM Is Used

The LLM (Hugging Face via LangChain) is used only for **judgment calls**:

1. **Orchestrator** — Prioritize which appointment to process first.
2. **Stage agent** — Decide `complete` vs `escalate` per stage.

Workflow logic (state updates, escalation routing, resume after resolve) is handled in Python. If `HF_API_KEY` is missing or the API fails, **rule-based fallbacks** keep the demo working.

## Troubleshooting

| Issue                       | Fix                                                                  |
| --------------------------- | -------------------------------------------------------------------- |
| Port 8000 in use            | Stop the other process or use `--port 8001`                          |
| Frontend can't reach API    | Ensure backend is running on port 8000                               |
| `npm` not found             | Install Node.js from https://nodejs.org                              |
| LLM errors / slow responses | Leave `HF_API_KEY` empty to use fallbacks, or try a smaller HF model |

## Deploy on one URL (free — Render)

The app is configured so **FastAPI serves the React build** from the same origin. One public URL serves both UI and API.

### Architecture

```
https://your-app.onrender.com/
├── /                    → CareFlow UI (React)
├── /appointments        → API
├── /orchestrator/run    → API
└── /exceptions          → API
```

### Step 1 — Push to GitHub

```bash
cd Appoinment-Management
git init
git add .
git commit -m "CareFlow agentic appointment workflow"
# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

Do **not** commit `backend/.env` (secrets). `.env.example` is safe to commit.

### Step 2 — Create Render account

1. Go to [https://render.com](https://render.com) and sign up (free).
2. Connect your GitHub account.

### Step 3 — Deploy from Blueprint

**Option A — Using `render.yaml` (recommended)**

1. Dashboard → **New** → **Blueprint**
2. Select your repository
3. Render reads `render.yaml` at the repo root
4. Click **Apply**

**Option B — Manual web service**

1. **New** → **Web Service** → connect repo
2. Settings:
   - **Build command:** `bash scripts/build.sh`
   - **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root directory:** leave blank (repo root)

### Step 4 — Environment variables (Render dashboard)

In your service → **Environment**:

| Key            | Value                                |
| -------------- | ------------------------------------ |
| `HF_API_KEY`   | Your Hugging Face token (optional)   |
| `HF_MODEL_ID`  | `mistralai/Mistral-7B-Instruct-v0.2` |
| `STAGE_COUNT`  | `6`                                  |
| `DATABASE_URL` | `sqlite:///./appointments.db`        |

Render also sets `PYTHON_VERSION` / `NODE_VERSION` from `render.yaml`.

### Step 5 — Deploy and test

1. Wait for the build (5–10 min first time).
2. Open `https://YOUR-SERVICE.onrender.com` — you should see **CareFlow**.
3. Test: **Reset Demo** → **Run Orchestrator** → Eva escalate → **Resolve**.

API docs (same host): `https://YOUR-SERVICE.onrender.com/docs`

### Step 6 — Before your interview

- Open the URL **once** 1–2 minutes early (free tier **cold start** ~30–60s after sleep).
- SQLite on free Render is **ephemeral** — data may reset on redeploy; use **Reset Demo** as needed.

### Test single-URL locally (optional)

```bash
bash scripts/build.sh
cd backend && source venv/bin/activate
uvicorn app.main:app --port 8000
# Open http://localhost:8000 (UI + API together)
```

## License

Prototype for interview / demonstration purposes.
