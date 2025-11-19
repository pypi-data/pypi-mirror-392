"""Pinecone vector DB integration 🌲"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import uuid
import asyncio


class VectorDBIntegration(ABC):
    """Abstract base for vector DB integrations"""

    def __init__(self, collection: str, **kwargs):
        self.collection = collection
        self.config = kwargs

    @abstractmethod
    async def aupsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Async upsert vectors"""
        pass

    @abstractmethod
    async def aquery(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Async query vectors"""
        pass

    def upsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Sync upsert wrapper"""
        return asyncio.run(self.aupsert(vectors))

    def query(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Sync query wrapper"""
        return asyncio.run(self.aquery(query_vector, top_k, **kwargs))


class PineconeIntegration(VectorDBIntegration):
    """Pinecone integration"""

    def __init__(self, collection: str = "chonks", **kwargs):
        super().__init__(collection, **kwargs)
        self._client = None

    def _get_client(self):
        """Lazy-load Pinecone client"""
        if self._client is None:
            try:
                from pinecone import Pinecone

                api_key = self.config.get("api_key") or os.getenv("PINECONE_API_KEY")
                if not api_key:
                    raise ValueError("PINECONE_API_KEY not found")

                self._client = Pinecone(api_key=api_key)
                self._index = self._client.Index(self.collection)

            except ImportError:
                raise ImportError("pinecone-client required. Install with: pip install chunkup[all]")

        return self._index

    async def aupsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Async upsert to Pinecone"""
        import asyncio

        index = self._get_client()
        ids = [str(uuid.uuid4()) for _ in vectors]

        # Convert to Pinecone format
        pinecone_vectors = []
        for i, vector in enumerate(vectors):
            pinecone_vectors.append({
                "id": ids[i],
                "values": vector["values"],
                "metadata": vector.get("metadata", {})
            })

        # Pinecone SDK is sync, run in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, index.upsert, pinecone_vectors)

        return ids

    async def aquery(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Async query from Pinecone"""
        import asyncio

        index = self._get_client()

        # Pinecone SDK is sync
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                **kwargs
            )
        )

        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata,
            }
            for match in response.matches
        ]