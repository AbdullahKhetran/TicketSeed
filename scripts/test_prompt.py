"""
Prompt test script — Person B

Tests either prompt file directly against Groq, without needing the
FastAPI backend to be running.

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
  LLM_PROVIDER=groq          (required; project is Groq-only)
  GROQ_API_KEY               your Groq API key (console.groq.com)
  GROQ_MODEL_ID              model id (default: openai/gpt-oss-120b)

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
import re
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

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_DEFAULT_MODEL = "openai/gpt-oss-120b"


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
# Groq provider (only supported LLM)
# ---------------------------------------------------------------------------


def _call_groq(system: str, user: str) -> str:
    api_key = os.environ["GROQ_API_KEY"]
    model = os.getenv("GROQ_MODEL_ID", _DEFAULT_MODEL)

    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    with httpx.Client(timeout=120) as client:
        r = client.post(
            _GROQ_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )
    if not r.is_success:
        print(f"\nGroq error {r.status_code}:\n{r.text}\n")
        r.raise_for_status()

    raw: str = r.json()["choices"][0]["message"]["content"].strip()

    # Strip <think>...</think> blocks produced by reasoning models
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Strip markdown code fences if the model wraps the JSON
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    return raw


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
    parser = argparse.ArgumentParser(description="Test a prompt file directly against Groq.")
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

    if "GROQ_API_KEY" not in os.environ or not os.environ["GROQ_API_KEY"].strip():
        print("GROQ_API_KEY is not set. Add it to your .env file (see .env.example).")
        sys.exit(1)

    provider_name = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    if provider_name and provider_name != "groq":
        print(f"Unknown LLM_PROVIDER '{provider_name}'. This project supports Groq only (LLM_PROVIDER=groq).")
        sys.exit(1)

    prd_text = args.prd.read_text(encoding="utf-8")

    plan_json: str | None = None
    if args.capability == 2:
        plan_path = args.plan or (ROOT / "samples" / "fixtures" / "sprint-plan.example.json")
        plan_json = plan_path.read_text(encoding="utf-8")

    # Load prompt
    prompt_file = PROMPT_DIR / ("prd_to_sprints.md" if args.capability == 1 else "sprint_to_tickets.md")
    system, user_template = _load_prompt(prompt_file)
    user = _inject_schema(user_template, args.capability, plan_json, args.sprint_id, prd_text)

    model = os.getenv("GROQ_MODEL_ID", _DEFAULT_MODEL)

    # Call
    print(f"Provider : groq")
    print(f"Model    : {model}")
    print(f"Prompt   : {prompt_file.name}")
    print(f"PRD      : {args.prd}")
    if args.capability == 2:
        print(f"Sprint   : {args.sprint_id}")
    print("\nCalling LLM… (this may take 20–60 seconds)")
    t0 = time.monotonic()
    raw = _call_groq(system, user)
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
