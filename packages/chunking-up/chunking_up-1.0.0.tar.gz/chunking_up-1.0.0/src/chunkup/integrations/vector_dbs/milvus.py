"""Milvus vector DB integration 🔍"""

from .pinecone import VectorDBIntegration
from typing import List, Dict, Any, Optional
import os
import uuid
import asyncio


class MilvusIntegration(VectorDBIntegration):
    """Milvus integration"""

    def __init__(self, collection: str = "chonks", **kwargs):
        super().__init__(collection, **kwargs)
        self._client = None

    def _get_client(self):
        """Lazy-load Milvus client"""
        if self._client is None:
            try:
                from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType

                uri = self.config.get("uri") or os.getenv("MILVUS_URI", "http://localhost:19530")
                token = self.config.get("token") or os.getenv("MILVUS_TOKEN")

                connections.connect("default", uri=uri, token=token)
                self._client = connections

            except ImportError:
                raise ImportError("pymilvus required. Install with: pip install chunkup[all]")

        return self._client

    async def aupsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Async upsert to Milvus"""
        import asyncio

        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType

        # Create collection if it doesn't exist
        if not self._collection_exists():
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=255, is_primary=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=len(vectors[0]["values"])),
                FieldSchema(name="metadata", dtype=DataType.JSON),
            ]

            schema = CollectionSchema(fields, description="CHONK collection")
            collection = Collection(self.collection, schema)

            # Create index
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: collection.create_index("vector", index_params)
            )

        collection = Collection(self.collection)
        ids = [str(uuid.uuid4()) for _ in vectors]

        # Prepare data
        entities = [
            ids,
            [v["values"] for v in vectors],
            [v.get("metadata", {}) for v in vectors],
        ]

        # Milvus SDK is sync
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            collection.insert,
            entities
        )

        # Flush data
        await loop.run_in_executor(None, collection.flush)

        return ids

    async def aquery(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Async query from Milvus"""
        import asyncio

        from pymilvus import Collection

        collection = Collection(self.collection)
        collection.load()

        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 16}
        }

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=["metadata"]
            )
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "metadata": hit.entity.get("metadata", {}),
            }
            for hit in results[0]
        ]

    def _collection_exists(self):
        """Check if collection exists"""
        try:
            from pymilvus import Collection
            Collection(self.collection)
            return True
        except:
            return False