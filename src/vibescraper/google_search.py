from googleapiclient.discovery import build
from vibescraper.config import GOOGLE_API_KEY, GOOGLE_CSE_ID


def google_search(query, num_results=20):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    results = []
    start = 1
    while len(results) < num_results:
        batch_size = min(10, num_results - len(results))
        try:
            res = service.cse().list(
                q=query,
                cx=GOOGLE_CSE_ID,
                num=batch_size,
                start=start
            ).execute()
            items = res.get("items", [])
            for item in items:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
            if len(items) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print(f"Google search API error: {e}")
            break
    print(f"Fetched {len(results)} results for query '{query}'")
    return results
