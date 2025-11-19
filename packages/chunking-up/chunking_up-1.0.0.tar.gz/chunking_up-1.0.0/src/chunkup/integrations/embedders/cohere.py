"""Cohere embedding integration 🧠"""

from .openai import EmbedderIntegration
from typing import List, Dict, Any, Optional
import os
import asyncio


class CohereEmbedder(EmbedderIntegration):
    """Cohere embedding integration"""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        super().__init__(model or "embed-multilingual-v3.0", api_key, **kwargs)

    def _get_client(self):
        """Lazy-load Cohere client"""
        if self._client is None:
            try:
                import cohere

                self._client = cohere.AsyncClient(api_key=self.api_key)

            except ImportError:
                raise ImportError("cohere package required. Install with: pip install chunkup[all]")

        return self._client

    async def aembed(self, texts: List[str]) -> List[List[float]]:
        """Async embed with Cohere"""
        client = self._get_client()

        response = await client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"
        )

        return response.embeddings