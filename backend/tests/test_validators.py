"""Capability 1 and 2 validator rules. No LLM calls."""

from backend.app.models import IssueSeverity, Ticket, TicketList, TicketSize
from backend.app.validators import validate_sprint_plan, validate_ticket_list
from backend.tests.helpers import PRD, plan, question, requirement, sprint, ticket, ticket_list


def _errors(report):
    return [issue for issue in report.issues if issue.severity == IssueSeverity.error]


def _warnings(report):
    return [issue for issue in report.issues if issue.severity == IssueSeverity.warning]


# ---------------------------------------------------------------------------
# Capability 1
# ---------------------------------------------------------------------------


def test_clean_plan_is_ok():
    report = validate_sprint_plan(plan(), PRD)
    assert report.ok is True
    assert report.issues == []


def test_quote_match_is_normalised():
    messy = plan(requirements=[requirement(source_quote="  ORDER, online! ")])
    report = validate_sprint_plan(messy, PRD)
    assert report.ok is True
    assert report.issues == []


def test_invented_quote_is_a_warning():
    invented = plan(requirements=[requirement(source_quote="teleport the inventory")])
    report = validate_sprint_plan(invented, PRD)
    warnings = _warnings(report)
    assert report.ok is True
    assert len(warnings) == 1
    assert warnings[0].target == "R1"


def test_uncovered_requirement_is_a_warning():
    uncovered = plan(
        requirements=[
            requirement("R1"),
            requirement("R2", source_quote="and pay"),
        ],
        sprints=[sprint(requirement_ids=["R1"])],
    )
    report = validate_sprint_plan(uncovered, PRD)
    warnings = _warnings(report)
    assert report.ok is True
    assert len(warnings) == 1
    assert warnings[0].target == "R2"


def test_sprint_unknown_requirement_is_an_error():
    bad = plan(sprints=[sprint(requirement_ids=["R1", "R99"])])
    report = validate_sprint_plan(bad, PRD)
    errors = _errors(report)
    assert report.ok is False
    assert len(errors) == 1
    assert errors[0].target == "S1"


def test_question_unknown_requirement_is_an_error():
    bad = plan(client_questions=[question(requirement_ids=["R99"])])
    report = validate_sprint_plan(bad, PRD)
    errors = _errors(report)
    assert report.ok is False
    assert len(errors) == 1
    assert errors[0].target == "Q1"


def test_depends_on_unknown_sprint_is_an_error():
    bad = plan(sprints=[sprint(depends_on=["S9"])])
    report = validate_sprint_plan(bad, PRD)
    errors = _errors(report)
    assert report.ok is False
    assert any(issue.target == "S1" for issue in errors)


def test_depends_on_higher_order_is_an_error():
    bad = plan(
        sprints=[
            sprint("S1", order=1, depends_on=["S2"]),
            sprint("S2", order=2, requirement_ids=[]),
        ]
    )
    report = validate_sprint_plan(bad, PRD)
    assert report.ok is False
    assert any(issue.target == "S1" and issue.severity == IssueSeverity.error for issue in report.issues)


def test_depends_on_equal_order_is_an_error():
    bad = plan(
        sprints=[
            sprint("S1", order=1),
            sprint("S2", order=1, requirement_ids=[], depends_on=["S1"]),
        ]
    )
    report = validate_sprint_plan(bad, PRD)
    assert report.ok is False
    assert any(issue.target == "S2" and issue.severity == IssueSeverity.error for issue in report.issues)


def test_sprint_dependency_cycle_is_an_error():
    bad = plan(
        sprints=[
            sprint("S1", order=1, depends_on=["S2"]),
            sprint("S2", order=2, requirement_ids=[], depends_on=["S1"]),
        ]
    )
    report = validate_sprint_plan(bad, PRD)
    errors = _errors(report)
    assert report.ok is False
    assert any(issue.target == "sprints" for issue in errors)


# ---------------------------------------------------------------------------
# Capability 2
# ---------------------------------------------------------------------------


def test_tickets_covering_sprint_are_ok():
    report = validate_ticket_list(ticket_list(), plan())
    assert report.ok is True
    assert report.issues == []


def test_ticket_requirement_outside_sprint_is_an_error():
    sprint_plan = plan(
        requirements=[
            requirement("R1"),
            requirement("R2", source_quote="and pay"),
        ],
        sprints=[
            sprint("S1", order=1, requirement_ids=["R1"]),
            sprint("S2", order=2, requirement_ids=["R2"]),
        ],
    )
    tickets = ticket_list(
        tickets=[ticket(requirement_ids=["R1", "R2"])],
    )
    report = validate_ticket_list(tickets, sprint_plan)
    errors = _errors(report)
    assert report.ok is False
    assert len(errors) == 1
    assert errors[0].target == "S1-T1"


def test_uncovered_sprint_requirement_is_a_warning():
    sprint_plan = plan(
        requirements=[
            requirement("R1"),
            requirement("R2", source_quote="and pay"),
        ],
        sprints=[sprint(requirement_ids=["R1", "R2"])],
    )
    report = validate_ticket_list(ticket_list(), sprint_plan)
    warnings = _warnings(report)
    assert report.ok is True
    assert len(warnings) == 1
    assert warnings[0].target == "R2"


def test_duplicate_ticket_id_is_an_error():
    tickets = ticket_list(
        tickets=[
            ticket("S1-T1"),
            ticket("S1-T1", title="Duplicate order endpoint"),
        ]
    )
    report = validate_ticket_list(tickets, plan())
    errors = _errors(report)
    assert report.ok is False
    assert any(issue.target == "S1-T1" for issue in errors)


def test_depends_on_unknown_ticket_is_an_error():
    tickets = ticket_list(tickets=[ticket(depends_on=["S1-T9"])])
    report = validate_ticket_list(tickets, plan())
    errors = _errors(report)
    assert report.ok is False
    assert len(errors) == 1
    assert errors[0].target == "S1-T1"


def test_ticket_dependency_cycle_is_an_error():
    tickets = ticket_list(
        tickets=[
            ticket("S1-T1", depends_on=["S1-T2"]),
            ticket("S1-T2", title="Add payment", depends_on=["S1-T1"], requirement_ids=[]),
        ]
    )
    report = validate_ticket_list(tickets, plan())
    errors = _errors(report)
    assert report.ok is False
    assert any(issue.target == "S1" for issue in errors)


def test_unknown_sprint_id_is_an_error():
    report = validate_ticket_list(ticket_list(sprint_id="S9"), plan())
    errors = _errors(report)
    assert report.ok is False
    assert len(report.issues) == 1
    assert len(errors) == 1
    assert errors[0].target == "S9"


def test_xl_without_clarification_is_an_error():
    raw = Ticket.model_construct(
        id="S1-T1",
        title="Build the whole shop",
        size=TicketSize.XL,
        needs_clarification=False,
        requirement_ids=["R1"],
        depends_on=[],
    )
    tickets = TicketList.model_construct(sprint_id="S1", tickets=[raw])
    report = validate_ticket_list(tickets, plan())
    errors = _errors(report)
    assert report.ok is False
    assert len(errors) == 1
    assert errors[0].target == "S1-T1"


def test_constructed_xl_ticket_is_flagged_and_passes():
    flagged = ticket(size=TicketSize.XL, needs_clarification=False)
    assert flagged.needs_clarification is True
    report = validate_ticket_list(ticket_list(tickets=[flagged]), plan())
    assert report.ok is True
    assert report.issues == []
