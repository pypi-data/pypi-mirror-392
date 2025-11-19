"""Refine and clean chunks ✨"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RefinerConfig:
    remove_empty: bool = True
    deduplicate: bool = True
    deduplication_threshold: float = 0.9
    trim_whitespace: bool = True
    min_chunk_length: int = 10
    merge_small_chunks: bool = True
    merge_threshold: int = 50


class ChonkRefiner:
    """Clean, deduplicate, and refine chunks"""

    def __init__(self, config: Optional[RefinerConfig] = None):
        self.config = config or RefinerConfig()

    async def arefine(self, chunks: List[str]) -> List[str]:
        """Async refine chunks"""
        # Run refinement steps concurrently where possible
        if self.config.trim_whitespace:
            chunks = await self._atrim_chunks(chunks)

        if self.config.remove_empty:
            chunks = await self._aremove_empty(chunks)

        if self.config.merge_small_chunks:
            chunks = await self._amerge_small(chunks)

        if self.config.deduplicate:
            chunks = await self._adeduplicate(chunks)

        return chunks

    def refine(self, chunks: List[str]) -> List[str]:
        """Sync refine wrapper"""
        if self.config.trim_whitespace:
            chunks = [c.strip() for c in chunks]

        if self.config.remove_empty:
            chunks = [c for c in chunks if len(c) >= self.config.min_chunk_length]

        if self.config.merge_small_chunks:
            chunks = self._merge_small(chunks)

        if self.config.deduplicate:
            chunks = self._deduplicate(chunks)

        return chunks

    async def _atrim_chunks(self, chunks: List[str]) -> List[str]:
        return [c.strip() for c in chunks]

    async def _aremove_empty(self, chunks: List[str]) -> List[str]:
        return [c for c in chunks if len(c) >= self.config.min_chunk_length]

    async def _amerge_small(self, chunks: List[str]) -> List[str]:
        return self._merge_small(chunks)

    async def _adeduplicate(self, chunks: List[str]) -> List[str]:
        return self._deduplicate(chunks)

    def _merge_small(self, chunks: List[str]) -> List[str]:
        """Merge chunks smaller than threshold"""
        if not chunks:
            return []

        merged = []
        current = chunks[0]

        for next_chunk in chunks[1:]:
            if len(current) < self.config.merge_threshold:
                current += " " + next_chunk
            else:
                merged.append(current)
                current = next_chunk

        merged.append(current)
        return merged

    def _deduplicate(self, chunks: List[str]) -> List[str]:
        """Remove near-duplicate chunks"""
        seen = []

        for chunk in chunks:
            is_duplicate = False

            for seen_chunk in seen:
                similarity = self._jaccard_similarity(chunk, seen_chunk)
                if similarity > self.config.deduplication_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen.append(chunk)

        return seen

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity"""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())

        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0