"""Stub Bright Data MCP server.

Mirrors the official Bright Data MCP server's tool surface:
  - `search_engine` — SERP API (Google / Bing / DuckDuckGo)
  - `scrape_page`   — Web Unlocker (anti-bot bypass, returns rendered HTML)
  - `extract_text`  — pulls clean text from a scraped page
  - `web_data_lookup` — Bright Data's structured web datasets (companies,
    Linkedin profiles, e-commerce, etc.)

Returns canned, realistic responses so judges can reproduce the demo
without provisioning a Bright Data account. Real Bright Data MCP swap is
one env-var change (BRIGHTDATA_API_TOKEN) — the agent code is unchanged.

Run with: python -m gemini_bright_agent.mcp_stub

Submission: lablab.ai · Bright Data AI Agents Web Data Hackathon
            (build window 2026-05-25 → 2026-05-30)
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Canned SERP + scrape + dataset data
# ---------------------------------------------------------------------------


# A canned SERP for the query: "Anthropic Claude latest release notes 2026"
_SERPS: dict[str, list[dict[str, Any]]] = {
    "Anthropic Claude latest release notes 2026": [
        {
            "rank":    1,
            "title":   "Claude 4.7 release notes — Anthropic",
            "url":     "https://www.anthropic.com/news/claude-4-7-release-notes",
            "snippet": "Claude 4.7 (Sonnet, Haiku, Opus) shipped on 2026-04-21 with extended context, "
                       "improved tool use, and the new agentic mode. Latency drops 22% vs 4.6.",
            "domain":  "anthropic.com",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    2,
            "title":   "What's new in Anthropic's API · May 2026 — Anthropic Engineering Blog",
            "url":     "https://www.anthropic.com/news/api-changelog-may-2026",
            "snippet": "Files API GA, prompt caching defaults to 1h TTL, batch API now supports streaming. "
                       "Memory tool exits preview.",
            "domain":  "anthropic.com",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    3,
            "title":   "Built with Opus 4.7 · Cerebral Valley recap",
            "url":     "https://cerebralvalley.ai/posts/built-with-opus-4-7-recap",
            "snippet": "Anthropic's 48-hour hackathon at Cerebral Valley wrapped April 26 with 312 teams "
                       "and a $50K prize pool. Three winners ship next month.",
            "domain":  "cerebralvalley.ai",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    4,
            "title":   "Claude 4.7 vs GPT-5 head-to-head — Latent Space",
            "url":     "https://www.latent.space/p/claude-4-7-vs-gpt-5-benchmarks",
            "snippet": "Independent benchmark comparing Claude 4.7 Opus and GPT-5 on agent-tool-use tasks. "
                       "Claude leads on long-context retrieval, GPT-5 leads on math.",
            "domain":  "latent.space",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    5,
            "title":   "Claude prompt-caching guide — Anthropic docs",
            "url":     "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching",
            "snippet": "Cache up to four blocks per request, 1-hour TTL by default, 5-minute TTL on the "
                       "ephemeral tier. New `cache_creation_input_tokens` metric in usage.",
            "domain":  "docs.anthropic.com",
            "fetched_at": NOW.isoformat(),
        },
    ],
    "Anthropic CEO Dario Amodei latest interview 2026": [
        {
            "rank":    1,
            "title":   "Dario Amodei on superintelligence timelines — Hard Fork (NYT)",
            "url":     "https://www.nytimes.com/podcasts/hard-fork/dario-amodei-may-2026",
            "snippet": "Anthropic CEO Dario Amodei talks 2027 timelines, the company's $50B-revenue target, "
                       "and why he thinks RSP-level ASL-4 is 18 months out. Interview aired May 12, 2026.",
            "domain":  "nytimes.com",
            "fetched_at": NOW.isoformat(),
        },
    ],
}


_SCRAPED_PAGES: dict[str, dict[str, Any]] = {
    "https://www.anthropic.com/news/claude-4-7-release-notes": {
        "url":     "https://www.anthropic.com/news/claude-4-7-release-notes",
        "title":   "Claude 4.7 release notes",
        "status":  200,
        "rendered_chars": 8421,
        "text_excerpt": (
            "We're shipping Claude 4.7 today, an across-the-board upgrade to our model family. "
            "Three SKUs ship simultaneously: Sonnet, Haiku, and Opus. All three include extended "
            "context to 1M tokens with prompt caching, improved structured-tool-use accuracy, and "
            "a new 'agentic mode' that automatically retries failed tool calls with a self-repair "
            "step. Latency on Sonnet is 22% lower than 4.6 at the p95 measured across 100k "
            "production requests. Opus 4.7 ships with the new 'thinking' budget controls — "
            "developers can cap reasoning tokens per turn. Pricing is unchanged from 4.6."
        ),
        "fetched_at": NOW.isoformat(),
        "unlocked_by_brightdata": True,
    },
    "https://www.anthropic.com/news/api-changelog-may-2026": {
        "url":     "https://www.anthropic.com/news/api-changelog-may-2026",
        "title":   "What's new in the Anthropic API · May 2026",
        "status":  200,
        "rendered_chars": 5612,
        "text_excerpt": (
            "The Files API is now generally available. Upload up to 100 MB per file, share files "
            "across requests, automatic 30-day retention. The Memory tool exits preview today; "
            "developers can give Claude a persistent scratchpad bounded by a token budget. "
            "Prompt caching defaults to a 1-hour TTL across all tiers. The Batch API now supports "
            "streaming partial results back as each batched request completes."
        ),
        "fetched_at": NOW.isoformat(),
        "unlocked_by_brightdata": True,
    },
}


_DATASETS: dict[str, list[dict[str, Any]]] = {
    # Bright Data has dataset endpoints for, e.g., LinkedIn company pages.
    "linkedin_company:Anthropic": [
        {
            "company":         "Anthropic",
            "linkedin_url":    "https://www.linkedin.com/company/anthropicresearch",
            "headquarters":    "San Francisco, CA, United States",
            "industry":        "AI / Research",
            "employee_count":  1_842,
            "founded":         2021,
            "specialties":     ["LLMs", "AI Safety", "Constitutional AI", "RLHF"],
            "fetched_at":      NOW.isoformat(),
        },
    ],
}


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------


def search_engine_response(query: str, engine: str = "google") -> dict[str, Any]:
    results = _SERPS.get(query, [])
    if not results:
        # Soft fallback so the agent can still reason about an unknown query.
        results = [{
            "rank":    1,
            "title":   f"(stub) no canned SERP for {query!r}",
            "url":     "",
            "snippet": "Bright Data stub: this query has no canned results. "
                       "In production the real Bright Data SERP API would return "
                       "live results from the chosen engine.",
            "domain":  "stub",
            "fetched_at": NOW.isoformat(),
        }]
    return {
        "query":     query,
        "engine":    engine,
        "result_count": len(results),
        "results":   results,
    }


def scrape_page_response(url: str) -> dict[str, Any]:
    rec = _SCRAPED_PAGES.get(url)
    if rec is None:
        return {
            "url":    url,
            "status": 200,
            "rendered_chars": 0,
            "text_excerpt": (
                f"(stub) no canned scrape for {url}. In production the real "
                "Bright Data Web Unlocker would return the rendered page text "
                "after bypassing any anti-bot defences."
            ),
            "unlocked_by_brightdata": True,
            "fetched_at": NOW.isoformat(),
        }
    return rec


def extract_text_response(url: str, css_selector: str | None = None) -> dict[str, Any]:
    """Convenience tool: extract clean text from a previously-scraped page."""
    page = _SCRAPED_PAGES.get(url)
    if page is None:
        return {"error": f"page not scraped yet: {url!r} — call scrape_page first"}
    return {
        "url":          url,
        "css_selector": css_selector or "body",
        "text":         page["text_excerpt"],
        "char_count":   len(page["text_excerpt"]),
    }


def web_data_lookup_response(dataset: str, key: str) -> dict[str, Any]:
    lookup_key = f"{dataset}:{key}"
    rec = _DATASETS.get(lookup_key)
    if rec is None:
        return {"error": f"unknown dataset entry {lookup_key!r}",
                "known": list(_DATASETS.keys())}
    return {"dataset": dataset, "key": key, "records": rec, "count": len(rec)}


# ---------------------------------------------------------------------------
# MCP server wiring
# ---------------------------------------------------------------------------


def _make_server() -> Server:
    server = Server("bright-data-stub")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="search_engine",
                 description=("Run a SERP query through Bright Data's SERP API. "
                              "Returns the top results with rank, title, url, "
                              "snippet, and domain. Engine defaults to google."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "query":  {"type": "string"},
                                  "engine": {"type": "string",
                                              "enum": ["google", "bing", "duckduckgo"],
                                              "default": "google"},
                              },
                              "required": ["query"]}),
            Tool(name="scrape_page",
                 description=("Fetch a URL through Bright Data's Web Unlocker. "
                              "Returns the rendered HTML + a text excerpt + the "
                              "anti-bot status. Use this when the SERP snippet "
                              "isn't enough."),
                 inputSchema={"type": "object",
                              "properties": {"url": {"type": "string"}},
                              "required": ["url"]}),
            Tool(name="extract_text",
                 description=("Extract clean text from a previously-scraped page. "
                              "Optionally narrow by CSS selector."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "url":          {"type": "string"},
                                  "css_selector": {"type": "string"},
                              },
                              "required": ["url"]}),
            Tool(name="web_data_lookup",
                 description=("Look up a structured record from Bright Data's "
                              "web datasets (LinkedIn companies, Amazon "
                              "products, etc.). Returns canonical fields with "
                              "verbatim values."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "dataset": {"type": "string"},
                                  "key":     {"type": "string"},
                              },
                              "required": ["dataset", "key"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        a = arguments
        if name == "search_engine":
            payload = search_engine_response(a.get("query", ""),
                                              a.get("engine", "google"))
        elif name == "scrape_page":
            payload = scrape_page_response(a.get("url", ""))
        elif name == "extract_text":
            payload = extract_text_response(a.get("url", ""),
                                            a.get("css_selector"))
        elif name == "web_data_lookup":
            payload = web_data_lookup_response(a.get("dataset", ""),
                                                a.get("key", ""))
        else:
            payload = {"error": f"unknown tool {name!r}"}
        return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

    return server


async def _main() -> None:
    server = _make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
