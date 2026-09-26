"""
Prompt test script — Person B

Tests either prompt file directly against the configured LLM provider,
without needing Person A's backend to be running.

Usage
-----
  # Capability 1 (PRD → sprint plan):
  python scripts/test_prompt.py --capability 1 --prd samples/prd-messy.md

  # Capability 2 (sprint → tickets):
  python scripts/test_prompt.py --capability 2 --prd samples/prd-messy.md --sprint-id S1

  # Use a different PRD:
  python scripts/test_prompt.py --capability 1 --prd samples/prd-clean.md

Environment variables (put in .env or export before running)
-------------------------------------------------------------
  LLM_PROVIDER      openai | anthropic | watsonx   (default: openai)

  # OpenAI / any OpenAI-compatible endpoint:
  OPENAI_API_KEY    your key
  OPENAI_MODEL      model name (default: gpt-4o-mini)
  OPENAI_BASE_URL   override base URL for compatible APIs (optional)

  # Anthropic:
  ANTHROPIC_API_KEY your key
  ANTHROPIC_MODEL   model name (default: claude-3-5-haiku-latest)

  # IBM watsonx.ai:
  WATSONX_API_KEY   your IBM Cloud API key
  WATSONX_PROJECT_ID your watsonx project id
  WATSONX_URL       service URL (default: https://us-south.ml.cloud.ibm.com)
  WATSONX_MODEL     model id (default: ibm/granite-3-3-8b-instruct)

Output
------
  - Prints the raw JSON response from the LLM.
  - Validates it against the Pydantic model (SprintPlan or TicketList).
  - Prints a validation summary: OK or the list of errors.
  - Saves the raw response to scripts/last_response.json for inspection.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import textwrap
import time

import httpx
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path setup — make backend importable without installing it
# ---------------------------------------------------------------------------

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.models import SprintPlan, TicketList  # noqa: E402

load_dotenv(ROOT / ".env")

# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------

PROMPT_DIR = ROOT / "backend" / "prompts"


def _load_prompt(path: pathlib.Path) -> tuple[str, str]:
    """Return (system_section, user_template_section) parsed from a prompt .md file."""
    text = path.read_text(encoding="utf-8")

    def _extract(heading: str) -> str:
        # Find the heading line, then collect lines until the next ## heading
        lines = text.splitlines()
        inside = False
        collected: list[str] = []
        for line in lines:
            if line.strip() == f"## {heading}":
                inside = True
                continue
            if inside:
                if line.startswith("## "):
                    break
                collected.append(line)
        return "\n".join(collected).strip()

    system = _extract("System")
    # The user template is wrapped in a fenced code block inside the section
    user_template_section = _extract("User message template")
    # Strip the outer ``` fences if present
    lines = user_template_section.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    user_template = "\n".join(lines).strip()

    return system, user_template


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


def _call_openai(system: str, user: str) -> str:
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    with httpx.Client(timeout=120) as client:
        r = client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _call_anthropic(system: str, user: str) -> str:
    api_key = os.environ["ANTHROPIC_API_KEY"]
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")

    payload = {
        "model": model,
        "max_tokens": 8192,
        "temperature": 0.2,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    with httpx.Client(timeout=240) as client:
        r = client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
        )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def _get_watsonx_token(api_key: str) -> str:
    """Exchange an IBM Cloud API key for a short-lived IAM bearer token."""
    with httpx.Client(timeout=30) as client:
        r = client.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    r.raise_for_status()
    return r.json()["access_token"]


def _call_watsonx(system: str, user: str) -> str:
    api_key = os.environ.get("WATSONX_API_KEY") or os.environ["IBM_CLOUD_API_KEY"]
    project_id = os.environ["WATSONX_PROJECT_ID"]
    base_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model = os.getenv("WATSONX_MODEL", "ibm/granite-3-3-8b-instruct")

    token = _get_watsonx_token(api_key)

    # watsonx.ai uses a combined prompt; prepend system as an instruction block
    combined_prompt = f"{system}\n\n{user}"

    payload = {
        "model_id": model,
        "project_id": project_id,
        "input": combined_prompt,
        "parameters": {
            "decoding_method": "greedy",
            "temperature": 0.2,
            "max_new_tokens": 8192,
        },
    }
    with httpx.Client(timeout=120) as client:
        r = client.post(
            f"{base_url}/ml/v1/text/generation?version=2023-05-29",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
    if not r.is_success:
        print(f"\nwatsonx error {r.status_code}:\n{r.text}\n")
        r.raise_for_status()
    return r.json()["results"][0]["generated_text"]


PROVIDERS = {
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "watsonx": _call_watsonx,
}

# ---------------------------------------------------------------------------
# Schema injection
# ---------------------------------------------------------------------------


def _inject_schema(template: str, capability: int, plan_json: str | None, sprint_id: str | None, prd: str) -> str:
    if capability == 1:
        schema = json.dumps(SprintPlan.model_json_schema(), indent=2)
        return (
            template
            .replace("{{PRD_MARKDOWN}}", prd)
            .replace("{{JSON_SCHEMA}}", schema)
        )
    else:
        schema = json.dumps(TicketList.model_json_schema(), indent=2)
        return (
            template
            .replace("{{PRD_MARKDOWN}}", prd)
            .replace("{{SPRINT_PLAN_JSON}}", plan_json or "")
            .replace("{{SPRINT_ID}}", sprint_id or "")
            .replace("{{JSON_SCHEMA}}", schema)
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _strip_fences(raw: str) -> str:
    """Remove markdown code fences that some models wrap JSON in."""
    raw = raw.strip()
    if raw.startswith("```"):
        # drop the opening fence line (```json or ```)
        raw = raw[raw.index("\n") + 1:]
    if raw.endswith("```"):
        raw = raw[: raw.rfind("```")]
    return raw.strip()


def _validate(raw: str, capability: int) -> None:
    raw = _strip_fences(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"\n[FAIL]  Response is not valid JSON: {e}")
        return

    model_cls = SprintPlan if capability == 1 else TicketList
    try:
        model_cls.model_validate(data)
        print(f"\n[OK]  Pydantic validation passed ({model_cls.__name__})")
    except Exception as e:
        print(f"\n[FAIL]  Pydantic validation failed:\n{textwrap.indent(str(e), '    ')}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Test a prompt file directly against the LLM provider.")
    parser.add_argument("--capability", type=int, choices=[1, 2], required=True,
                        help="1 = PRD→sprints, 2 = sprint→tickets")
    parser.add_argument("--prd", type=pathlib.Path, required=True,
                        help="Path to the PRD Markdown file, e.g. samples/prd-messy.md")
    parser.add_argument("--sprint-id", type=str, default=None,
                        help="Sprint id to expand (required for --capability 2), e.g. S1")
    parser.add_argument("--plan", type=pathlib.Path, default=None,
                        help="Path to a sprint plan JSON file (for --capability 2). "
                             "Defaults to samples/fixtures/sprint-plan.example.json")
    args = parser.parse_args()

    # Validate args
    if args.capability == 2 and not args.sprint_id:
        parser.error("--sprint-id is required for --capability 2")

    prd_text = args.prd.read_text(encoding="utf-8")

    plan_json: str | None = None
    if args.capability == 2:
        plan_path = args.plan or (ROOT / "samples" / "fixtures" / "sprint-plan.example.json")
        plan_json = plan_path.read_text(encoding="utf-8")

    # Choose provider
    provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider_name not in PROVIDERS:
        print(f"Unknown LLM_PROVIDER '{provider_name}'. Choose from: {', '.join(PROVIDERS)}")
        sys.exit(1)
    call_provider = PROVIDERS[provider_name]

    # Load prompt
    prompt_file = PROMPT_DIR / ("prd_to_sprints.md" if args.capability == 1 else "sprint_to_tickets.md")
    system, user_template = _load_prompt(prompt_file)
    user = _inject_schema(user_template, args.capability, plan_json, args.sprint_id, prd_text)

    # Call
    print(f"Provider : {provider_name}")
    print(f"Prompt   : {prompt_file.name}")
    print(f"PRD      : {args.prd}")
    if args.capability == 2:
        print(f"Sprint   : {args.sprint_id}")
    print("\nCalling LLM… (this may take 20–60 seconds)")
    t0 = time.monotonic()
    raw = call_provider(system, user)
    elapsed = time.monotonic() - t0
    print(f"Response received in {elapsed:.1f}s")

    # Save
    out_path = ROOT / "scripts" / "last_response.json"
    try:
        parsed = json.loads(raw)
        out_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
        print(f"Saved to : {out_path.relative_to(ROOT)}")
    except json.JSONDecodeError:
        out_path.write_text(raw, encoding="utf-8")
        print(f"Saved raw (not JSON) to: {out_path.relative_to(ROOT)}")

    # Validate
    _validate(raw, args.capability)


if __name__ == "__main__":
    main()
