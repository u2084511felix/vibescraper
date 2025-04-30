from bs4 import BeautifulSoup, Tag
from types import NoneType
import re

class HTMLSemanticChunker:
    """
    A class that chunks HTML content based on semantic structure rather than arbitrary length limits.
    Splits content at logical boundaries like headers while preserving the integrity of lists, tables, etc.
    """

    def __init__(self, headers_to_split_on=None, elements_to_preserve=None, debug=False):
        """
        Initialize a semantic HTML chunker

        Args:
            headers_to_split_on: List of header tags to use as chunk boundaries (e.g., ['h1', 'h2'])
            elements_to_preserve: List of elements to keep whole (e.g., ['table', 'ul', 'ol'])
            debug: Whether to print debug information
        """
        self.headers_to_split_on = headers_to_split_on or [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        self.elements_to_preserve = elements_to_preserve or [
            'table', 'ul', 'ol', 'code', 'pre']
        self.debug = debug

        # Remove headers from junk tags to properly process them
        self.minimal_junk_tags = [tag for tag in ['script', 'style', 'noscript', 'iframe', 'svg', 'canvas']
                                  if tag not in self.headers_to_split_on and tag not in self.elements_to_preserve]

    def debug_print(self, message):
        """Print debug messages if debug is enabled"""
        if self.debug:
            print(message)

    def get_header_level(self, header_tag):
        """Get the level of a header tag (h1=1, h2=2, etc.)"""
        if header_tag[0] == 'h' and header_tag[1:].isdigit():
            return int(header_tag[1:])
        return 0

    def process_tag(self, tag, parent_headers=None):
        """
        Process a tag and its children, generating chunks based on semantic structure

        Args:
            tag: BeautifulSoup tag to process
            parent_headers: Headers from parent elements to include in context

        Returns:
            List of chunks with header context
        """
        if parent_headers is None:
            parent_headers = []

        if tag.name in self.minimal_junk_tags:
            return []

        if tag.name in self.elements_to_preserve:
            text = tag.get_text(strip=True)
            if text:
                return [{'tag': tag.name, 'headers': parent_headers.copy(), 'text': text}]
            return []

        # If this is a header, start a new chunk and update parent_headers for children
        if tag.name in self.headers_to_split_on:
            header_text = tag.get_text(strip=True)
            level = self.get_header_level(tag.name)

            # Update the header context based on hierarchical level
            new_headers = [
                h for h in parent_headers if self.get_header_level(h['tag']) < level]
            new_headers.append(
                {'tag': tag.name, 'text': header_text, 'level': level})

            # Process children with updated header context
            chunks = []
            for child in tag.children:
                if isinstance(child, Tag):
                    chunks.extend(self.process_tag(child, new_headers))

            # Add this header as its own chunk if it has no content
            if not chunks and header_text:
                chunks.append(
                    {'tag': tag.name, 'headers': parent_headers.copy(), 'text': header_text})

            return chunks

        # For content tags, check if they contain headers
        contains_header = any(header in [c.name for c in tag.find_all() if hasattr(c, 'name')]
                              for header in self.headers_to_split_on)

        # If it contains headers, process its children
        if contains_header:
            chunks = []
            for child in tag.children:
                if isinstance(child, Tag):
                    chunks.extend(self.process_tag(child, parent_headers))
            return chunks

        # Otherwise treat it as a leaf content node
        text = tag.get_text(strip=True)
        if text:
            return [{'tag': tag.name, 'headers': parent_headers.copy(), 'text': text}]

        return []

    def chunk_html(self, html):
        """
        Split HTML content into semantic chunks

        Args:
            html: Raw HTML content as string

        Returns:
            List of chunks with header context
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Clean up unwanted elements
        for tag_name in self.minimal_junk_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        chunks = []
        for tag in soup.body.children if soup.body else soup.children:
            if isinstance(tag, Tag):
                chunks.extend(self.process_tag(tag))

        # If no chunks were found, extract whatever text is available
        if not chunks:
            text = soup.get_text(strip=True)
            if text:
                chunks.append({'tag': 'body', 'headers': [], 'text': text})

        return chunks

    def format_chunks(self, chunks, include_headers=True):
        """
        Format chunks into user-friendly text blocks

        Args:
            chunks: List of chunk dictionaries from chunk_html
            include_headers: Whether to include header hierarchy in the output

        Returns:
            List of formatted text strings
        """
        formatted_chunks = []

        for chunk in chunks:
            if include_headers and chunk['headers']:
                # Add headers in hierarchical order
                header_texts = [h['text'] for h in sorted(
                    chunk['headers'], key=lambda x: x.get('level', 0))]
                context = " > ".join(header_texts)
                formatted_text = f"{context}\n{chunk['text']}"
                cleaned_text = re.sub(
                    r'\s+', ' ', formatted_text.replace('\n', ' ').replace('\t', ' '))
                formatted_text = cleaned_text
            else:
                formatted_text = chunk['text']
                cleaned_text = re.sub(
                    r'\s+', ' ', formatted_text.replace('\n', ' ').replace('\t', ' '))
                formatted_text = cleaned_text

            formatted_chunks.append(formatted_text)

        return formatted_chunks

    def merge_small_chunks(self, chunks, min_length=100):
        """
        Merge small chunks with the same header context

        Args:
            chunks: List of chunk dictionaries
            min_length: Minimum text length to consider a chunk "complete"

        Returns:
            List of merged chunks
        """
        if not chunks:
            return []

        merged = []
        current_chunk = chunks[0].copy()

        for chunk in chunks[1:]:
            # Check if headers match
            same_headers = (len(chunk['headers']) ==
                            len(current_chunk['headers']))
            if same_headers:
                for i, header in enumerate(chunk['headers']):
                    if i >= len(current_chunk['headers']) or header != current_chunk['headers'][i]:
                        same_headers = False
                        break

            # If headers match and current chunk is small, merge them
            if same_headers and len(current_chunk['text']) < min_length:
                current_chunk['text'] += f"\n{chunk['text']}"
            else:
                merged.append(current_chunk)
                current_chunk = chunk.copy()

        merged.append(current_chunk)
        return merged

    def split_html_by_semantics(self, html, merge_small=True, include_headers=True):
        """
        Main method to split HTML by semantic structure

        Args:
            html: HTML content as string
            merge_small: Whether to merge small chunks with the same context
            include_headers: Whether to include headers in the output text

        Returns:
            List of text chunks split by semantic structure
        """
        chunks = self.chunk_html(html)

        if merge_small:
            chunks = self.merge_small_chunks(chunks)

        return self.format_chunks(chunks, include_headers)


def process_html_with_semantic_chunker(html_content):
    chunker = HTMLSemanticChunker(
        headers_to_split_on=['h1', 'h2', 'h3', 'h4'],
        elements_to_preserve=['table', 'ul', 'ol', 'pre', 'code']
    )

    chunks = chunker.split_html_by_semantics(html_content)
    return chunks
