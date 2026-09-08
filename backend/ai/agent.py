"""
AI Business Manager agent.

Flow:
    User question
      -> LLM selects tools (intent)
      -> Python executes tools against the owner's data (facts)
      -> LLM interprets facts and answers (insight)

The LLM never calculates raw numbers — it only explains them.
Uses Groq's OpenAI-compatible API.
"""

import json

from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from ai.prompts import SYSTEM_PROMPT, TOOL_SELECTION_PROMPT
from ai.tools import TOOL_REGISTRY
from config import settings

def _llm(messages: list[dict], temperature: float = 0.3) -> str:
    if not settings.GROQ_API_KEY:
        raise HTTPException(503,
                            "AI is not configured. Set GROQ_API_KEY in .env")
    client = OpenAI(api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1")
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=600,
    )
    return resp.choices[0].message.content or ""


def select_tools(question: str) -> list[str]:
    """Ask the LLM which business tools it needs (intent understanding)."""
    tool_list = "\n".join(f"- {name}" for name in TOOL_REGISTRY)
    raw = _llm([{"role": "user", "content": TOOL_SELECTION_PROMPT.format(
        question=question, tools=tool_list)}], temperature=0.0)

    try:
        start, end = raw.find("["), raw.rfind("]")
        names = json.loads(raw[start:end + 1])
        valid = [n for n in names if n in TOOL_REGISTRY][:4]
        return valid or ["get_sales"]
    except Exception:
        return ["get_sales"]


def run_tools(db: Session, business_id: int, tool_names: list[str]) -> dict:
    """Execute selected tools and collect the facts."""
    facts = {}
    for name in tool_names:
        try:
            facts[name] = TOOL_REGISTRY[name](db, business_id)
        except Exception as e:
            facts[name] = {"error": f"tool failed: {e}"}
    return facts


def ask_agent(db: Session, business_id: int, question: str,
              history: list[dict] | None = None) -> dict:
    """Full agent pipeline. Returns answer + the facts used (for transparency)."""
    tool_names = select_tools(question)
    facts = run_tools(db, business_id, tool_names)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in (history or [])[-6:]:
        messages.append({"role": h.get("role", "user"),
                         "content": str(h.get("content", ""))[:1000]})
    messages.append({
        "role": "user",
        "content": (
            f"Owner's question: {question}\n\n"
            f"Facts from business tools (JSON):\n{json.dumps(facts, default=str)}"
        ),
    })

    answer = _llm(messages)
    return {
        "answer": answer.strip(),
        "tools_used": tool_names,
        "facts": facts,
    }
