"""The heart of CHONKING ⚡"""

from typing import Any, List, Dict, Union, Optional
from pydantic import BaseModel
import asyncio
from ..utils.languages import detect_language, get_splitter_for_language
from .fetcher import ContentFetcher
from .refiner import ChonkRefiner
from .embedder import Embedder
from .shipper import VectorShipper


class ChonkConfig(BaseModel):
    """Configure your CHONKING experience"""
    chunk_size: int = 512
    chunk_overlap: int = 50
    language: Optional[str] = None
    strategy: str = "recursive"  # recursive, semantic, token, markdown, html, code
    embed: bool = False
    vector_db: Optional[str] = None
    refine: bool = True
    speed_mode: bool = True  # ⚡


class ChonkResult(BaseModel):
    """The holy CHONK result 🦛"""
    chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    embeddings: Optional[List[List[float]]] = None
    vector_ids: Optional[List[str]] = None


class CHONK:
    """
    The Ultimate CHONKING Machine 🦛⚡

    Usage:
        >>> from chunkup import CHONK
        >>> chonker = CHONK()
        >>> result = chonker.chonk("your_text_here")
        >>> print(result.chunks)
    """

    def __init__(self, config: Optional[ChonkConfig] = None):
        self.config = config or ChonkConfig()
        self.fetcher = ContentFetcher()
        self.refiner = ChonkRefiner()
        self.embedder = Embedder() if self.config.embed else None
        self.shipper = VectorShipper(self.config.vector_db) if self.config.vector_db else None

        # ⚡ Activate speed mode
        if self.config.speed_mode:
            print("⚡ CHONK Speed Mode: ON")

    async def achonk(self, content: Union[str, bytes], **kwargs) -> ChonkResult:
        """Async CHONKING for maximum speed ⚡"""
        return await self._chonk(content, async_mode=True, **kwargs)

    def chonk(self, content: Union[str, bytes], **kwargs) -> ChonkResult:
        """CHONK your content!"""
        return asyncio.run(self._chonk(content, async_mode=False, **kwargs))

    async def _chonk(self, content: Union[str, bytes], async_mode: bool = False, **kwargs) -> ChonkResult:
        """The CHONKING pipeline 🦛"""

        # 1. Fetch content if needed
        if isinstance(content, str) and content.startswith(("http", "s3://", "notion://")):
            content = await self.fetcher.afetch(content) if async_mode else self.fetcher.fetch(content)

        # 2. Detect language
        language = self.config.language or detect_language(content)

        # 3. Select chunking strategy
        chunker = self._get_chunker(language)

        # 4. CHONK! ⚡
        chunks = chunker.split(content)

        # 5. Refine if enabled
        if self.config.refine:
            chunks = await self.refiner.arefine(chunks) if async_mode else self.refiner.refine(chunks)

        # 6. Embed if enabled
        embeddings = None
        if self.embedder:
            embeddings = await self.embedder.aembed(chunks) if async_mode else self.embedder.embed(chunks)

        # 7. Ship to vector DB if enabled
        vector_ids = None
        if self.shipper:
            vector_ids = await self.shipper.aship(chunks, embeddings) if async_mode else self.shipper.ship(chunks,
                                                                                                           embeddings)

        return ChonkResult(
            chunks=[{"content": chunk, "metadata": {}} for chunk in chunks],
            metadata={"language": language, "strategy": self.config.strategy, "chunk_count": len(chunks)},
            embeddings=embeddings,
            vector_ids=vector_ids,
        )

    def _get_chunker(self, language: str):
        """Get the right chunker for the job 🦛"""
        from ..chunkers import get_chunker
        return get_chunker(self.config.strategy, language, self.config)