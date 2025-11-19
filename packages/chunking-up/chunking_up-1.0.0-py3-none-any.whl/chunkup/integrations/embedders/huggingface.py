"""HuggingFace embedding integration 🤗"""

from .openai import EmbedderIntegration
from typing import List, Dict, Any, Optional
import os
import asyncio


class HuggingFaceEmbedder(EmbedderIntegration):
    """HuggingFace embedding integration"""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        super().__init__(model or "sentence-transformers/all-MiniLM-L6-v2", api_key, **kwargs)
        self._model = None

    def _get_model(self):
        """Lazy-load HuggingFace model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model)

            except ImportError:
                raise ImportError("sentence-transformers required. Install with: pip install chunkup[all]")

        return self._model

    async def aembed(self, texts: List[str]) -> List[List[float]]:
        """Async embed with HuggingFace (runs in thread pool)"""
        model = self._get_model()

        # SentenceTransformer is sync, run in thread pool
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, model.encode, texts)

        return embeddings.tolist()