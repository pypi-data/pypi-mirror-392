"""HTTP/HTTPS content loader 🌐"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from urllib.parse import urlparse


class LoaderIntegration(ABC):
    """Abstract base for loader integrations"""

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    async def afetch(self, uri: str) -> str:
        """Async fetch content from URI"""
        pass

    def fetch(self, uri: str) -> str:
        """Sync fetch wrapper"""
        return asyncio.run(self.afetch(uri))


class HTTPIntegration(LoaderIntegration):
    """HTTP/HTTPS loader"""

    def __init__(self, timeout: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.timeout = timeout

    async def afetch(self, uri: str) -> str:
        """Fetch from HTTP/HTTPS"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(uri, timeout=aiohttp.ClientTimeout(total=self.timeout)) as resp:
                content_type = resp.headers.get("content-type", "")

                if "application/pdf" in content_type:
                    return await self._extract_pdf(await resp.read())
                elif "text/html" in content_type:
                    return await self._extract_html(await resp.text())
                else:
                    return await resp.text()

    async def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            from PyPDF2 import PdfReader
            import io

            pdf = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text

        except ImportError:
            raise ImportError("PyPDF2 required for PDF support. Install with: pip install chunkup[all]")

    async def _extract_html(self, html: str) -> str:
        """Extract main content from HTML"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Remove script/style tags
            for tag in soup(["script", "style"]):
                tag.decompose()

            return soup.get_text(separator=" ", strip=True)

        except ImportError:
            # Fallback to simple extraction
            import re
            return re.sub(r"<[^>]+>", "", html)