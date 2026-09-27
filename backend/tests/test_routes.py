"""Route tests with a fake LLM provider. Never calls Groq."""

import json

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routes import _LLM_FAILURE_DETAIL
from backend.tests.helpers import PRD, plan, requirement, sprint, ticket, ticket_list

_BOOM = "SECRET_PROVIDER_BOOM"


class FakeProvider:
    def __init__(self, responses: list):
        self._responses = list(responses)
        self.calls = 0
        self.user_prompts: list[str] = []

    async def generate_json(self, system_prompt: str, user_prompt: str, json_schema: dict) -> str:
        self.calls += 1
        self.user_prompts.append(user_prompt)
        item = self._responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


@pytest.fixture
def client():
    return TestClient(app)


def _patch_provider(monkeypatch, responses: list) -> FakeProvider:
    fake = FakeProvider(responses)
    monkeypatch.setattr("backend.app.routes._get_provider", lambda: fake)
    return fake


def test_health_reports_status_and_hides_secrets(client):
    response = client.get("/api/health")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert "provider" in body
    text = response.text.lower()
    assert "api_key" not in text
    assert "groq_api_key" not in text
    assert "secret" not in text


def test_sprints_rejects_empty_prd(client):
    response = client.post("/api/plan/sprints", json={"prd_markdown": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "prd_markdown must not be empty."


def test_sprints_rejects_whitespace_prd(client):
    response = client.post("/api/plan/sprints", json={"prd_markdown": "  \n\t  "})
    assert response.status_code == 400
    assert response.json()["detail"] == "prd_markdown must not be empty."


def test_sprints_rejects_overlong_prd(client):
    response = client.post("/api/plan/sprints", json={"prd_markdown": "a" * 30_001})
    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"]


def test_sprints_happy_path(client, monkeypatch):
    fake = _patch_provider(monkeypatch, [plan().model_dump_json()])
    response = client.post("/api/plan/sprints", json={"prd_markdown": PRD})
    body = response.json()
    assert response.status_code == 200
    assert "plan" in body
    assert "validation" in body
    assert body["validation"]["ok"] is True
    assert fake.calls == 1


def test_sprints_retries_invalid_json_then_succeeds(client, monkeypatch):
    fake = _patch_provider(monkeypatch, ["not-json", plan().model_dump_json()])
    response = client.post("/api/plan/sprints", json={"prd_markdown": PRD})
    assert response.status_code == 200
    assert "plan" in response.json()
    assert fake.calls == 2


def test_sprints_retries_schema_mismatch_then_succeeds(client, monkeypatch):
    fake = _patch_provider(monkeypatch, ['{"nope": true}', plan().model_dump_json()])
    response = client.post("/api/plan/sprints", json={"prd_markdown": PRD})
    assert response.status_code == 200
    assert response.json()["validation"]["ok"] is True
    assert fake.calls == 2


def test_sprints_provider_failure_twice_is_502(client, monkeypatch):
    fake = _patch_provider(
        monkeypatch,
        [RuntimeError(_BOOM), RuntimeError(_BOOM)],
    )
    response = client.post("/api/plan/sprints", json={"prd_markdown": PRD})
    assert response.status_code == 502
    assert response.json()["detail"] == _LLM_FAILURE_DETAIL
    assert _BOOM not in response.text
    assert fake.calls == 2


def test_sprints_schema_mismatch_twice_is_502(client, monkeypatch):
    fake = _patch_provider(monkeypatch, ['{"nope": true}', '{"still": false}'])
    response = client.post("/api/plan/sprints", json={"prd_markdown": PRD})
    assert response.status_code == 502
    assert response.json()["detail"] == _LLM_FAILURE_DETAIL
    assert fake.calls == 2


def _tickets_body(**overrides) -> dict:
    body = {
        "prd_markdown": PRD,
        "plan": plan().model_dump(mode="json"),
        "sprint_id": "S1",
    }
    body.update(overrides)
    return body


def test_tickets_rejects_empty_prd(client):
    response = client.post("/api/plan/tickets", json=_tickets_body(prd_markdown=""))
    assert response.status_code == 400
    assert response.json()["detail"] == "prd_markdown must not be empty."


def test_tickets_rejects_unknown_sprint(client):
    response = client.post("/api/plan/tickets", json=_tickets_body(sprint_id="S2"))
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_tickets_happy_path(client, monkeypatch):
    fake = _patch_provider(monkeypatch, [ticket_list().model_dump_json()])
    response = client.post("/api/plan/tickets", json=_tickets_body())
    body = response.json()
    assert response.status_code == 200
    assert "tickets" in body
    assert "validation" in body
    assert body["validation"]["ok"] is True
    assert fake.calls == 1


def test_tickets_prompt_is_slimmed_and_compact(client, monkeypatch):
    """Cap 2 user prompt matches harness: compact JSON, later sprints dropped."""
    later_marker = "UNIQUE_LATER_SPRINT_MARKER_SHOULD_NOT_APPEAR"
    multi = plan(
        requirements=[
            requirement("R1", source_quote="order online"),
            requirement("R2", source_quote="and pay"),
        ],
        sprints=[
            sprint("S1", order=1, requirement_ids=["R1"], rationale="Foundations come first."),
            sprint(
                "S2",
                order=2,
                requirement_ids=["R2"],
                name="Later",
                depends_on=["S1"],
                rationale=later_marker,
                deliverables=[later_marker],
            ),
        ],
    )
    tickets = ticket_list(
        sprint_id="S1",
        tickets=[ticket("S1-T1", requirement_ids=["R1"])],
    )
    fake = _patch_provider(monkeypatch, [tickets.model_dump_json()])
    response = client.post(
        "/api/plan/tickets",
        json=_tickets_body(plan=multi.model_dump(mode="json"), sprint_id="S1"),
    )
    assert response.status_code == 200
    assert fake.calls == 1
    prompt = fake.user_prompts[0]
    assert later_marker not in prompt
    assert '"id":"S1"' in prompt
    assert '"id":"S2"' not in prompt
    # Compact JSON: schema/plan should not be pretty-printed with 2-space indent
    assert '{\n  "id"' not in prompt
    # Schema fence still present and compact
    assert "```json\n{" in prompt
    # Round-trip: embedded plan JSON parses and only has S1
    start = prompt.index("```json\n", prompt.index("Full sprint plan")) + len("```json\n")
    end = prompt.index("\n```", start)
    embedded = json.loads(prompt[start:end])
    assert [s["id"] for s in embedded["sprints"]] == ["S1"]
    assert embedded["client_questions"] == []
