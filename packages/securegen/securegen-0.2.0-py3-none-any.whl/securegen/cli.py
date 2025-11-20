#!/usr/bin/env python
"""securegen CLI entry point.

Usage:
    securegen "build a login API in python"
"""

import sys
import argparse

from securegen.controller import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="securegen",
        description="Multi-agent secure prompt generator for AI codegen.",
    )
    parser.add_argument(
        "prompt",
        nargs=argparse.REMAINDER,
        help="The natural-language prompt you would normally send to an AI code generator.",
    )
    args = parser.parse_args()

    if not args.prompt:
        print('Usage: securegen "build a login API in python"')
        sys.exit(1)

    original_prompt = " ".join(args.prompt)
    result = run_pipeline(original_prompt)

    print("\n=== Original Prompt ===")
    print(original_prompt)

    print("\n=== Red Team Findings ===")
    findings = result.get("findings") or []
    if not findings:
        print("No issues detected (or model did not return structured findings).")
    else:
        for f in findings:
            t = f.get("type", "unknown")
            d = f.get("detail", "").strip()
            print(f"- [{t}] {d}")

    print("\n=== Final Secure Prompt ===")
    secure_prompt = (result.get("secure_prompt") or "").strip()
    if not secure_prompt:
        print("(No secure prompt generated; check model configuration.)")
    else:
        print(secure_prompt)

    code_preview = result.get("code_preview")
    if code_preview:
        print("\n=== Code Preview (from secure prompt) ===")
        print(code_preview.strip())


if __name__ == "__main__":
    main()
