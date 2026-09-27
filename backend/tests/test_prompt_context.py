"""Tests for Cap 2 plan slimming (matches scripts/test_prompt harness)."""

import pytest

from backend.app.prompt_context import slim_plan_for_sprint
from backend.tests.helpers import plan, question, requirement, sprint


def _full_plan_dict() -> dict:
    """Two earlier stubs, target S3, later S4, extra requirement, and a question."""
    return plan(
        requirements=[
            requirement("R1", source_quote="order online"),
            requirement("R2", source_quote="and pay"),
            requirement("R3", source_quote="Customers should"),
            requirement("R99", source_quote="order online"),  # unused later-only
        ],
        sprints=[
            sprint("S1", order=1, requirement_ids=["R1"], name="Foundations"),
            sprint("S2", order=2, requirement_ids=["R2"], name="Payments", depends_on=["S1"]),
            sprint(
                "S3",
                order=3,
                requirement_ids=["R3"],
                name="Checkout",
                depends_on=["S2"],
                deliverables=["Checkout UI"],
                rationale="After payments.",
            ),
            sprint(
                "S4",
                order=4,
                requirement_ids=["R99"],
                name="Later work",
                deliverables=["Should not appear"],
                rationale="Dropped for Cap 2.",
            ),
        ],
        client_questions=[question(requirement_ids=["R1"])],
    ).model_dump(mode="json")


def test_slim_keeps_target_sprint_full():
    slim = slim_plan_for_sprint(_full_plan_dict(), "S3")
    target = next(s for s in slim["sprints"] if s["id"] == "S3")
    assert target["name"] == "Checkout"
    assert target["deliverables"] == ["Checkout UI"]
    assert target["rationale"] == "After payments."
    assert target["requirement_ids"] == ["R3"]


def test_slim_stubs_earlier_sprints():
    slim = slim_plan_for_sprint(_full_plan_dict(), "S3")
    by_id = {s["id"]: s for s in slim["sprints"]}
    assert set(by_id) == {"S1", "S2", "S3"}
    assert by_id["S1"]["deliverables"] == []
    assert by_id["S1"]["rationale"] == ""
    assert by_id["S1"]["name"] == "Foundations"
    assert by_id["S1"]["requirement_ids"] == ["R1"]
    assert by_id["S2"]["deliverables"] == []
    assert by_id["S2"]["rationale"] == ""


def test_slim_drops_later_sprints_and_unused_requirements():
    slim = slim_plan_for_sprint(_full_plan_dict(), "S3")
    assert all(s["id"] != "S4" for s in slim["sprints"])
    req_ids = {r["id"] for r in slim["requirements"]}
    assert req_ids == {"R1", "R2", "R3"}
    assert "R99" not in req_ids


def test_slim_clears_client_questions():
    slim = slim_plan_for_sprint(_full_plan_dict(), "S3")
    assert slim["client_questions"] == []
    assert slim["project"]["name"] == "Shop"


def test_slim_unknown_sprint_raises():
    with pytest.raises(ValueError, match="S9"):
        slim_plan_for_sprint(_full_plan_dict(), "S9")


def test_slim_first_sprint_has_no_stubs():
    slim = slim_plan_for_sprint(_full_plan_dict(), "S1")
    assert [s["id"] for s in slim["sprints"]] == ["S1"]
    assert {r["id"] for r in slim["requirements"]} == {"R1"}
