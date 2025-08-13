import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

#search_engine = "google"
search_engine = "brave"
#NOTE: After installing you must run 'check-api-keys' in the terminal to import your api keys from your environment correctly.
