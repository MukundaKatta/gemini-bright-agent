"""gemini-bright-agent dashboard."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gemini_bright_agent.runner import ask  # noqa: E402


st.set_page_config(page_title="gemini-bright-agent", layout="wide", page_icon=":mag_right:")
st.title("gemini-bright-agent")
st.caption(
    "Web-research agent on Google Cloud Agent Builder (ADK) + Gemini 2.5, "
    "wired to the Bright Data MCP server. Cites sources verbatim. Apache 2.0."
)

with st.sidebar:
    st.header("Ask the web")
    question = st.text_area(
        "Your research question",
        value="Anthropic Claude latest release notes 2026",
        height=120,
    )
    model = st.selectbox(
        "Gemini model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        index=0,
    )
    stub = st.toggle(
        "Use stub Bright Data MCP",
        value=True,
        help="On = local stub with canned SERPs + scraped pages. Off = real Bright Data account (set BRIGHTDATA_API_TOKEN).",
    )
    run = st.button("Run research", type="primary", use_container_width=True)
    st.divider()
    st.caption(
        f"Project: `{os.getenv('GOOGLE_CLOUD_PROJECT', 'not-set')}`  "
        f"Vertex AI: `{os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')}`"
    )

st.markdown(
    """
The agent walks these Bright Data MCP tools to answer research questions:
- **search_engine** for the SERP (Google / Bing / DuckDuckGo)
- **scrape_page** for the Web Unlocker fetch (anti-bot bypass + rendered HTML)
- **extract_text** to pull clean text from a previously-scraped page
- **web_data_lookup** for Bright Data's structured datasets (LinkedIn, e-com, etc.)
"""
)

if run:
    with st.status("Running Vertex AI Gemini...", expanded=True) as status:
        t0 = time.perf_counter()
        try:
            resp = ask(question, stub=stub, model=model)
        except Exception as e:  # pragma: no cover
            status.update(label=f"Error: {e}", state="error")
            st.exception(e)
            st.stop()
        elapsed = (time.perf_counter() - t0) * 1000
        status.update(label=f"Done in {elapsed:.0f} ms", state="complete")

    st.subheader("Research answer")
    st.markdown(resp.final_text or "_(no final response)_")

    with st.expander(f"Agent event trace ({len(resp.events)} events)"):
        for i, ev in enumerate(resp.events):
            st.markdown(f"**{i}.** author=`{ev.get('author')}` final=`{ev.get('is_final')}`")
            text = ev.get("text") or ""
            if text:
                st.code(text[:1500], language=None)
else:
    st.info("Use the sidebar to fire a research question through the stub Bright Data MCP.")
