from openai import OpenAI
from vibescraper.config import client
import tiktoken


### Embeddings
"""

    OpenAI Embedding Utilities

"""
encoding_name = 'cl100k_base'
class EmbeddingModels:
    large = "text-embedding-3-large"
    small = "text-embedding-3-small"
    legacy = "text-embedding-ada-002"

def truncate_to_token_limit(text, model):

    max_tokens = 8191
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    length = len(tokens)

    if length <= max_tokens:
        return text

    print(f'Chunk too large ({length}), truncating to 8191 tokens')
    truncated_tokens = tokens[:max_tokens]
    truncated_text = encoding.decode(truncated_tokens)
    return truncated_text


async def get_embedding(text, model='small', dimensions=3072, encoding_format="float"):

    if model == 'small':
        model = EmbeddingModels.small
        if dimensions > 1536:
            dimensions = 1536

    if model == 'large':
        model = EmbeddingModels.large

    if model == 'legacy':
        model = EmbeddingModels.legacy
        if dimensions > 1536:
            dimensions = 1536

    truncated_text = truncate_to_token_limit(text, model)

    response = client.embeddings.create(
        input=truncated_text,
        model=model,
        encoding_format=encoding_format,
        dimensions=dimensions
    )
    return response.data[0].embedding



### Text Generator
"""

    OpenAI Text Generation Utilities

"""


class TextModels:
    smarter = "gpt-4.1"
    o4mini = "o4-mini"
    latest = "gpt-4o"
    latest_mini = "gpt-4o-mini"
    previous = "gpt-4-turbo-preview"
    previous1 = "gpt-4-1106-preview"
    legacy = "gpt-4"
    og = "gpt-4-0314"
    alpha = "gpt-4o-64k-output-alpha"
    turbo4 = "gpt-4-turbo"
    hipster = "gpt-4o"
    hipster_latest = "gpt-4o-2024-08-06"
    hipster_mini = "gpt-4o-mini"
    turbo35 = "gpt-3.5-turbo"
    preview45 = "gpt-4.5-preview"
    o1 = "o1"
    o1prevew = "o1-preview"
    o1mini = "o1-mini"
    o3mini = "o3-mini"
    o3 = "o3"
    nano41 = "gpt-4.1-nano"


async def generate(system_message, prompt, model=TextModels.latest):
    messages = []
    messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=messages
        )

        return response.choices[0].message.content


    except Exception as e:
        print(e)
