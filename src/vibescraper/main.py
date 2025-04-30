from vibescraper.vibe_search import vibe_search
import asyncio
import sys

def main():
    if sys.argv:
        query = sys.argv[1]
    else:
        query = "What are some of the most highly rated authentic chinese restaurants in london as of 2025?"

    print(query)
    results = asyncio.run(vibe_search(query, domain_count=10))
    print(results)

if __name__ == "__main__":
    main()
