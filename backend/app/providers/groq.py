"""
groq.py — Groq LLM provider adapter.

Environment variables required (set in .env, never committed):
    GROQ_API_KEY   — Groq API key (free at console.groq.com, no card required)

Optional:
    GROQ_MODEL_ID  — model to use
                     (default: openai/gpt-oss-120b — free tier, 131K context, clean JSON output)

Selected when LLM_PROVIDER=groq (the default).
"""

from __future__ import annotations

import os
import re

import truststore
truststore.inject_into_ssl()

import httpx

_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_DEFAULT_MODEL = "openai/gpt-oss-120b"


class GroqProvider:
    """Groq provider — calls the OpenAI-compatible chat completions API."""

    def __init__(self) -> None:
        self._api_key = os.environ["GROQ_API_KEY"]
        self._model_id = os.environ.get("GROQ_MODEL_ID", _DEFAULT_MODEL)

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
    ) -> str:
        """Call Groq and return the raw JSON string."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _API_URL,
                json={
                    "model": self._model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4096,
                    # gpt-oss burns completion budget on reasoning; "low" leaves room
                    # for JSON without raising max_tokens / TPM.
                    "reasoning_effort": "low",
                },
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            )
            resp.raise_for_status()

        raw: str = resp.json()["choices"][0]["message"]["content"].strip()

        # Strip <think>...</think> blocks produced by reasoning models (e.g. qwen)
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        # Strip markdown code fences if the model wraps the JSON
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)

        return raw
