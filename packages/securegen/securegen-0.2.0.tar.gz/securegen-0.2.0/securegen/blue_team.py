"""Blue-team agents for secure prompt rewriting."""

from typing import List, Dict, Any

from securegen.models import call_model_text


def blue_agent_rewrite(original_prompt: str, findings: List[Dict[str, Any]]) -> str:
    """First secure rewrite based on red-team findings."""
    system_prompt = (
        "You are a senior secure software architect. Your job is to rewrite insecure or incomplete "
        "natural-language prompts into secure, implementation-ready prompts for AI code generators.\n\n"
        "You will be given the original prompt and a list of security findings. Rewrite the prompt so that it:\n"
        "- Preserves the developer's original intent and tech stack\n"
        "- Explicitly addresses the security findings\n"
        "- Uses clear, unambiguous language\n"
        "- Remains concise and practical (something a developer would paste into a code assistant)\n\n"
        "Return only the rewritten prompt text."
    )
    user_content = {
        "original_prompt": original_prompt,
        "findings": findings,
    }
    return call_model_text(
        model_name="blue_rewrite", system_prompt=system_prompt, user_content=user_content
    )


def blue_agent_harden(rewritten_prompt: str, findings: List[Dict[str, Any]]) -> str:
    """Strengthen the security guarantees and add explicit best practices."""
    system_prompt = (
        "You are a security hardening assistant. You receive a rewritten prompt that is already "
        "security-aware, plus a list of findings.\n\n"
        "Your job is to:\n"
        "- Make security requirements more explicit and precise\n"
        "- Add missing details about hashing, validation, rate limiting, and PII protection\n"
        "- Ensure sensitive flows (auth, payments, personal data) are described with secure defaults\n"
        "- Avoid unnecessary verbosity\n\n"
        "Return only the improved prompt text."
    )
    user_content = {
        "rewritten_prompt": rewritten_prompt,
        "findings": findings,
    }
    return call_model_text(
        model_name="blue_harden", system_prompt=system_prompt, user_content=user_content
    )


def blue_agent_cleanup(hardened_prompt: str) -> str:
    """Clean up the hardened prompt for developer usability."""
    system_prompt = (
        "You are a developer-experience specialist. You receive a security-hardened prompt.\n"
        "Your task is to:\n"
        "- Keep all security requirements intact\n"
        "- Remove redundancy and overly formal prose\n"
        "- Make the prompt concise, direct, and easy for a developer to read and paste\n\n"
        "Return only the final cleaned prompt."
    )
    return call_model_text(
        model_name="blue_cleanup", system_prompt=system_prompt, user_content=hardened_prompt
    )


def run_blue_team(original_prompt: str, findings: List[Dict[str, Any]]) -> str:
    """Run blue-team agents in sequence to produce the final secure prompt."""
    draft1 = blue_agent_rewrite(original_prompt, findings)
    draft2 = blue_agent_harden(draft1, findings)
    final_prompt = blue_agent_cleanup(draft2)
    return final_prompt
