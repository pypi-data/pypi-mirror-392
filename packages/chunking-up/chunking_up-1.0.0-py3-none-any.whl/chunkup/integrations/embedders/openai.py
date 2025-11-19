"""OpenAI embedding integration 🤖"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import asyncio


class EmbedderIntegration(ABC):
    """Abstract base for embedder integrations"""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key or self._get_api_key()
        self.config = kwargs
        self._client = None

    @abstractmethod
    async def aembed(self, texts: List[str]) -> List[List[float]]:
        """Async embed texts"""
        pass

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Sync embed wrapper"""
        return asyncio.run(self.aembed(texts))

    def _get_api_key(self) -> str:
        """Get API key from environment"""
        env_var = f"{self.__class__.__name__.upper().replace('EMBEDDER', '')}_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found. Set {env_var} environment variable.")
        return api_key


class OpenAIEmbedder(EmbedderIntegration):
    """OpenAI embedding integration"""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        super().__init__(model or "text-embedding-3-small", api_key, **kwargs)

    def _get_client(self):
        """Lazy-load OpenAI client"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)

            except ImportError:
                raise ImportError("openai package required. Install with: pip install chunkup[all]")

        return self._client

    async def aembed(self, texts: List[str]) -> List[List[float]]:
        """Async embed with OpenAI"""
        client = self._get_client()

        response = await client.embeddings.create(
            model=self.model,
            input=texts,
            encoding_format="float"
        )

        return [data.embedding for data in response.data]