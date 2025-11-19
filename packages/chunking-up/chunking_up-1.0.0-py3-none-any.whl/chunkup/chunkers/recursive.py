"""Recursive text splitting - the OG CHONKER 🦛"""

import re
from typing import List
from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    """Recursively split text by separators"""

    def __init__(self, language: str, config):
        super().__init__(language, config)
        self.separators = self._get_separators()

    def split(self, text: str) -> List[str]:
        """Split text recursively"""
        chunks = self._split_text(text, self.separators)
        return self._merge_chunks(chunks)

    def _get_separators(self) -> List[str]:
        """Get language-aware separators"""
        # Default separators work for most languages
        return [
            "\n\n",  # Paragraphs
            "\n",  # Lines
            ". ",  # Sentences
            " ",  # Words
            ""  # Characters
        ]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split using separators"""
        if not text:
            return []

        for sep in separators:
            if not sep:
                # Character-level split
                return [text[i:i + self.config.chunk_size] for i in range(0, len(text), self.config.chunk_size)]

            if sep in text:
                parts = text.split(sep)
                chunks = []

                for part in parts:
                    if len(part) > self.config.chunk_size:
                        # Recursively split if too large
                        sub_chunks = self._split_text(part, separators[separators.index(sep) + 1:])
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(part)

                # Reconstruct with separator
                return [sep.join(chunks[i:i + 5]) for i in range(0, len(chunks), 5)]

        return [text]