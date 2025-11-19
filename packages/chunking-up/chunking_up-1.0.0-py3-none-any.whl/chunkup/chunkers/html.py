"""HTML-aware chunking 🌐"""

from typing import List
import re
from .base import BaseChunker


class HTMLChunker(BaseChunker):
    """Preserve HTML structure while chunking"""

    def split(self, text: str) -> List[str]:
        """Split HTML preserving tags"""
        try:
            from bs4 import BeautifulSoup, NavigableString

            soup = BeautifulSoup(text, "html.parser")
            chunks = []

            # Extract main content areas
            for element in soup.find_all(["p", "div", "section", "article", "h1", "h2", "h3"]):
                content = element.get_text(separator=" ", strip=True)
                if len(content) > self.config.min_chunk_length:
                    chunks.append(content)

            return chunks

        except ImportError:
            # Fallback: regex-based HTML stripping
            clean_text = re.sub(r"<[^>]+>", " ", text)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()

            from .recursive import RecursiveChunker
            return RecursiveChunker(self.language, self.config).split(clean_text)