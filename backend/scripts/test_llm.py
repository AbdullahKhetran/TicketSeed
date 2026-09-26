"""
Quick diagnostic script — tests the configured LLM provider connection.
Run from repo root with .venv active:
    python -m backend.scripts.test_llm
"""
import asyncio
import os
import truststore
import httpx
from dotenv import load_dotenv

# Use the OS/system certificate store so corporate proxy certs are trusted
truststore.inject_into_ssl()

load_dotenv()


async def test_groq(base_url: str = "https://api.groq.com/openai/v1") -> None:
    api_key = os.environ["GROQ_API_KEY"]
    model_id = os.environ.get("GROQ_MODEL_ID", "openai/gpt-oss-120b")

    print(f"Provider : groq")
    print(f"Model    : {model_id}")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/chat/completions",
            json={
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": 'Respond with valid JSON only. Return: {"greeting": "hello"}'},
                ],
                "temperature": 0.2,
                "max_tokens": 20,
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        if resp.status_code == 200:
            result = resp.json()["choices"][0]["message"]["content"].strip()
            print(f"Response : {result}")
            print("\nConnection to Groq is working correctly.")
        else:
            print(f"FAILED — {resp.status_code}: {resp.text}")


async def main() -> None:
    provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
    print(f"Testing LLM_PROVIDER={provider!r}\n")
    if provider == "groq":
        await test_groq()
    else:
        print(f"Unknown provider {provider!r}. Set LLM_PROVIDER=groq in your .env file.")


asyncio.run(main())
