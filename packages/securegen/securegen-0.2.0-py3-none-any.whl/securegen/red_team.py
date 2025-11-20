"""Red-team agents for prompt-level security analysis."""

from typing import List, Dict, Any

from securegen.models import call_model_json


def red_agent_sensitive(prompt: str) -> List[Dict[str, Any]]:
    """Detect mishandling of secrets / sensitive data at the prompt level."""
    system_prompt = (
        "You are a red-team security agent. Analyze this natural-language prompt that a "
        "developer will send to an AI code generator.\n\n"
        "Identify any signs that the generated code might mishandle sensitive data or secrets, such as:\n"
        "- Storing or exposing passwords in plaintext\n"
        "- Logging sensitive data (passwords, tokens, PII)\n"
        "- Hardcoding API keys, tokens, or secrets\n"
        "- Returning PII directly in responses without masking\n\n"
        "Return a JSON array of findings. Each finding must be an object with keys:\n"
        "  type: 'sensitive_data'\n"
        "  detail: short description of the risk in one sentence.\n"
        "If no issues are found, return an empty JSON array []."
    )
    return call_model_json(
        model_name="red_sensitive", system_prompt=system_prompt, user_content=prompt
    )


def red_agent_top5(prompt: str) -> List[Dict[str, Any]]:
    """Check for missing coverage of a small set of common vulns."""
    system_prompt = (
        "You are a vulnerability coverage auditor. You are given a natural-language prompt "
        "that will be sent to an AI code generator to implement some web or API functionality.\n\n"
        "Check whether the prompt explicitly mentions protections for each of the following areas:\n"
        "1) Authentication & password hashing\n"
        "2) Authorization / role-based access control\n"
        "3) Input validation & injection defenses (e.g., SQLi, XSS)\n"
        "4) Rate limiting / brute-force protection\n"
        "5) Protection of personal data (PII), including encryption/masking where relevant\n\n"
        "For each area that is missing or ambiguous, add a finding with:\n"
        "  type: 'coverage_gap'\n"
        "  detail: one sentence describing what is missing.\n"
        "Return a JSON array of findings. If there are no gaps, return []."
    )
    return call_model_json(
        model_name="red_top5", system_prompt=system_prompt, user_content=prompt
    )


def red_agent_dangerous(prompt: str) -> List[Dict[str, Any]]:
    """Detect obviously dangerous/insecure instructions in the prompt."""
    system_prompt = (
        "You are a red-team prompt auditor. Analyze this natural-language prompt that a developer "
        "plans to send to an AI code generator.\n\n"
        "Look for any obviously dangerous or insecure instructions, such as:\n"
        "- 'skip authentication'\n"
        "- 'do not hash the password'\n"
        "- 'no input validation needed'\n"
        "- 'disable SSL certificate verification'\n"
        "- 'trust all user input'\n"
        "- 'store tokens in localStorage with no expiration'\n\n"
        "Return a JSON array of findings. Each finding must be an object with:\n"
        "  type: 'dangerous_instruction'\n"
        "  detail: the exact phrase or behavior and why it is risky.\n"
        "If there are no such instructions, return []."
    )
    return call_model_json(
        model_name="red_dangerous", system_prompt=system_prompt, user_content=prompt
    )


def run_red_team(prompt: str) -> List[Dict[str, Any]]:
    """Run all red-team agents and aggregate their findings."""
    findings: List[Dict[str, Any]] = []
    for agent in (red_agent_sensitive, red_agent_top5, red_agent_dangerous):
        try:
            findings.extend(agent(prompt) or [])
        except Exception as exc:  # pragma: no cover
            findings.append(
                {
                    "type": "agent_error",
                    "detail": f"Red-team agent {agent.__name__} failed: {exc}",
                }
            )
    return findings
