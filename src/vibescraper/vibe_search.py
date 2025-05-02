import requests
from vibescraper.openai_utils import get_embedding, generate
from vibescraper.google_search import google_search
from vibescraper.page_embedder import PageEmbeddingProcessor, CombinedResultsProcessor
from vibescraper.html_parser import process_html_with_semantic_chunker
from vibescraper.brave_search import brave_search
from vibescraper.db_schema import DBManager


from vibescraper.change_search_api import search_engine

# --------- HTML FETCHING ---------


def fetch_html(url):

    try:
        resp = requests.get(url, timeout=10, headers={
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

# --------- Vibe search scrape and summarize ---------


async def vibe_search(query, text_model='gpt-4o', embedding_model='small', dimensions=1536, top_k=5, domain_count=5):
    """
    Args: 
        query - search string
        text_model - the text generation model used for summaries and query expansion.
        embedding_model - embedding model size: small, large, legacy. default  = small
        dimensions - embedding dimensions. default 1536
        top_k - the number of top similar chunks to get in vector search/
        domain_count - the number of domains to search

    Returns an AI summary of the search results from the scraped domains.

    """

    db = DBManager()
    db.create_tables()

    print(f"Starting {search_engine} search: {query}")

    if search_engine == 'brave':
        urls = await brave_search(query, count=domain_count)
    else:
        search_results = google_search(query, num_results=domain_count)
        urls = [r["link"] for r in search_results]

    combined_processor = CombinedResultsProcessor(query, text_model=text_model, embedding_model=embedding_model, dimensions=dimensions, top_k=top_k)

    for url in urls:
        html = fetch_html(url)

        with open('searched_urls.txt', '+a') as f:
            f.write('\n')
            f.write(url)

        if not html:
            continue

        print(f"\nProcessing: {url}")
        chunks = process_html_with_semantic_chunker(html)

        page_processor = PageEmbeddingProcessor(
            url,
            query,
            db,
            combined_processor.operation_id,
            text_model, 
            embedding_model,
            dimensions,
            top_k
        )

        await page_processor.process_chunks(chunks)

        page_processor.save_to_json()
        combined_processor.add_page_results(page_processor)

    await combined_processor.process_combined_results()
    combined_processor.save_to_json()

    return combined_processor.combined_summary
