# IBM Bob Usage Statement

> **Project:** TicketSeed · **Team:** The Clique · **Tool:** IBM Bob 2.0
> **Submission:** lablab.ai Hackathon

---

## Developer Workflow Addressed

TicketSeed solves a high-friction sprint-planning workflow: translating a non-technical client PRD into an ordered sprint plan and developer-ready tickets with full source traceability. The entire development lifecycle — from data modelling and LLM integration to prompt engineering, deterministic validation, and React frontend construction — was built end-to-end inside Bob across four team roles (Backend, Prompts & Quality, Frontend, Delivery).

---

## IBM Bob 2.0 Features Utilized

**Plan Mode** was used to architect the two-capability API contract (`POST /api/plan/sprints`, `POST /api/plan/tickets`), design the Pydantic v2 data models in `backend/app/models.py`, and define the eight deterministic validation rules before a single line of code was written.

**Agent Mode** drove implementation: scaffolding the FastAPI app, writing the Groq-only LLM provider adapter (`providers/groq.py`), implementing the full validator suite in `validators.py` — including cycle detection, normalised source-quote matching, and coverage checks — and building the complete React + TypeScript + Tailwind frontend across five components (`InputView`, `SprintPlanView`, `TicketsView`, `ValidationPanel`, `Spinner`), the API client, and the Markdown/JSON export layer.

**AGENTS.md custom project rules** kept every session grounded: Bob read the single source of truth on startup, enforced that prompts lived as files (never inline strings), that the backend remained stateless, and that `models.py` was the contract between backend and frontend TypeScript types.

**Subagents** were used for focused codebase exploration — extracting git history, reading file trees, and summarising cross-file relationships — without polluting the main working context. The built-in **code review** was run before every merge, and Bob generated all **PR descriptions and commit messages** across seven pull requests.

**Features used at a glance:**

- Agent Mode
- Plan Mode
- Ask Mode
- AGENTS.md (Custom Project Rules)
- Subagents
- Multi-file Editing
- Code Review
- PR Descriptions & Commit Messages
- Todo Tracking

---

## Impact & Efficiency

The full backend — models, routes, validators, retry logic, and provider adapter — was completed in a single sprint with no rework on the core data contract. The frontend (~40 files, including all views, types, and export logic) was implemented in one Agent Mode session from a blank scaffold, replacing an estimated two days of manual work. Validator correctness was enforced structurally by Bob's multi-file awareness, catching a cross-file type inconsistency between `models.py` and `types.ts` before it reached integration. The watsonx provider was safely removed across five files in a single targeted edit after the team decided on Groq-only, with zero leftover references.

---

## Most Critical Touchpoints

Bob's assistance was most critical at three junctures:

1. **Designing `backend/app/models.py`** as the single schema source of truth that every other file depends on — frontend types, validators, routes, and fixtures all derive from it.
2. **Implementing `backend/app/validators.py`**, where eight correctness rules — including acyclic dependency checks and normalised PRD quote matching — needed to be precise and structurally sound.
3. **Building the entire React frontend** in a single coherent pass, ensuring TypeScript types mirrored the Pydantic models exactly and all API calls used relative paths compatible with both the Vite dev proxy and Vercel's production routing.

---
