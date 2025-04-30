# vibescraper

**vibescraper** is a Python utility that generates an AI summary of web results based on a search query.

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
from vibescraper import vibe_search

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
