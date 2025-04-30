import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

search_engine = 'brave' # else 'google'

#NOTE: After installing you must run 'check-api-keys' in the terminal to import your api keys from your environment correctly.
