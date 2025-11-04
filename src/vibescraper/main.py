from vibescraper.vibe_search import vibe_search
from vibescraper.google_search import google_search
from vibescraper.brave_search import brave_search, brave_summary
import asyncio
import sys

def main():

    query = "What are some of the most highly rated authentic chinese restaurants in london as of 2025?"

    print(query)
    #results = asyncio.run(vibe_search(query))
    results = asyncio.run(brave_summary(query))
    
    # for url in results:
    #     print(url)
    #
    # 
#    results = google_search(query, 10)
    print(results)

if __name__ == "__main__":
    main()
