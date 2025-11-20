"""Code preview generation from the final secure prompt."""

from securegen.models import call_model_text


def generate_preview(secure_prompt: str) -> str:
    """Generate a short secure code snippet from the secure prompt."""
    if not secure_prompt:
        return ""

    system_prompt = (
        "You are a senior backend engineer. Given a secure natural-language prompt describing "
        "a feature, generate a short code snippet (15-30 lines) that demonstrates the key secure "
        "patterns (e.g., password hashing, validation, rate limiting).\n\n"
        "Focus on clarity, not completeness. Return only code, no explanation."
    )
    return call_model_text(
        model_name="code_preview", system_prompt=system_prompt, user_content=secure_prompt
    )
