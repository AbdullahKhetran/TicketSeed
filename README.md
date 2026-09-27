# TicketSeed

Paste a client's non-technical PRD (Markdown), get a sprint plan, then turn any sprint into developer-ready tickets.

Built for the IBM Bob 2.0 Hackathon (Sep 25–27, 2026).

---

## What it does 

TicketSeed has two capabilities:

1. **PRD → Sprint plan** — Submit a Markdown PRD. The app extracts requirements (each with a verbatim source quote from the document), organises them into ordered sprints, and produces a list of questions to send back to the client for anything left ambiguous.

2. **Sprint → Tickets** — Pick one sprint from the plan and generate its developer tickets. Each ticket has a title, type, description, acceptance criteria, size estimate, priority, and a reference back to the requirements it covers.

Every LLM response is validated by plain code before it reaches the frontend. If a source quote cannot be found in the original PRD, it is flagged. If a ticket has no traceable requirement, it is flagged.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| LLM provider | Groq (`GROQ_API_KEY`) |
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS |
| Hosting | Vercel (frontend on CDN, backend as a Python Function) |

---

## Repository layout

```
ticketseed/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── models.py        # Pydantic v2 models (source of truth for all data shapes)
│   │   ├── validators.py    # post-LLM validation (plain code)
│   │   ├── routes.py        # API route handlers
│   │   └── providers/
│   │       └── groq.py      # Groq LLM adapter
│   ├── prompts/
│   │   ├── prd_to_sprints.md
│   │   └── sprint_to_tickets.md
│   └── tests/
├── frontend/
│   └── src/                 # React + TypeScript UI
├── api/
│   └── index.py             # Vercel entry point
├── samples/                 # sample PRDs and fixture JSON
├── docs/
│   └── PRD-ticketseed.md    # full project spec
├── requirements.txt
└── .env.example
```

---

## API

### `POST /api/plan/sprints`

Converts a PRD into a sprint plan.

**Request**
```json
{ "prd_markdown": "..." }
```

**Response**
```json
{
  "plan": {
    "project": { "name": "...", "summary": "...", "assumptions": [] },
    "requirements": [ { "id": "R1", "text": "...", "source_quote": "...", "kind": "functional" } ],
    "sprints": [ { "id": "S1", "order": 1, "name": "...", "goal": "...", "requirement_ids": ["R1"], "deliverables": [], "depends_on": [], "rationale": "..." } ],
    "client_questions": [ { "id": "Q1", "question": "...", "why_it_matters": "...", "requirement_ids": ["R1"] } ]
  },
  "validation": { "ok": true, "issues": [] }
}
```

---

### `POST /api/plan/tickets`

Generates tickets for a single sprint.

**Request**
```json
{ "prd_markdown": "...", "plan": { ... }, "sprint_id": "S1" }
```

**Response**
```json
{
  "tickets": {
    "sprint_id": "S1",
    "tickets": [
      {
        "id": "S1-T1",
        "title": "...",
        "type": "feature",
        "description": "...",
        "acceptance_criteria": [],
        "technical_notes": "...",
        "areas": [],
        "size": "M",
        "priority": "high",
        "depends_on": [],
        "requirement_ids": ["R1"],
        "needs_clarification": false,
        "clarification_note": null
      }
    ]
  },
  "validation": { "ok": true, "issues": [] }
}
```

---

### `GET /api/health`

Returns `{ "status": "ok", "provider": "groq" }`. No secrets exposed.

---

### Error responses

| Code | Meaning |
|---|---|
| `400` | Empty PRD or PRD exceeds the length limit (~30,000 characters) |
| `502` | LLM returned invalid JSON after one retry |

---

## Running locally

### Backend

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set required environment variables
cp .env.example .env
# Edit .env — set GROQ_API_KEY and optionally GROQ_MODEL_ID

# 4. Start the API server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies `/api` requests to the backend on port 8000.

### Tests

```bash
pytest backend/tests/
```

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key |
| `GROQ_MODEL_ID` | No | Model to use (default: `openai/gpt-oss-120b`) |
| `LLM_PROVIDER` | No | Provider name (only `groq` is supported) |

---

## Validation rules

After every LLM call the backend checks (and flags, not drops):

**Sprint plan**
- Every `source_quote` exists verbatim (normalised) in the submitted PRD
- Every requirement is assigned to at least one sprint
- All `requirement_ids` in sprints and questions reference real requirements
- Sprint `depends_on` is acyclic

**Tickets**
- Every ticket's `requirement_ids` belong to the chosen sprint
- Every sprint requirement is covered by at least one ticket
- Ticket IDs are unique; `depends_on` is acyclic within the sprint
- Any ticket sized `XL` is automatically marked `needs_clarification`

---

## Deployment

The project deploys as a single Vercel project. The frontend is served from the CDN; the backend runs as a Python Serverless Function via `api/index.py`. Both share the same domain, so no CORS configuration is needed in production.

---

## Team

| Person | Role |
|---|---|
| Abdullah | Backend |
| Sergiu | Prompts & quality |
| TBA | Frontend |
| TBA | Delivery / infrastructure |
