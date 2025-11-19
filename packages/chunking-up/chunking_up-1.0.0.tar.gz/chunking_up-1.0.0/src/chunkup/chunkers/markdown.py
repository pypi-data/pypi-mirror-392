"""Markdown-aware chunking 📄"""

from typing import List
import re
from .base import BaseChunker


class MarkdownChunker(BaseChunker):
    """Preserve markdown structure while chunking"""

    def __init__(self, language: str, config):
        super().__init__(language, config)
        self.markdown_patterns = {
            "headers": r"^(#{1,6})\s+(.+)$",
            "code_blocks": r"```[\s\S]*?```",
            "lists": r"^(\s*[-*+]|\d+\.)\s+",
            "quotes": r"^>\s+",
        }

    def split(self, text: str) -> List[str]:
        """Split markdown preserving structure"""
        # First split by headers
        sections = self._split_by_headers(text)

        chunks = []
        for section in sections:
            if len(section) > self.config.chunk_size:
                # Split large sections further
                sub_chunks = self._split_section(section)
                chunks.extend(sub_chunks)
            else:
                chunks.append(section)

        return self._merge_chunks(chunks)

    def _split_by_headers(self, text: str) -> List[str]:
        """Split markdown by headers"""
        lines = text.split("\n")
        sections = []
        current_section = []

        for line in lines:
            if re.match(self.markdown_patterns["headers"], line):
                # New header found, save previous section
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []

            current_section.append(line)

        # Add final section
        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def _split_section(self, section: str) -> List[str]:
        """Split a markdown section"""
        # Try to split by code blocks first
        code_block_pattern = self.markdown_patterns["code_blocks"]
        parts = re.split(f"({code_block_pattern})", section)

        chunks = []
        current_chunk = ""

        for part in parts:
            if not part.strip():
                continue

            if len(current_chunk) + len(part) > self.config.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = part
            else:
                current_chunk += "\n" + part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks