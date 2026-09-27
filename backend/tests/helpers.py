"""Minimal valid models for validator and route tests. No LLM calls."""

from backend.app.models import (
    ClientQuestion,
    Project,
    Requirement,
    RequirementKind,
    Sprint,
    SprintPlan,
    Ticket,
    TicketArea,
    TicketList,
    TicketPriority,
    TicketSize,
    TicketType,
)

PRD = "Customers should be able to order online and pay."


def requirement(
    req_id: str = "R1",
    source_quote: str = "order online",
    **overrides,
) -> Requirement:
    data = {
        "id": req_id,
        "text": "Customers can place an order.",
        "source_quote": source_quote,
        "kind": RequirementKind.functional,
    }
    data.update(overrides)
    return Requirement(**data)


def sprint(
    sprint_id: str = "S1",
    order: int = 1,
    requirement_ids: list[str] | None = None,
    depends_on: list[str] | None = None,
    **overrides,
) -> Sprint:
    data = {
        "id": sprint_id,
        "order": order,
        "name": "Foundations",
        "goal": "Ship the ordering base.",
        "requirement_ids": ["R1"] if requirement_ids is None else requirement_ids,
        "deliverables": ["API"],
        "depends_on": [] if depends_on is None else depends_on,
        "rationale": "Foundations come first.",
    }
    data.update(overrides)
    return Sprint(**data)


def question(
    question_id: str = "Q1",
    requirement_ids: list[str] | None = None,
) -> ClientQuestion:
    return ClientQuestion(
        id=question_id,
        question="Which payment provider should we use?",
        why_it_matters="The answer changes the integration work.",
        requirement_ids=[] if requirement_ids is None else requirement_ids,
    )


def plan(
    requirements: list[Requirement] | None = None,
    sprints: list[Sprint] | None = None,
    client_questions: list[ClientQuestion] | None = None,
) -> SprintPlan:
    return SprintPlan(
        project=Project(name="Shop", summary="An online shop.", assumptions=[]),
        requirements=[requirement()] if requirements is None else requirements,
        sprints=[sprint()] if sprints is None else sprints,
        client_questions=[] if client_questions is None else client_questions,
    )


def ticket(
    ticket_id: str = "S1-T1",
    requirement_ids: list[str] | None = None,
    depends_on: list[str] | None = None,
    size: TicketSize = TicketSize.S,
    needs_clarification: bool = False,
    **overrides,
) -> Ticket:
    data = {
        "id": ticket_id,
        "title": "Build order endpoint",
        "type": TicketType.feature,
        "description": "Create the order API.",
        "acceptance_criteria": ["POST /orders returns 201"],
        "technical_notes": "",
        "areas": [TicketArea.backend],
        "size": size,
        "priority": TicketPriority.high,
        "depends_on": [] if depends_on is None else depends_on,
        "requirement_ids": ["R1"] if requirement_ids is None else requirement_ids,
        "needs_clarification": needs_clarification,
        "clarification_note": None,
    }
    data.update(overrides)
    return Ticket(**data)


def ticket_list(
    sprint_id: str = "S1",
    tickets: list[Ticket] | None = None,
) -> TicketList:
    return TicketList(
        sprint_id=sprint_id,
        tickets=[ticket()] if tickets is None else tickets,
    )
