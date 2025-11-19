"""Ship chunks to vector databases 🚢"""

import asyncio
from typing import List, Dict, Any, Optional
import os
import uuid


class VectorShipper:
    """Unified interface for 10+ vector databases"""

    def __init__(self, vector_db: str, collection: Optional[str] = None, **kwargs):
        self.vector_db = vector_db
        self.collection = collection or "chonks"
        self.config = kwargs
        self._client = None

    async def aship(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """Async ship to vector DB"""
        if self.vector_db == "pinecone":
            return await self._aship_pinecone(chunks, embeddings)
        elif self.vector_db == "qdrant":
            return await self._aship_qdrant(chunks, embeddings)
        elif self.vector_db == "weaviate":
            return await self._aship_weaviate(chunks, embeddings)
        elif self.vector_db == "chroma":
            return await self._aship_chroma(chunks, embeddings)
        else:
            raise ValueError(f"Unsupported vector DB: {self.vector_db}")

    def ship(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """Sync ship wrapper"""
        return asyncio.run(self.aship(chunks, embeddings))

    async def _aship_pinecone(self, chunks: List[Dict], embeddings: List[List[float]]) -> List[str]:
        """Ship to Pinecone"""
        try:
            from pinecone import Pinecone

            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            index = pc.Index(self.collection)

            # Prepare vectors
            vectors = []
            ids = []

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = str(uuid.uuid4())
                ids.append(chunk_id)

                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": chunk.get("metadata", {}),
                })

            # Pinecone SDK is sync, run in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, index.upsert, vectors)

            return ids

        except ImportError:
            raise ImportError("pinecone-client required. Install with: pip install chunkup[all]")

    async def _aship_qdrant(self, chunks: List[Dict], embeddings: List[List[float]]) -> List[str]:
        """Ship to Qdrant"""
        try:
            from qdrant_client import QdrantClient, models

            client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))

            # Ensure collection exists
            if not client.collection_exists(self.collection):
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client.create_collection(
                        collection_name=self.collection,
                        vectors_config=models.VectorParams(
                            size=len(embeddings[0]),
                            distance=models.Distance.COSINE
                        )
                    )
                )

            points = []
            ids = []

            for chunk, embedding in zip(chunks, embeddings):
                point_id = str(uuid.uuid4())
                ids.append(point_id)

                points.append(models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=chunk.get("metadata", {}),
                ))

            # Qdrant SDK is sync
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                client.upsert,
                self.collection,
                points
            )

            return ids

        except ImportError:
            raise ImportError("qdrant-client required. Install with: pip install chunkup[all]")

    async def _aship_weaviate(self, chunks: List[Dict], embeddings: List[List[float]]) -> List[str]:
        """Ship to Weaviate"""
        try:
            import weaviate

            client = weaviate.Client(url=os.getenv("WEAVIATE_URL", "http://localhost:8080"))

            # Weaviate SDK is sync
            loop = asyncio.get_event_loop()

            ids = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_id = str(uuid.uuid4())
                ids.append(chunk_id)

                data_object = chunk.get("metadata", {})

                await loop.run_in_executor(
                    None,
                    client.data_object.create,
                    data_object,
                    self.collection,
                    chunk_id,
                    vector=embedding,
                )

            return ids

        except ImportError:
            raise ImportError("weaviate-client required. Install with: pip install chunkup[all]")

    async def _aship_chroma(self, chunks: List[Dict], embeddings: List[List[float]]) -> List[str]:
        """Ship to Chroma"""
        try:
            import chromadb

            client = chromadb.PersistentClient(path="./chroma_db")
            collection = client.get_or_create_collection(name=self.collection)

            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [c.get("metadata", {}) for c in chunks]
            documents = [c.get("content", "") for c in chunks]

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

        except ImportError:
            raise ImportError("chromadb required. Install with: pip install chunkup[all]")