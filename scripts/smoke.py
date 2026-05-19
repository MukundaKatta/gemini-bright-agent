"""Real Vertex AI smoke test for gemini-bright-agent.

Runs a research question end-to-end through Gemini 2.5 Flash on the
Bright Data MCP stub and verifies the agent walks SERP → scrape → cite,
emits all 5 labeled sections, and quotes the verbatim "22%" latency
figure from the scraped Anthropic page.

Usage:
    GOOGLE_CLOUD_PROJECT=careersavvy-mukunda \
    GOOGLE_GENAI_USE_VERTEXAI=true \
    GOOGLE_CLOUD_LOCATION=us-central1 \
    .venv/bin/python scripts/smoke.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "careersavvy-mukunda")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from gemini_bright_agent.runner import ask  # noqa: E402


QUESTION = (
    "Anthropic Claude latest release notes 2026. Walk the Bright Data "
    "tools — SERP search, then scrape the top first-party result, then "
    "lookup the LinkedIn company record — and output the labeled sections "
    "from your system prompt with verbatim quotes."
)


def main() -> int:
    print("== gemini-bright-agent smoke ==")
    print(f"project={os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"location={os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    print(f"vertexai={os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")
    print()
    print(f"> {QUESTION}")
    print()

    resp = ask(QUESTION, stub=True)
    print("--- FINAL TEXT ---")
    print(resp.final_text or "(no final text)")
    print("--- END FINAL TEXT ---")
    print(f"events: {len(resp.events)}")

    text = resp.final_text or ""
    upper = text.upper()
    checks = {
        "has ANSWER section":      "ANSWER" in upper,
        "has SOURCES section":     "SOURCES" in upper,
        "has KEY QUOTES section":  "KEY QUOTES" in upper,
        "has CONFIDENCE section":  "CONFIDENCE" in upper,
        "has NEXT STEP section":   "NEXT STEP" in upper,
        "quotes 22% verbatim":     "22%" in text,
        "cites anthropic.com":     "anthropic.com" in text.lower(),
        "names Claude 4.7":        "4.7" in text,
    }
    print()
    print("--- CHECKS ---")
    for label, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
