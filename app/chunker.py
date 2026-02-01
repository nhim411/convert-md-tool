"""
Markdown Chunker Module
Splits markdown text into semantic chunks based on headers.
Optimized for RAG (Retrieval-Augmented Generation) ingestion.
"""

import re
from typing import List, Dict, Any

class MarkdownChunker:
    """
    Splits markdown content into chunks based on headers.
    """

    def __init__(self, chunk_level: int = 2):
        """
        Initialize chunker.

        Args:
            chunk_level: Maximum header level to split by (1 or 2).
                         1 = Split by H1 only.
                         2 = Split by H1 and H2.
        """
        self.chunk_level = chunk_level

    def chunk_text(self, text: str, source_file: str = "") -> List[Dict[str, Any]]:
        """
        Chunk the markdown text.

        Args:
            text: Markdown content
            source_file: Name of the source file (for metadata)

        Returns:
            List of chunks (dicts with header, content, metadata)
        """
        lines = text.split('\n')
        chunks = []
        current_chunk = {
            "source": source_file,
            "header": "",
            "content": [],
            "level": 0
        }

        # Regex for headers
        # Matches # Title, ## Title
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')

        for line in lines:
            match = header_pattern.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                # If we hit a header logic depends on configured chunk_level
                # For now, simple logic: if level <= chunk_level, start new chunk

                if level <= self.chunk_level:
                    # Save current chunk if it has content
                    if current_chunk["content"]:
                        # Join content and add
                        current_chunk["content"] = "\n".join(current_chunk["content"]).strip()
                        if current_chunk["content"]: # Only add if not empty
                            chunks.append(current_chunk)

                    # Start new chunk
                    current_chunk = {
                        "source": source_file,
                        "header": title,
                        "content": [line], # Include header in content context? Yes usually
                        "level": level
                    }
                else:
                    # Higher level header (e.g. H3 when split by H2) - treat as content
                    current_chunk["content"].append(line)
            else:
                # Regular line
                current_chunk["content"].append(line)

        # Add last chunk
        if current_chunk["content"]:
            current_chunk["content"] = "\n".join(current_chunk["content"]).strip()
            if current_chunk["content"]:
                chunks.append(current_chunk)

        # Post-processing: If first chunk has no header (preamble), label it
        if chunks and not chunks[0]["header"]:
            chunks[0]["header"] = "Preamble / Introduction"

        return chunks
