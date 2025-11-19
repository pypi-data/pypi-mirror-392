"""Qdrant vector DB integration 📍"""

from .pinecone import VectorDBIntegration
from typing import List, Dict, Any, Optional
import os
import uuid
import asyncio


class QdrantIntegration(VectorDBIntegration):
    """Qdrant integration"""

    def __init__(self, collection: str = "chonks", **kwargs):
        super().__init__(collection, **kwargs)
        self._client = None

    def _get_client(self):
        """Lazy-load Qdrant client"""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient, models

                url = self.config.get("url") or os.getenv("QDRANT_URL", "http://localhost:6333")
                api_key = self.config.get("api_key") or os.getenv("QDRANT_API_KEY")

                self._client = QdrantClient(url=url, api_key=api_key)

            except ImportError:
                raise ImportError("qdrant-client required. Install with: pip install chunkup[all]")

        return self._client

    async def aupsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Async upsert to Qdrant"""
        import asyncio

        client = self._get_client()

        # Ensure collection exists
        if not client.collection_exists(self.collection):
            # Get vector size from first vector
            vector_size = len(vectors[0]["values"])

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.create_collection(
                    collection_name=self.collection,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
            )

        points = []
        ids = []

        for vector in vectors:
            point_id = str(uuid.uuid4())
            ids.append(point_id)

            points.append(models.PointStruct(
                id=point_id,
                vector=vector["values"],
                payload=vector.get("metadata", {})
            ))

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            client.upsert,
            self.collection,
            points
        )

        return ids

    async def aquery(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Async query from Qdrant"""
        import asyncio

        client = self._get_client()

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                **kwargs
            )
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "metadata": point.payload,
            }
            for point in response
        ]