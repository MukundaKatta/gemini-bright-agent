# Bright Data AI Agents Web Data Hackathon — lablab.ai submission

Lablab event: https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon
Build window: 2026-05-25 → 2026-05-30
Demos: 2026-05-31

## Elevator pitch
A Gemini-powered research analyst that uses Bright Data's MCP server
(SERP API + Web Unlocker + structured datasets) to answer plain-English
research questions with cited sources, verbatim quotes, and a
confidence note.

## Rule compliance

| Rule | How we meet it |
|---|---|
| Uses Bright Data | MCP tool surface matches the official `@brightdata/mcp` (SERP, Web Unlocker, structured datasets); stub for demos, real account via `BRIGHTDATA_API_TOKEN` |
| AI agent (not just a script) | `google.adk.agents.LlmAgent` with Gemini 2.5 Flash on Vertex AI walks the tools across multiple turns and self-evaluates source quality |
| Newly created during the contest period | Repo init within the build window (2026-05-25 → 2026-05-30) |
| Original work | Standalone repo, Apache 2.0 |
| Runs on the web | Streamlit dashboard, Cloud Run deployable |

## Description

`gemini-bright-agent` treats every research question as a SERP →
unlock → cite loop. You ask "Anthropic Claude latest release notes
2026" and the agent walks the Bright Data MCP tools:

1. `search_engine(query, engine)` — pull the top SERP results.
2. Pick the most authoritative sources (prefer first-party).
3. `scrape_page(url)` — fetch the rendered page through the Web Unlocker
   (anti-bot bypass, returns `unlocked_by_brightdata: true`).
4. `extract_text(url, css_selector)` — clean text for citation.
5. `web_data_lookup(dataset, key)` — if the question touches a structured
   record (company, profile, product), pull the canonical dataset row.

The agent's answer is a 5-section report (ANSWER / SOURCES / KEY
QUOTES / CONFIDENCE / NEXT STEP). Every number, date, version string,
and quoted line must be copied verbatim from a tool result — the
system prompt rejects paraphrasing inside KEY QUOTES.

## Built with
python, gemini, gemini-2-5, vertex-ai, google-cloud-agent-builder,
agent-development-kit, mcp, model-context-protocol, bright-data,
bright-data-mcp, web-unlocker, serp-api, streamlit, google-cloud-run,
apache-2

## Try it out
- Code repo: https://github.com/MukundaKatta/gemini-bright-agent
- Live demo (Cloud Run): pinned after deploy
- Demo video (YouTube unlisted): pinned after upload
