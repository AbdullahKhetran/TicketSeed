# Local Development Quickstart

Get the backend and frontend running on your machine.

---

## Prerequisites

| Tool | Minimum version | Check |
|---|---|---|
| Python | 3.11 | `python --version` |
| Node.js | 18 | `node --version` |
| npm | 9 | `npm --version` |
| Git | any | `git --version` |

---

## 1 — Clone & enter the repo

```bash
git clone https://github.com/AbdullahKhetran/TicketSeed.git
cd TicketSeed
```

---

## 2 — Environment variables

Copy the example file and fill in your credentials:

```bash
# Mac/Linux
cp .env.example .env
# Windows
copy .env.example .env
```

Open `.env` and set:

```env
# Required — Groq API key (free, no card required)
LLM_PROVIDER=groq
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL_ID=openai/gpt-oss-120b
```

> **Never commit `.env`.** It is already in `.gitignore`.

**Where to get the Groq API key (free, takes 2 minutes):**
1. Go to **[console.groq.com](https://console.groq.com)** — sign up free, no card required
2. Click **"API Keys"** in the left sidebar
3. Click **"Create API Key"** → copy it into `GROQ_API_KEY`

---

## 3 — Backend

### 3a. Create a virtual environment

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3b. Install dependencies

```bash
pip install -r requirements.txt
```

### 3c. Start the FastAPI server

```bash
uvicorn backend.app.main:app --reload --port 8000
```

The API is now live at **http://localhost:8000**.

| Endpoint | Description |
|---|---|
| `GET  http://localhost:8000/api/health` | Liveness check — returns `{"status":"ok","provider":"groq"}` |
| `POST http://localhost:8000/api/plan/sprints` | PRD → sprint plan |
| `POST http://localhost:8000/api/plan/tickets` | Sprint → tickets |
| `GET  http://localhost:8000/docs` | Swagger UI (auto-generated) |

**Verify the backend is working:**

```bash
curl http://localhost:8000/api/health
# Expected: {"status":"ok","provider":"groq"}
```

---

## 4 — Frontend

> ⚠️ The `frontend/` directory does not exist yet — this section is ready for Person C to fill in once the scaffold is created. The steps below follow the expected Vite + React + Tailwind setup from the PRD.

### 4a. Install dependencies

```bash
cd frontend
npm install
```

### 4b. Start the Vite dev server

```bash
npm run dev
```

The frontend is now live at **http://localhost:5173**.

All `/api` requests from the browser are **automatically proxied** to `http://localhost:8000` by the Vite dev server — no CORS issues, no environment variable needed in the frontend.

---

## 5 — Running both at the same time

Open **two terminals** side by side:

**Terminal 1 — backend**
```bash
# From repo root, with .venv active
uvicorn backend.app.main:app --reload --port 8000
```

**Terminal 2 — frontend**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## 6 — Running the tests

```bash
# From repo root, with .venv active
pytest backend/tests/ -v
```

---

## 7 — Trying the API directly (no frontend)

Use the auto-generated Swagger UI at **http://localhost:8000/docs**, or curl:

```bash
# Capability 1 — PRD to sprint plan
curl -X POST http://localhost:8000/api/plan/sprints \
  -H "Content-Type: application/json" \
  -d '{"prd_markdown": "## My App\nUsers can sign up and log in."}'

# Capability 2 — sprint to tickets (replace S1 with the sprint id from the plan above)
curl -X POST http://localhost:8000/api/plan/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "prd_markdown": "## My App\nUsers can sign up and log in.",
    "plan": { ... },
    "sprint_id": "S1"
  }'
```

Sample PRDs are available in [`samples/`](../samples/) — use them as realistic test inputs.

### Sample PRD size (hackathon / free tier)

The three files in `samples/` (`prd-clean.md`, `prd-messy.md`, `prd-vague.md`) are **intentionally shortened** for the hackathon demo.

Groq’s free tier enforces a low tokens-per-minute (TPM) budget (~**8k** for our model). Capability 2 sends the PRD plus the sprint plan and schema in one request, so long client PRDs easily exceed that limit (`413` / rate limit). Shorter samples keep Cap 1 and Cap 2 runnable without raising TPM or upgrading the plan.

`scripts/test_prompt.py` Cap 2 also **slims the sprint plan** to the target sprint (plus stubs of earlier sprints) for the same reason.

In production you can accept longer PRDs (up to `MAX_PRD_CHARS`); these samples are demo fixtures, not a product limit.

---

## 8 — Common issues

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'backend'` | Run `uvicorn` from the repo root, not from inside `backend/` |
| `KeyError: 'GROQ_API_KEY'` | `.env` file is missing or the variable name is wrong — check against section 2 above |
| `401 Unauthorized` from Groq | API key is invalid or expired — regenerate it at [console.groq.com](https://console.groq.com) |
| `ValueError: LLM_PROVIDER is not set` | `LLM_PROVIDER` is missing from `.env` — add `LLM_PROVIDER=groq` |
| `413` / TPM rate limit from Groq | Request too large for free tier — use the shortened `samples/` PRDs; wait a minute and retry |
| `502` from `/api/plan/sprints` | The LLM returned invalid JSON twice. Check `uvicorn` logs for the raw response |
| Frontend shows blank page or CORS error | Make sure both servers are running and the Vite proxy is configured (`/api` → `localhost:8000`) |
| `pytest` not found | Virtual environment is not activated — run `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (macOS/Linux) |

