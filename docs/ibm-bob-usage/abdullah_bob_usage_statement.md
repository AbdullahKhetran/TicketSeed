**IBM Bob Usage Statement — TicketSeed**

Our team used IBM Bob as the primary development assistant throughout the entire project, covering every layer of the stack.

---

**Backend — Abdullah (Person A)**

- Started a Bob **Agent mode** task pointed at `AGENTS.md` and `docs/PRD-ticketseed.md` to scaffold the backend from scratch. Bob authored `backend/app/models.py` (Pydantic v2 data models), `routes.py`, `validators.py`, and the Groq LLM provider adapter — the first deliverable the whole team was unblocked on.
- Used Bob to **diagnose and fix a Windows venv/uvicorn startup error** (`pip` and `uvicorn` executables not found in the relocated `.venv`), resolving it in a single short session (3% context, 19.31 Bobcoins — the most expensive single fix in the project).
- Ran Bob's built-in **Create Pull Request workflow** twice to generate PR descriptions from git diffs and open PRs on GitHub.
- Used Bob as a **PR Reviewer** — fed it an open branch-to-main PR and asked it to review and merge if clear; it read the diff, validated it against the spec, and confirmed the merge.

---

**Prompts & Fixtures — Sergiu (Person B)**

- Opened a Bob task with the PRD attached and asked Bob to understand the full scope of Person B's work. Bob generated an **8-item todo list** and completed all items in one session: `samples/prd-clean.md`, `prd-vague.md`, `prd-messy.md`, both fixture JSON files (`sprint-plan.example.json`, `tickets.example.json`), both LLM prompt files (`backend/prompts/prd_to_sprints.md`, `sprint_to_tickets.md`), and a `docs/metrics.md` template.
- Ran the **Create Pull Request workflow** to branch, write the PR description, and raise the PR for the `prompts/person-b-initial-deliverables` branch — 4-step todo list, all completed.

---

**Frontend — Najmi (Person C)**

- Gave Bob a single focused instruction: *"implement the frontend, do nothing else right now"*. Bob read the existing backend models and API contract, then implemented the full React + TypeScript + Vite + Tailwind CSS frontend in `frontend/src/` — including the two-capability UI, loading states, `react-markdown` rendering, and relative `/api/…` calls matching the backend contract.
- Session ran to **10/10 todos completed** with a PR opened, consuming ~68k tokens (25% of the 270k context window).

---

**Delivery — Abdullah (Person D role)**

- Used Bob to author `api/index.py` (Vercel entry point), `vercel.json` (Vite as primary framework, FastAPI as Python function, `maxDuration` set), and to iterate on dependency install issues that caused Vercel build failures.
- Used Bob to **document the production URL** and mark the deployment checklist complete, committed on the `delivery/docs-production-status` branch.

---

**Summary of Bob modes and features used**

| Feature | Used by |
|---|---|
| Agent mode (code generation) | Abdullah, Najmi |
| Agent mode (content / file generation) | Sergiu |
| Agent mode (debugging) | Abdullah |
| Create Pull Request workflow | Abdullah, Sergiu |
| PR Review task | Abdullah |
| Plan mode (architecture decisions) | Abdullah |
| `AGENTS.md` project rules (loaded every session) | All |
| Todo list tracking across multi-step tasks | All |