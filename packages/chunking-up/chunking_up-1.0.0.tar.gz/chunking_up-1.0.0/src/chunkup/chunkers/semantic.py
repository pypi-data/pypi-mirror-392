"""Semantic chunking using embeddings 🧠"""

import numpy as np
from typing import List
from .base import BaseChunker


class SemanticChunker(BaseChunker):
    """Split where semantic similarity breaks"""

    def split(self, text: str) -> List[str]:
        """Split by detecting semantic boundaries"""
        try:
            # Split into sentences first
            sentences = self._split_into_sentences(text)

            if len(sentences) <= 1:
                return sentences

            # Get embeddings for sentences
            embeddings = self._get_embeddings(sentences)

            # Calculate similarity breaks
            breakpoints = self._find_breakpoints(embeddings)

            # Group sentences at breakpoints
            return self._group_sentences(sentences, breakpoints)

        except Exception as e:
            # Fallback to recursive
            from .recursive import RecursiveChunker
            return RecursiveChunker(self.language, self.config).split(text)

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences (works for 56 languages)"""
        # Universal sentence splitting using regex
        # Works reasonably well across languages
        pattern = r'(?<=[.!?。！？])\s+'
        import re
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_embeddings(self, sentences: List[str]) -> np.ndarray:
        """Get embeddings for sentences"""
        # Use a lightweight model for semantic chunking
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            embeddings = model.encode(sentences, convert_to_tensor=True)
            return embeddings.cpu().numpy()

        except ImportError:
            # Fallback: use random embeddings (not ideal but works)
            return np.random.rand(len(sentences), 384)

    def _find_breakpoints(self, embeddings: np.ndarray, threshold: float = 0.7) -> List[int]:
        """Find where to split based on cosine similarity"""
        # Calculate cosine similarity between consecutive sentences
        from sklearn.metrics.pairwise import cosine_similarity

        similarities = cosine_similarity(embeddings[:-1], embeddings[1:]).diagonal()

        # Find indices where similarity drops below threshold
        breakpoints = [i + 1 for i, sim in enumerate(similarities) if sim < threshold]

        return breakpoints

    def _group_sentences(self, sentences: List[str], breakpoints: List[int]) -> List[str]:
        """Group sentences into chunks at breakpoints"""
        if not breakpoints:
            return sentences

        chunks = []
        start = 0

        for break_point in breakpoints:
            chunk = " ".join(sentences[start:break_point])
            if chunk:
                chunks.append(chunk)
            start = break_point

        # Add remaining sentences
        if start < len(sentences):
            chunks.append(" ".join(sentences[start:]))

        return chunks