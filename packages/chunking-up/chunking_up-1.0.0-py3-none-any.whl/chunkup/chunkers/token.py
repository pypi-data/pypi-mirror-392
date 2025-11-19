"""Token-based chunking for precise control 📊"""

from typing import List
from .base import BaseChunker


class TokenChunker(BaseChunker):
    """Split by token count using tiktoken"""

    def __init__(self, language: str, config):
        super().__init__(language, config)
        self._encoding = None

    def split(self, text: str) -> List[str]:
        """Split by token count"""
        try:
            import tiktoken

            if not self._encoding:
                self._encoding = tiktoken.get_encoding("cl100k_base")

            tokens = self._encoding.encode(text)
            chunks = []

            for i in range(0, len(tokens), self.config.chunk_size):
                chunk_tokens = tokens[i:i + self.config.chunk_size]
                chunk_text = self._encoding.decode(chunk_tokens)
                chunks.append(chunk_text)

            return chunks

        except ImportError:
            raise ImportError("tiktoken required for token-based chunking. Install with: pip install chunkup")
        except Exception:
            # Fallback to character-based
            return [text[i:i + self.config.chunk_size] for i in range(0, len(text), self.config.chunk_size)]