import os
import time
from urllib.parse import urljoin
import requests
from vibescraper.config import BRAVE_API_KEY

API_KEY = BRAVE_API_KEY

API_HOST = "https://api.search.brave.com"
API_PATH = {
    "web": urljoin(API_HOST, "res/v1/web/search"),
}
API_HEADERS = {
    "web": {
        "X-Subscription-Token": API_KEY,
        "Api-Version": "2023-10-11",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    }
}
API_TIMEOUT = 500
MAX_QUERY_CHARS = 400
MAX_QUERY_WORDS = 50


def validate_query_length(query: str) -> str:
    query = query.strip()
    if len(query) > MAX_QUERY_CHARS:
        query = query[:MAX_QUERY_CHARS]
    words = query.split()
    if len(words) > MAX_QUERY_WORDS:
        query = " ".join(words[:MAX_QUERY_WORDS])
    if not query:
        raise ValueError("Query must not be empty after trimming.")
    return query


def get_brave_search(
    query: str,
    count: int = 10,
    extra_snippets: int = 0,
    result_filter: str = None,
    min_remaining: int = 5  # threshold to start slowing down
):
    try:
        query = validate_query_length(query)
    except ValueError as ve:
        return f"Invalid query: {ve}"

    params_web = {
        "q": query,
        "count": count
    }
    if extra_snippets:
        params_web["extra_snippets"] = extra_snippets
    if result_filter:
        params_web["result_filter"] = result_filter

    try:
        resp_web = requests.get(
            API_PATH["web"],
            params=params_web,
            headers=API_HEADERS["web"],
            timeout=API_TIMEOUT
        )

    except Exception as e:
        return f"Web search failed: {str(e)}"

    if resp_web.status_code != 200:
        raw_text = resp_web.text
        return f"Web search failed: HTTP {resp_web.status_code}, content: {raw_text[:200]}"
    try:
        data_web = resp_web.json()
        return data_web

    except Exception as e:
        raw_text = resp_web.text
        return f"Web search returned non-JSON response: {str(e)}\nContent: {raw_text[:200]}"


async def brave_search(query: str, count: int = 10, extra_snippets: int = 0, result_filter: str = None):

    search_results = get_brave_search(
        query,
        count=count,
        extra_snippets=extra_snippets,
        result_filter=result_filter
    )

    return list(map(lambda x: x.get('url'), search_results['web']['results']))
