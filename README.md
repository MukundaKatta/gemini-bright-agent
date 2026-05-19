# gemini-bright-agent

A research-analyst agent built on **Google Cloud Agent Builder (ADK)**,
**Gemini 2.5**, and the **Bright Data MCP server**. Submission for the
**Bright Data AI Agents Web Data Hackathon** on lablab.ai (build window
2026-05-25 → 2026-05-30).

## What it does

The user gives the agent a research question that needs fresh web data.
The agent walks the Bright Data MCP tools — SERP search, Web Unlocker
scrape, text extraction, and structured-dataset lookup — and answers
with cited URLs, verbatim quotes, and a confidence note.

## Tool surface

The agent uses the standard Bright Data MCP tool surface — same as the
official [`@brightdata/mcp`](https://github.com/brightdata/mcp) npm
package — so the stub here is one env-var swap away from a real Bright
Data account.

- `search_engine(query, engine)` — SERP API (Google / Bing / DuckDuckGo)
- `scrape_page(url)` — Web Unlocker, anti-bot bypass, rendered HTML + text
- `extract_text(url, css_selector)` — clean text from a previously-scraped page
- `web_data_lookup(dataset, key)` — structured datasets (LinkedIn companies, Amazon products, etc.)

## Architecture

```
┌──────────────────────┐    ┌───────────────────────┐   ┌────────────────────────────┐
│ Streamlit dashboard  │──▶ │  ADK LlmAgent          │──▶│  Bright Data MCP server     │
│ on Cloud Run         │    │  Gemini 2.5 on Vertex  │   │  (stub for demos,           │
│                      │    │  AI                    │   │   real account via          │
│ "research my Q ..."  │    │                        │   │   BRIGHTDATA_API_TOKEN)     │
└──────────────────────┘    └───────────────────────┘   └────────────────────────────┘
```

## Output contract

The system prompt requires EXACTLY these labeled sections per answer:

```
ANSWER:      one-two sentences, every number/date/version copied verbatim from tools.
SOURCES:     bulleted URLs the agent actually consulted (not the whole SERP).
KEY QUOTES:  2-4 verbatim quotes pulled from the scraped pages, each tagged with its URL.
CONFIDENCE:  high / medium / low, with a one-sentence reason grounded in source quality.
NEXT STEP:   one concrete follow-up search.
```

Strict rule: every quantitative claim must come from a tool result. The
agent cites byte-for-byte, never paraphrases inside KEY QUOTES.

## Try it against a real Bright Data account

```sh
export BRIGHTDATA_API_TOKEN="brd_..."
pip install -e .
streamlit run app/dashboard.py
```

Untick "Use stub Bright Data MCP" in the sidebar. The agent now spawns
the official `@brightdata/mcp` server via `npx`.

## Tests

```sh
pip install -e ".[dev]"
pytest -q
```

The suite pins the research-chain contract: the top SERP result for the
canned query points to a URL `scrape_page` recognises, the verbatim "22%
latency drop" claim appears in both the SERP snippet and the scraped
page, and structured-dataset lookups return the expected employee count
for Anthropic.

## License

Apache 2.0. Standalone repo created during the Bright Data Web Data
Hackathon contest period (2026-05-25 → 2026-05-30).
