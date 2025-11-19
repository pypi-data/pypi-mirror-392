"""PDF-specific chunking 📑"""

from typing import List
from .base import BaseChunker


class PDFChunker(BaseChunker):
    """Chunk PDFs by pages and content"""

    def split(self, text: str) -> List[str]:
        """Split PDF text"""
        # PDF text often has page markers
        pages = self._split_by_pages(text)

        chunks = []
        for page in pages:
            if len(page) > self.config.chunk_size:
                # Split large pages further
                from .recursive import RecursiveChunker
                sub_chunks = RecursiveChunker(self.language, self.config).split(page)
                chunks.extend(sub_chunks)
            else:
                chunks.append(page)

        return chunks

    def _split_by_pages(self, text: str) -> List[str]:
        """Split by page markers"""
        # Common PDF page markers
        patterns = [
            r"\f",  # Form feed
            r"Page \d+",  # "Page 1"
            r"\n\s*\d+\s*\n",  # Page numbers on their own line
        ]

        import re

        # Try each pattern
        for pattern in patterns:
            pages = re.split(pattern, text)
            if len(pages) > 1:
                return [p.strip() for p in pages if p.strip()]

        # Fallback: treat as single page
        return [text]