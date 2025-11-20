"""Controller/orchestrator for the securegen pipeline."""

from typing import Dict, Any

from securegen.red_team import run_red_team
from securegen.blue_team import run_blue_team
from securegen.codegen import generate_preview


def run_pipeline(original_prompt: str) -> Dict[str, Any]:
    """Run the full multi-agent pipeline on a single prompt."""
    findings = run_red_team(original_prompt)
    secure_prompt = run_blue_team(original_prompt, findings)
    code_preview = generate_preview(secure_prompt) if secure_prompt else None

    return {
        "findings": findings,
        "secure_prompt": secure_prompt,
        "code_preview": code_preview,
    }
