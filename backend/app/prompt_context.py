"""
prompt_context.py — Cap 2 prompt trimming for Groq free-tier TPM.

Same rules as scripts/test_prompt.py historically used for Cap 2.
"""

from __future__ import annotations


def slim_plan_for_sprint(plan: dict, sprint_id: str) -> dict:
    """
    Keep only the target sprint, earlier sprints as stubs, and related requirements.
    Cuts Cap 2 prompt size so Groq free-tier ~8k TPM can accept the request.
    """
    sprints = plan.get("sprints") or []
    target = next((s for s in sprints if s.get("id") == sprint_id), None)
    if target is None:
        raise ValueError(f"Sprint id {sprint_id!r} not found in plan.")

    target_order = int(target.get("order", 0))
    kept_sprints: list[dict] = []
    for s in sprints:
        order = int(s.get("order", 0))
        if s.get("id") == sprint_id:
            kept_sprints.append(s)
        elif order < target_order:
            # Stub earlier sprints — enough context to avoid duplicating their work
            kept_sprints.append({
                "id": s.get("id"),
                "order": order,
                "name": s.get("name"),
                "goal": s.get("goal"),
                "requirement_ids": s.get("requirement_ids") or [],
                "deliverables": [],
                "depends_on": s.get("depends_on") or [],
                "rationale": "",
            })

    needed_req_ids = set(target.get("requirement_ids") or [])
    for s in kept_sprints:
        needed_req_ids.update(s.get("requirement_ids") or [])

    requirements = [
        r for r in (plan.get("requirements") or []) if r.get("id") in needed_req_ids
    ]

    return {
        "project": plan.get("project") or {},
        "requirements": requirements,
        "sprints": kept_sprints,
        "client_questions": [],
    }
