# Project Checklist — TicketSeed

> Status key: ✅ Done · ⬜ Remaining · 🔲 Blocked (needs something else first)
>
> Last updated: 2026-09-27 (after Cap 2 prompt slim + live check of all three sample PRDs).  
> Cross-reference with [`docs/PRD-ticketseed.md`](PRD-ticketseed.md) §15.2.
>
> LLM: **Groq only** (`LLM_PROVIDER=groq`). No watsonx / OpenAI / Anthropic adapters.

---

## Person A — Backend (Abdullah)

### Models & core structure
- [x] `backend/app/models.py` — all Pydantic v2 models matching PRD §7 (SprintPlan, TicketList, enums, API envelopes)
- [x] `backend/app/__init__.py` created
- [x] `backend/app/providers/base.py` — `LLMProvider` Protocol
- [x] `backend/app/providers/__init__.py`
- [x] `backend/app/providers/groq.py` — Groq provider adapter (only provider)
- [x] watsonx provider removed — project is Groq-only
- [x] `reasoning_effort: "low"` on Groq calls — free-tier TPM friendly (gpt-oss otherwise burns budget on reasoning)

### API & application
- [x] `backend/app/main.py` — FastAPI app, CORS middleware, router mounted at `/api`
- [x] `backend/app/routes.py` — `GET /api/health`, `POST /api/plan/sprints`, `POST /api/plan/tickets`
- [x] Input validation — 400 on empty PRD, 400 on PRD over 30 000 chars
- [x] LLM retry logic — retry once on bad JSON / schema mismatch, return 502 after second failure
- [x] Prompt files loaded from `backend/prompts/` (not inlined as strings)
- [x] Cap 2 prompt slim — `slim_plan_for_sprint` + compact JSON (same as `scripts/test_prompt.py` harness; avoids Groq free-tier 413)
- [x] `backend/scripts/test_llm.py` — Groq connectivity smoke test
- [x] `backend/scripts/test_endpoint.py` — local endpoint smoke test

### Validators
- [x] `backend/app/validators.py` — `validate_sprint_plan()` (Capability 1, all 4 rules)
- [x] `backend/app/validators.py` — `validate_ticket_list()` (Capability 2, all 5 rules)
- [x] Cycle-detection helper `_has_cycle()`
- [x] Normalised quote matching `_normalise()`

### Tests
- [x] `backend/tests/test_validators.py` — pytest suite covering Capability 1 validation rules
- [x] `backend/tests/test_validators.py` — pytest suite covering Capability 2 validation rules
- [x] `backend/tests/test_routes.py` — route-level tests (happy path + error cases + Cap 2 slim prompt)
- [x] `backend/tests/test_prompt_context.py` — Cap 2 plan-slimming helper
- [x] All tests passing (`pytest backend/tests/` — 38 passed)

### Remaining / in-progress
- [ ] Notify Person C whenever `models.py` changes (ongoing contract per PRD §15.3)
- [x] Error handling review — confirm 400 and 502 responses match PRD §9 spec exactly
- [x] Code frozen (Sunday midday) — freeze after pytest + Cap 2 TPM prompt slim bugfix
- [x] Bob sessions — 4 screenshots in `bob_sessions/abdullah/` (meets ≥3 requirement)

---

## Person B — Prompts & Quality (Sergiu)

### Fixtures (prerequisite for Person C)
- [x] `samples/fixtures/sprint-plan.example.json` — hand-written, passes Pydantic models
- [x] `samples/fixtures/tickets.example.json` — hand-written, passes Pydantic models

### Sample PRDs
- [x] `samples/prd-clean.md` — well-written, unambiguous sample (shortened for Groq ~8k TPM)
- [x] `samples/prd-messy.md` — realistic messy client PRD (shortened for Groq ~8k TPM)
- [x] `samples/prd-vague.md` — vague PRD that should generate client questions (shortened for Groq ~8k TPM)

### Prompts
- [x] `backend/prompts/prd_to_sprints.md` — system + user template for Capability 1
- [x] `backend/prompts/sprint_to_tickets.md` — system + user template for Capability 2
- [x] `scripts/test_prompt.py` — direct Groq prompt test harness (Cap 1 + Cap 2; shares `slim_plan_for_sprint` with the API)

### Quality & metrics
- [x] Run all three sample PRDs through `POST /api/plan/sprints` and check validator output (`prd-clean`, `prd-messy`, `prd-vague` — live frontend / Groq)
- [x] Run all three sample PRDs through `POST /api/plan/tickets` (at least one sprint per sample — live after Cap 2 prompt slim)
- [ ] Tune `prd_to_sprints.md` until validator warnings are rare
- [ ] Tune `sprint_to_tickets.md` until validator warnings are rare
- [x] `docs/metrics.md` — template scaffolded
- [ ] `docs/metrics.md` — fill numbers from PRD §18:
  - [ ] Traceability % (source quotes verified) — target > 95 %
  - [ ] Coverage % (requirements → sprints, sprint requirements → tickets) — target 100 %
  - [ ] Client questions count per sample (especially `prd-vague.md`)
  - [ ] Time comparison (automated vs manual ticket writing)

### Bob evidence
- [x] `bob_sessions/sergiu/the_clique_personB_01_prompts_and_fixtures.png`
- [ ] At least 2 more Bob session screenshots in `bob_sessions/sergiu/`

---

## Person C — Frontend (merged PR #6 — `frontend/initial-implementation`)

### Scaffold & types
- [x] Vite + React + TypeScript + Tailwind CSS project in `frontend/`
- [x] TypeScript types mirroring `backend/app/models.py` exactly (`frontend/src/types.ts`)
- [x] Vite dev-server proxy configured: `/api` → `http://localhost:8000`

### Upload view (Capability 1 — input)
- [x] PRD text area or file-upload input (paste + drag/drop `.md`)
- [x] Markdown preview of the uploaded PRD (`react-markdown`)
- [x] "Generate sprint plan" button with loading state
- [x] Error display for API failures (400 / 502 messages from backend)

### Sprint plan view (Capability 1 — output)
- [x] Sprint cards rendered in dependency order (`order`)
- [x] Requirements listed per sprint with `source_quote` shown
- [x] Client questions panel with "Copy all" button
- [x] Validation panel showing `ValidationReport` issues (warnings and errors)
- [x] Editable sprint **name** and **goal** (inline edit)
- [ ] Editable **requirement assignment** (move requirements between sprints) — PRD §10 gap

### Tickets view (Capability 2 — output)
- [x] Per-sprint generate from plan view (one sprint at a time, not all at once)
- [x] "Generate tickets" button with loading state
- [x] Ticket cards showing title, type, size, priority, acceptance criteria
- [x] Link from ticket back to `requirement_ids` → `source_quote`
- [x] Editable ticket fields (inline edit)
- [x] `needs_clarification` / `clarification_note` highlighted; flagged tickets sorted first
- [x] "Regenerate" for the active sprint

### Export & finishing
- [x] Export Markdown (plan + generated tickets) from plan and tickets views
- [x] Export JSON (plan + tickets + validation) from plan and tickets views

### API integration
- [x] All calls use relative `/api/...` paths (no hardcoded host)
- [x] Connected to real backend (`/api/plan/sprints`, `/api/plan/tickets`)

### Remaining / Bob evidence
- [ ] Requirement ↔ sprint reassignment UI (optional polish if time)
- [ ] At least 3 Bob session screenshots in `bob_sessions/ali/` or `bob_sessions/najmi/`
- [ ] UI freeze except bug fixes (Sunday midday)

---

## Person D — Delivery (TBA / Ali / Najmi)

### Repository setup
- [x] Repository created with this PRD committed
- [x] `AGENTS.md` in place
- [x] `docs/QUICKSTART.md` — local setup guide (Groq)
- [x] `requirements.txt` — all Python dependencies listed
- [x] `.env.example` — variable names only, no secrets (`GROQ_API_KEY`, `GROQ_MODEL_ID`, `LLM_PROVIDER`, `MAX_PRD_CHARS`)
- [ ] `README.md` — project description, local setup, env variables, how to run

### Vercel deployment
- [ ] Vercel project connected to the repo
- [ ] `vercel.json` — routes `POST /api/*` to the Python function, everything else to the frontend
- [ ] `api/index.py` — Vercel entry point importing the FastAPI `app`
- [ ] Fluid compute enabled, `maxDuration` set explicitly in `vercel.json`
- [ ] Hello-world deploy live (placeholder frontend + `/api/health` responding)
- [ ] LLM API key set as a Vercel environment variable (not committed)
- [ ] One real LLM call confirmed on the **deployed URL** (not only locally)
- [ ] Full app deployed and reachable at the production Application URL

### Bob skills (optional, PRD §12.3)
- [ ] `.bob/skills/` — skill file(s) created if time allows

### Bob session evidence collection
- [ ] Collect screenshots from all team members into `bob_sessions/`
  - [x] `bob_sessions/abdullah/` — 4 screenshots present
  - [x] `bob_sessions/sergiu/` — 1 screenshot present
  - [ ] `bob_sessions/ali/` — needs ≥ 3 screenshots
  - [ ] `bob_sessions/najmi/` — needs ≥ 3 screenshots

### Submission materials
- [x] `docs/metrics.md` template available (numbers still empty — Person B)
- [ ] Problem & Solution Statement — 500 words or fewer
- [ ] IBM Bob Usage Statement — 500 words or fewer
- [ ] Cover image
- [ ] Demo script drafted (following PRD §17 structure)
- [ ] Video demo recorded — ≤ 3 min, ≥ 90 s of product in action
- [ ] Backup video take recorded
- [ ] Slide presentation prepared
- [ ] Submission assembled on the lablab platform

---

## Submission Checklist (PRD §20 — whole team)

- [ ] Public code repository link
- [ ] `bob_sessions/` with task session screenshots from **every** team member (A, B, C, D)
- [ ] Problem and Solution Statement (≤ 500 words)
- [ ] IBM Bob Usage Statement (≤ 500 words)
- [ ] Cover image
- [ ] Video demo (≤ 3 min, ≥ 90 s of product in action)
- [ ] Slide presentation
- [ ] Application URL (Vercel production URL) + demo platform
- [ ] Technology and category tags filled in

---

## Quick status summary

| Area | Owner | Status |
|---|---|---|
| Pydantic models | A | ✅ Complete |
| LLM provider adapter (Groq only) | A | ✅ Complete |
| FastAPI app + routes | A | ✅ Complete |
| Validators (Cap 1 + Cap 2) | A | ✅ Complete |
| Groq TPM fixes (`reasoning_effort`, smoke scripts) | A | ✅ Complete |
| Bob sessions (Abdullah) | A | ✅ Complete (4) |
| Validator / route / prompt-context pytest | A | ✅ Complete (38 passed) |
| Error-handling review + code freeze | A | ✅ Complete |
| Cap 2 prompt slim (shared with harness) | A | ✅ Complete (`backend/slim-cap2-prompt`) |
| Prompts (both) + sample PRDs + fixtures | B | ✅ Complete |
| Prompt test harness (Cap 1 + Cap 2) | B / A | ✅ Complete (shared slim helper) |
| Live Cap 1 + Cap 2 on all three samples | A / B | ✅ Complete (clean, messy, vague) |
| Prompt tuning + metrics numbers | B | ⬜ Remaining (runs done; tune + fill metrics) |
| Frontend scaffold + types + proxy | C | ✅ Complete (PR #6) |
| Upload / plan / tickets views + export + real API | C | ✅ Complete |
| Requirement reassignment between sprints | C | ⬜ Remaining (PRD gap) |
| Bob sessions (Ali / Najmi) | C | ⬜ Remaining |
| `.env.example` + `requirements.txt` + QUICKSTART | D | ✅ Complete |
| README | D | ⬜ Remaining |
| Vercel deployment (`api/index.py` + `vercel.json`) | D | ⬜ Not started |
| Submission materials | D | ⬜ Remaining |
