"""
Wraps Tavily search so the rest of the code doesn't need to know
which search API we're using under the hood. If you ever swap
Tavily for SerpAPI or something else, only this file changes.
"""
from tavily import TavilyClient
from config import TAVILY_API_KEY, SEARCH_RESULTS_PER_QUERY

client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str, max_results: int = SEARCH_RESULTS_PER_QUERY) -> list[dict]:
    """
    Returns a list of sources, each like:
    {"title": ..., "url": ..., "content": ...}
    'content' is Tavily's cleaned extract of the page — no manual scraping needed.
    """
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",   # deeper crawl = better content per source
        include_answer=False,
    )
    sources = []
    for r in response.get("results", []):
        sources.append({
            "title": r.get("title", "Untitled"),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        })
    return sources


if __name__ == "__main__":
    # Quick manual test — run: python tools/search_tool.py
    results = search_web("does coffee cause dehydration")
    for r in results:
        print(f"- {r['title']} ({r['url']})")
        print(f"  {r['content'][:150]}...\n")
