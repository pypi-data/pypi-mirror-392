"""Generate embeddings for chunks 🧠"""

import asyncio
from typing import List, Optional, Dict, Any, Union
import os


class Embedder:
    """Unified embedding interface for 10+ providers"""

    def __init__(self, provider: str = "openai", model: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key or self._get_api_key()
        self._client = None

    def _get_api_key(self) -> str:
        """Get API key from environment"""
        env_var = f"{self.provider.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found. Set {env_var} environment variable.")
        return api_key

    async def aembed(self, chunks: List[str]) -> List[List[float]]:
        """Async embed chunks"""
        if self.provider == "openai":
            return await self._aembed_openai(chunks)
        elif self.provider == "cohere":
            return await self._aembed_cohere(chunks)
        elif self.provider == "huggingface":
            return await self._aembed_huggingface(chunks)
        elif self.provider == "vertex":
            return await self._aembed_vertex(chunks)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def embed(self, chunks: List[str]) -> List[List[float]]:
        """Sync embed wrapper"""
        return asyncio.run(self.aembed(chunks))

    async def _aembed_openai(self, chunks: List[str]) -> List[List[float]]:
        """OpenAI embeddings"""
        try:
            from openai import AsyncOpenAI

            if not self._client:
                self._client = AsyncOpenAI(api_key=self.api_key)

            model = self.model or "text-embedding-3-small"

            response = await self._client.embeddings.create(
                model=model,
                input=chunks
            )

            return [data.embedding for data in response.data]

        except ImportError:
            raise ImportError("openai package required. Install with: pip install chunkup[all]")

    async def _aembed_cohere(self, chunks: List[str]) -> List[List[float]]:
        """Cohere embeddings"""
        try:
            import cohere

            client = cohere.AsyncClient(api_key=self.api_key)
            model = self.model or "embed-multilingual-v3.0"

            response = await client.embed(
                texts=chunks,
                model=model,
                input_type="search_document"
            )

            return response.embeddings

        except ImportError:
            raise ImportError("cohere package required. Install with: pip install chunkup[all]")

    async def _aembed_huggingface(self, chunks: List[str]) -> List[List[float]]:
        """HuggingFace embeddings"""
        try:
            from sentence_transformers import SentenceTransformer

            # Note: This is synchronous, but we run in thread pool
            loop = asyncio.get_event_loop()
            model = self._get_huggingface_model()

            embeddings = await loop.run_in_executor(None, model.encode, chunks)
            return embeddings.tolist()

        except ImportError:
            raise ImportError("sentence-transformers required. Install with: pip install chunkup[all]")

    async def _aembed_vertex(self, chunks: List[str]) -> List[List[float]]:
        """Google Vertex AI embeddings"""
        try:
            from vertexai.language_models import TextEmbeddingModel

            model = TextEmbeddingModel.from_pretrained(self.model or "text-embedding-004")

            # Vertex SDK is sync, run in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: [model.get_embeddings([chunk])[0].values for chunk in chunks]
            )

            return embeddings

        except ImportError:
            raise ImportError("google-cloud-aiplatform required. Install with: pip install chunkup[all]")

    def _get_huggingface_model(self):
        """Lazy load HuggingFace model"""
        if not hasattr(self, "_hf_model"):
            from sentence_transformers import SentenceTransformer
            model_name = self.model or "sentence-transformers/all-MiniLM-L6-v2"
            self._hf_model = SentenceTransformer(model_name)
        return self._hf_model