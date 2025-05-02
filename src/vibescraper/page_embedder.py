from typing import Dict, List, Optional, Union
import numpy as np
import asyncio
from vibescraper.openai_utils import get_embedding, generate
from vibescraper.json_utils import save_page_json, save_combined_json
import re
import ast
import json
import os
import inspect
import sys
import subprocess
from vibescraper.timer_decorator import timer


class PageEmbeddingProcessor:
    """
    Process semantic chunks from a single page, generate embeddings,
    and find top K most similar chunks to a search query.
    """

    def __init__(self, page_url, search_query=None, db_manager=None, operation_id=None, text_model='gpt-4o', embedding_model='small', dimensions=1536, top_k=5):
        self.page_url = page_url
        self.search_query = search_query
        self.chunks = []
        self.embeddings = []
        self.query_embedding = None
        self.top_results = None
        self.page_summary = ""
        self.db_manager = db_manager
        self.operation_id = operation_id
        self.page_id = None
        self.model = embedding_model
        self.text_model = text_model
        self.dimensions = dimensions
        self.top_k = top_k

        if db_manager and operation_id:
            try:
                self.page_id = db_manager.create_page(operation_id, page_url)
                print(f"Created page record with ID: {self.page_id}")
            except Exception as e:
                print(f"Error creating page record: {e}")

    async def process_chunks(self, chunks):
        """Process semantic chunks from a single page"""
        self.chunks = chunks

        self.embeddings = []
        for chunk in chunks:
            embedding = await get_embedding(chunk, model=self.model, dimensions=self.dimensions)
            self.embeddings.append(embedding)


        if self.search_query:

            query_transform_system_msg = "You are an expert research assistant. Given a short search engine query, expand it into a detailed, context-rich statement that clearly explains the user's information need. Restate the query as a full sentence or paragraph. Add synonyms and related concepts to broaden the scope. Clarify any ambiguous terms or phrases. Include any relevant background or context that might help a search engine or AI system find the most relevant information."

            query_transform_prompt = f"Original Query: '{self.search_query}'. Expanded, Detailed Version:"

            expanded_query = await generate(query_transform_system_msg, query_transform_prompt, model=self.text_model)
            print('Expanded query: ', expanded_query)

            self.query_embedding = await get_embedding(expanded_query, model=self.model, dimensions=self.dimensions)
            self.top_results = await self._find_top_similar(self.query_embedding, k=self.top_k)

        return self.embeddings

    async def _find_top_similar(self, query_embedding, k=5):
        """Find top k chunks most similar to query embedding"""
        if not self.embeddings:
            return []

        similarities = []
        for i, emb in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, emb)
            similarities.append((i, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)

        top_k = similarities[:k]
        results = []

        for i, (idx, sim) in enumerate(top_k):
            results.append({
                'chunk_text': self.chunks[idx],
                'embedding': self.embeddings[idx],
                'similarity': float(sim),
                'rank': i + 1
            })


        summary_str = f'Given the following query: {
            self.search_query}, please summarize the following information scraped from {self.page_url}: '

        chunk_string = ''
        for result in results:
            chunk_string += f', {result["chunk_text"]}'

        summary_str += chunk_string

        system_message = 'You goal is to summarize a given set of scraped web data into a summary, based on a query. Create a fully referenced summary such that any information contained in the summary has a sourced reference in brackets as follows: (reference: <quote>, source: <url>). Note, the <quote> MUST be an actual snippet from the given source material, and the source <url> must be the exact given source url that snippet was taken from.'

        self.page_summary = await generate(system_message, summary_str, model=self.text_model)
        print('Generated page summary for: ', self.page_url)
        print('\n')
        print(self.page_summary)

        if self.db_manager and self.page_id and self.operation_id:
            try:
                # Update page summary
                self.db_manager.update_page_summary(
                    self.page_id, self.page_summary)

                # Store chunks
                for result in results:
                    self.db_manager.create_chunk(
                        self.page_id,
                        self.operation_id,
                        result['chunk_text'],
                        result['embedding'],
                        result['similarity'],
                        result['rank']
                    )
            except Exception as e:
                print(f"Error storing data in database: {e}")

        return results



    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        if not isinstance(a, np.ndarray):
            a = np.array(a)
        if not isinstance(b, np.ndarray):
            b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def save_to_json(self, output_dir='./results'):
        """Save page results to JSON file (completely separate from DB operations)"""
        if self.top_results:
            filepath = save_page_json(
                self.page_url,
                self.page_summary,
                self.top_results,
                output_dir
            )
            if filepath:
                print(f"Saved page results to: {filepath}")
                return filepath
        return None


class CombinedResultsProcessor:
    """
    Process the top results from all pages and perform a final similarity search.
    """

    def __init__(self, search_query, db_manager=None, text_model='gpt-4o', embedding_model='small', dimensions=1536, top_k=5):
        self.search_query = search_query
        self.query_embedding = None
        self.page_results = []
        self.combined_results = None
        self.combined_summary = ''
        self.top_results = []
        self.all_embeddings = []
        self.all_chunks = []
        self.page_urls = []

        # Database related attributes
        self.db_manager = db_manager
        self.operation_id = None
        self.model = embedding_model
        self.text_model = text_model
        self.dimensions = dimensions
        self.top_k = top_k

        if db_manager:
            try:
                self.operation_id = db_manager.create_operation(search_query)
                print(f"Created operation with ID: {self.operation_id}")
            except Exception as e:
                print(f"Error creating operation record: {e}")

    def add_page_results(self, page_processor):
        self.page_results.append(page_processor)

    async def process_combined_results(self):
        if not self.query_embedding:

            self.query_embedding = self.page_results[0].query_embedding #await get_embedding(self.search_query, model=self.model, dimensions=self.dimensions)

        for page in self.page_results:
            if not page.top_results:
                continue

            for result in page.top_results:
                self.all_chunks.append(result['chunk_text'])
                self.all_embeddings.append(result['embedding'])
                self.page_urls.append(page.page_url)

        self.top_results = await self._find_top_similar(self.query_embedding, k=self.top_k)


    async def _find_top_similar(self, query_embedding, k=7):
        if not self.all_embeddings:
            return []

        similarities = []
        for i, emb in enumerate(self.all_embeddings):
            similarity = self._cosine_similarity(query_embedding, emb)
            similarities.append((i, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)

        top_k = similarities[:k]
        results = []

        for idx, sim in top_k:
            results.append({
                'chunk_text': self.all_chunks[idx],
                'embedding': self.all_embeddings[idx],
                'similarity': float(sim)
            })

        summary_str = f'Given the following query: {
            self.search_query}, please rewrite the following page summaries into a well documented and fully referenced report, no more than 1000 words long: '

        page_summary = next(
            (p.page_summary for p in self.page_results if p.page_url == self.page_urls[idx]), "")

        summary_str += page_summary

        system_message = 'You goal is to write a report no more than 1000 words long about a topic, given a query string and a set of summaries from source material. The summaries contain references. Please use these references to create a fully referenced report such that any information contained in the report has a sourced reference in brackets as follows: (reference: <quote>, source: <url>). Note, the <quote> MUST be an actual snippet from the given source material, and the source <url> must be the exact given source url that snippet was taken from.'


        self.combined_summary = await generate(system_message, summary_str, model=self.text_model)
        print('Generated combined summary: ')
        print('\n')
        print(self.combined_summary)

        if self.db_manager and self.operation_id:
            try:
                self.db_manager.update_operation_summary(
                    self.operation_id, self.combined_summary)
            except Exception as e:
                print(f"Error updating operation summary in database: {e}")

        pages_data = []
        for i, (idx, sim) in enumerate(similarities[:k]):
            page_summary = next(
                (p.page_summary for p in self.page_results if p.page_url == self.page_urls[idx]), "")

            pages_data.append({
                'rank': i+1,
                'url': self.page_urls[idx],
                'chunk_text': self.all_chunks[idx],
                'similarity': float(sim),
                'page_summary': page_summary,
            })

        self.combined_results = {
            'combined_summary': self.combined_summary,
            'pages': pages_data
        }

        return results

    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        if not isinstance(a, np.ndarray):
            a = np.array(a)
        if not isinstance(b, np.ndarray):
            b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def save_to_json(self, filepath=None):
        """Save combined results to JSON file (completely separate from DB operations)"""
        if self.combined_results:
            filepath = save_combined_json(
                self.search_query,
                self.combined_summary,
                self.combined_results['pages'],
                filepath
            )
            if filepath:
                print(f"Saved combined results to: {filepath}")
                return filepath
        return None
