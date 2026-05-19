from gemini_bright_agent.mcp_stub import (
    _SERPS,
    _SCRAPED_PAGES,
    _DATASETS,
    extract_text_response,
    scrape_page_response,
    search_engine_response,
    web_data_lookup_response,
)


def test_serps_seeded():
    assert "Anthropic Claude latest release notes 2026" in _SERPS
    assert len(_SERPS["Anthropic Claude latest release notes 2026"]) == 5


def test_search_engine_known_query():
    payload = search_engine_response("Anthropic Claude latest release notes 2026")
    assert payload["engine"] == "google"
    assert payload["result_count"] == 5
    titles = [r["title"] for r in payload["results"]]
    assert any("4.7" in t for t in titles)


def test_search_engine_unknown_query_fallback():
    payload = search_engine_response("some unrelated query")
    assert payload["result_count"] == 1
    assert "stub" in payload["results"][0]["title"].lower()


def test_search_engine_engine_param():
    payload = search_engine_response("Anthropic Claude latest release notes 2026", engine="bing")
    assert payload["engine"] == "bing"


def test_scrape_page_known_url():
    payload = scrape_page_response(
        "https://www.anthropic.com/news/claude-4-7-release-notes"
    )
    assert payload["status"] == 200
    assert payload["unlocked_by_brightdata"] is True
    assert "Claude 4.7" in payload["text_excerpt"]
    assert "22%" in payload["text_excerpt"]


def test_scrape_page_unknown_url_returns_stub():
    payload = scrape_page_response("https://example.com/unknown")
    assert payload["status"] == 200
    assert payload["rendered_chars"] == 0
    assert payload["unlocked_by_brightdata"] is True


def test_extract_text_requires_prior_scrape():
    payload = extract_text_response("https://example.com/never-fetched")
    assert "error" in payload


def test_extract_text_returns_clean_text():
    url = "https://www.anthropic.com/news/api-changelog-may-2026"
    payload = extract_text_response(url)
    assert "Files API" in payload["text"]
    assert payload["char_count"] > 100


def test_web_data_lookup_returns_anthropic_record():
    payload = web_data_lookup_response("linkedin_company", "Anthropic")
    assert payload["count"] == 1
    rec = payload["records"][0]
    assert rec["company"] == "Anthropic"
    assert rec["employee_count"] == 1842
    assert "Constitutional AI" in rec["specialties"]


def test_web_data_lookup_unknown_returns_error_with_known_list():
    payload = web_data_lookup_response("linkedin_company", "NotExist")
    assert "error" in payload
    assert any("Anthropic" in k for k in payload["known"])


def test_research_story_chain_is_consistent():
    """The agent's killer move: SERP → scrape → extract → cite verbatim.

    The chain stays consistent: the top result from search_engine points to
    a URL that scrape_page recognises, and the text excerpt matches the
    SERP snippet's claim (22% latency drop, Claude 4.7).
    """
    serp = search_engine_response("Anthropic Claude latest release notes 2026")
    top_url = serp["results"][0]["url"]
    scrape = scrape_page_response(top_url)
    extract = extract_text_response(top_url)

    assert scrape["unlocked_by_brightdata"] is True
    # The 22% latency claim must appear verbatim in both SERP snippet AND
    # the scraped page — that's what the agent will cite.
    assert "22%" in serp["results"][0]["snippet"]
    assert "22%" in extract["text"]
