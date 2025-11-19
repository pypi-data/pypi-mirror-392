"""Base chunker class 🏗️"""

from abc import ABC, abstractmethod
from typing import List


class BaseChunker(ABC):
    """Abstract base for all chunkers"""

    def __init__(self, language: str, config):
        self.language = language
        self.config = config

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """Split text into chunks"""
        pass

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """Merge chunks respecting size limits"""
        if not chunks:
            return []

        merged = []
        current = chunks[0]

        for next_chunk in chunks[1:]:
            if len(current) + len(next_chunk) + 1 <= self.config.chunk_size:
                current += " " + next_chunk
            else:
                merged.append(current)
                current = next_chunk

        merged.append(current)
        return merged