import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


#NOTE: After installing you must run 'check-api-keys' in the terminal to import your api keys from your environment correctly.

# --- API key environment variable accessors appended by installer ---
import os
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
search_engine = 'google'
