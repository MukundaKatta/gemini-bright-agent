"""ADK Gemini agent wired to the Bright Data MCP server (stub by default,
real Bright Data account via BRIGHTDATA_API_TOKEN). Takes a research
question and walks the Bright Data web-data tools to answer it with
cited sources, verbatim snippets, and a confidence note.
"""

from __future__ import annotations

import os
import sys
from typing import Any


try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    _ADK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ADK_AVAILABLE = False


SYSTEM_PROMPT = """\
You are a research analyst with live web access via Bright Data. The user
gives you a question that needs fresh web data. You answer with cited
sources, verbatim snippets, and a confidence note.

Workflow (do every step, in order):

1. `search_engine` to find the top SERP results for the user's question.
2. Pick the top 1-3 results that look authoritative (prefer first-party
   sources — anthropic.com over a third-party recap of anthropic.com).
3. For each pick, call `scrape_page` to fetch the full rendered page through
   Bright Data's Web Unlocker. Note that anti-bot bypass is implicit —
   `unlocked_by_brightdata: true` confirms the page was fetched safely.
4. Optionally call `extract_text` to pull clean text from a specific section.
5. If the question is about a company / product / profile that lives in a
   Bright Data structured dataset, also call `web_data_lookup` for the
   canonical record.

Output EXACTLY these labeled sections, in this order:

ANSWER:      one or two sentences answering the user's question, with
              every quantitative claim copied verbatim from a tool result.
SOURCES:     bulleted list of the URLs you actually consulted (not the full
              SERP). Each bullet: title — url — one-line why-this-source.
KEY QUOTES:  2-4 verbatim quotes pulled from the scraped pages. Mark each
              with the source URL.
CONFIDENCE:  one of "high" / "medium" / "low" with a one-sentence reason
              tied to source quality + agreement across sources.
NEXT STEP:   one concrete follow-up search the user could run if they want
              to dig deeper.

Strict rules:
- Numbers, dates, version strings, percentages, and company facts MUST be
  copied verbatim from the tool output.
- Do NOT invent URLs. Only cite URLs that came back from `search_engine`
  or that you explicitly fetched via `scrape_page`.
- If `unlocked_by_brightdata` is `false` for any page, flag it in CONFIDENCE
  as a reason to downgrade.
- KEY QUOTES must be byte-for-byte from the scraped text — no paraphrasing.
- If the SERP is empty or the stub returns "no canned" results, set
  CONFIDENCE to "low" and explain.
"""


def _bright_data_toolset(stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        raise ImportError(
            "google-adk and mcp must be installed: pip install google-adk mcp"
        )

    if stub:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "gemini_bright_agent.mcp_stub"],
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    else:
        # Real Bright Data MCP server.
        params = StdioServerParameters(
            command="npx",
            args=["-y", "@brightdata/mcp"],
            env={
                **os.environ,
                "BRIGHTDATA_API_TOKEN": os.environ.get("BRIGHTDATA_API_TOKEN", ""),
            },
        )
    return McpToolset(connection_params=StdioConnectionParams(server_params=params))


def build_agent(model: str = "gemini-2.5-flash", stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        return None
    return LlmAgent(
        model=model,
        name="gemini_bright_agent",
        instruction=SYSTEM_PROMPT,
        tools=[_bright_data_toolset(stub=stub)],
    )
