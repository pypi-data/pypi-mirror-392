"""Chroma vector DB integration 🎨"""

from .pinecone import VectorDBIntegration
from typing import List, Dict, Any, Optional
import os
import uuid
import asyncio


class ChromaIntegration(VectorDBIntegration):
    """Chroma integration"""

    def __init__(self, collection: str = "chonks", **kwargs):
        super().__init__(collection, **kwargs)
        self._client = None
        self._collection = None

    def _get_collection(self):
        """Lazy-load Chroma collection"""
        if self._collection is None:
            try:
                import chromadb

                persist_dir = self.config.get("persist_dir", "./chroma_db")
                self._client = chromadb.PersistentClient(path=persist_dir)

                self._collection = self._client.get_or_create_collection(
                    name=self.collection,
                    metadata={"hnsw:space": "cosine"}
                )

            except ImportError:
                raise ImportError("chromadb required. Install with: pip install chunkup[all]")

        return self._collection

    async def aupsert(self, vectors: List[Dict[str, Any]]) -> List[str]:
        """Async upsert to Chroma"""
        import asyncio

        collection = self._get_collection()

        ids = [str(uuid.uuid4()) for _ in vectors]
        metadatas = [v.get("metadata", {}) for v in vectors]
        documents = [v.get("content", "") for v in vectors]
        embeddings = [v["values"] for v in vectors]

        # Chroma SDK is sync
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            collection.upsert,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

        return ids

    async def aquery(self, query_vector: List[float], top_k: int = 10, **kwargs) -> List[Dict]:
        """Async query from Chroma"""
        import asyncio

        collection = self._get_collection()

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                include=["metadatas", "documents", "distances"]
            )
        )

        return [
            {
                "id": results["ids"][0][i],
                "score": results["distances"][0][i],
                "metadata": results["metadatas"][0][i],
                "document": results["documents"][0][i],
            }
            for i in range(len(results["ids"][0]))
        ]