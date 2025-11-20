"""Model abstraction layer for securegen.

This keeps provider-specific logic (OpenAI, Anthropic, etc.) in one place,
so the rest of the code only thinks in terms of `call_model_text` and
`call_model_json`.
"""

import json
import os
from typing import Any, Dict, List

# Optional imports; we raise clear errors if not installed.
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

try:
    import anthropic  # type: ignore
except Exception:  # pragma: no cover
    anthropic = None  # type: ignore


OPENAI_MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_MODEL_STRONG = os.getenv("OPENAI_MODEL_STRONG", "gpt-4.1")
ANTHROPIC_MODEL_DEFAULT = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")


def _get_openai_client():
    if OpenAI is None:
        raise RuntimeError("openai package is not installed. Run `pip install openai`.")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI()


def _get_anthropic_client():
    if anthropic is None:
        raise RuntimeError(
            "anthropic package is not installed. Run `pip install anthropic`."
        )
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    return anthropic.Anthropic()


def _serialize_user_content(user_content: Any) -> str:
    if isinstance(user_content, (dict, list)):
        try:
            return json.dumps(user_content, indent=2)
        except Exception:
            return str(user_content)
    return str(user_content)


def _call_openai_chat(model: str, system_prompt: str, user_content: Any) -> str:
    client = _get_openai_client()
    content = _serialize_user_content(user_content)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


def _call_anthropic_chat(model: str, system_prompt: str, user_content: Any) -> str:
    client = _get_anthropic_client()
    content = _serialize_user_content(user_content)
    resp = client.messages.create(
        model=model,
        max_tokens=800,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )
    chunks: List[str] = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            chunks.append(block.text)
    return "\n".join(chunks).strip()


def call_model_text(model_name: str, system_prompt: str, user_content: Any) -> str:
    """Call a model and return plain text.

    Routing:
    - Names starting with 'red_' try Anthropic first, then fall back to OpenAI.
    - Names starting with 'blue_' or 'code_' use OpenAI.
    """
    # Red team prefers Anthropic
    if model_name.startswith("red_"):
        try:
            return _call_anthropic_chat(
                ANTHROPIC_MODEL_DEFAULT, system_prompt, user_content
            )
        except Exception:
            return _call_openai_chat(
                OPENAI_MODEL_STRONG, system_prompt, user_content
            )

    # Blue team + codegen use OpenAI
    return _call_openai_chat(OPENAI_MODEL_STRONG, system_prompt, user_content)


def call_model_json(model_name: str, system_prompt: str, user_content: Any) -> List[Dict[str, Any]]:
    """Call a model and parse JSON array of findings.

    If parsing fails, wrap raw text as a single generic finding so the pipeline still runs.
    """
    text = call_model_text(model_name, system_prompt, user_content)
    if not text:
        return []

    candidate = text.strip()
    if "```" in candidate:
        parts = candidate.split("```")
        for part in parts:
            p = part.strip()
            if p.startswith("json"):
                p = p[len("json") :].strip()
            if p.startswith("[") or p.startswith("{"):
                candidate = p
                break

    try:
        data = json.loads(candidate)
        if isinstance(data, list):
            return data  # type: ignore[return-value]
        if isinstance(data, dict):
            return [data]  # type: ignore[list-item]
    except Exception:
        pass

    return [
        {
            "type": f"{model_name}_unparsed",
            "detail": text,
        }
    ]
