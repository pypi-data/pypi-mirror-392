"""Weaviate vector DB integration 🧠"""

from .pinecone import VectorDBIntegration
from typing import List, Dict, Any, Optional
import os
import uuid
import asyncio


class WeaviateIntegration(VectorDBIntegration):
    """Weaviate integration"""

    def __init__(self, collection: str = "Chonk", **kwargs):
        super().__init__(collection, **kwargs)
        self._client = None

    def _get_client(self):
        """Lazy-load Weaviate client"""
        if self._client is None:
            try:
                import weaviate

                url = self.config.get("url") or os.getenv("WEAVIATE_URL", "http://localhost:8080")
                api_key = self.config.get("api_key") or os.getenv("WEAVIATE_API_KEY")

                auth_config = None
                if api_key:
                    auth_config = weaviate.AuthApiToken(api_key=api_key)

                self._client = weaviate.Client(url=url, auth_client_secret=auth_config)

            except ImportError:
                raise ImportError("weaviate-client required. Install with: pip install chunkup[all]")

        return self._client

    async def aupsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Async upsert to Weaviate"""
        import asyncio

        client = self._get_client()

        # Weaviate SDK is sync
        loop = asyncio.get_event_loop()
        ids = []

        for vector in vectors:
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)

            data_object = vector.get("metadata", {})

            await loop.run_in_executor(
                None,
                client.data_object.create,
                data_object,
                self.collection,
                chunk_id,
                vector=vector["values"]
            )

        return ids

    async def aquery(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Async query from Weaviate"""
        import asyncio

        client = self._get_client()

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.query.get(
                self.collection,
                ["_additional {id, certainty, distance}"]
            ).with_near_vector({
                "vector": query_vector,
                "certainty": kwargs.get("certainty", 0.7)
            }).with_limit(top_k).do()
        )

        if "data" in response and "Get" in response["data"]:
            objects = response["data"]["Get"].get(self.collection, [])

            return [
                {
                    "id": obj["_additional"]["id"],
                    "score": obj["_additional"].get("certainty", 0),
                    "metadata": {k: v for k, v in obj.items() if k != "_additional"},
                }
                for obj in objects
            ]

        return []