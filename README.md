# vibescraper

**vibescraper** is a Python utility that generates an AI summary of web results based on a search query.

This is very much a work in progress. The results of each search may vary depending on how well the parser handles the pages. If you find that some results are not sufficient, you can try increasing the number of sites to return in the search api using the domain_count argument in the vibe_search function.

The number of sites will slow the operation down, so you may need to experiment and find the optimal tradeoff that suits your needs, between speed and accuracy of results.

In order to select the search api you need to run the following in your projects python environment:
    - change-search-api <google/brave>


The output files and folders from the search operations can be used or discarded as you need.
In future I may change this so that the datbase can be saved or discarded according to an argument flag in the vibe_search function or as part of another python config script.

---





## How it works

- **Web Search:** Searched the web using search engine API.
- **Semantic Chunking:** Extracts html from each url in the search results, then divides the html page content into meaningful chunks.
- **Embedding Generation:** Generate vector embeddings for each chunk using openai embedding models.
- **Similarity Search:** Find the most relevant content chunks for a given search query.
- **AI Summarization:** Generates concise summaries of relevant content, then combines all summaries into a combined summary.
- **JSON Export:** Saves results and summaries as JSON files for easy inspection or downstream use.

---

## Installation

Install via pip (from PyPI):

`pip install vibescraper`

Or install locally with Poetry:

`poetry install`

NOTE:
You need either a Beave or Google search API key to use this, as well as an open AI API key.


to import the keys into config.py after installing run:
    `check-api-keys`

in your python project env.

---

## Requirements

- Python 3.12+
- [OpenAI API key](https://platform.openai.com/) (for embedding and summarization)
- Other dependencies: numpy, requests, beautifulsoup4, pandas, sqlalchemy, openai, tiktoken, google-api-python-client, html5lib

---

## Usage

- Install the package into your python project, then import the vibe_search function

```python
from vibescraper.vibe_search import vibe_search

ai_summary = await vibe_search(query='What is the state of the software development job market in 2025?', domain_count=10, text_model='gpt-4o')
```

## Environment Variables

You must set your OpenAI API key (and either a Google or Brave yea keys)  as environment variables

---

## License

MIT License

---

## Contributing

Pull requests and issues are welcome!

---
