"""Content fetching from any source 🚚"""

import asyncio
import aiohttp
from typing import Union, Dict, Any, Optional
import mimetypes
from urllib.parse import urlparse
import os
import json


class ContentFetcher:
    """Fetch content from URLs, files, APIs, cloud storage"""

    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def afetch(self, source: str) -> str:
        """Async fetch from any supported source ⚡"""
        if source.startswith("http"):
            return await self._fetch_url(source)
        elif source.startswith("s3://"):
            return await self._fetch_s3(source)
        elif source.startswith("notion://"):
            return await self._fetch_notion(source)
        elif os.path.isfile(source):
            return await self._fetch_file(source)
        else:
            raise ValueError(f"Unsupported source: {source}")

    def fetch(self, source: str) -> str:
        """Sync fetch wrapper"""
        return asyncio.run(self.afetch(source))

    async def _fetch_url(self, url: str) -> str:
        """Fetch from HTTP/HTTPS with smart content extraction"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url) as resp:
                content_type = resp.headers.get("content-type", "")

                if "application/pdf" in content_type:
                    return await self._extract_pdf(await resp.read())
                elif "text/html" in content_type:
                    return await self._extract_html(await resp.text())
                else:
                    return await resp.text()

    async def _fetch_file(self, path: str) -> str:
        """Fetch from local file system"""
        mime_type, _ = mimetypes.guess_type(path)

        with open(path, "rb") as f:
            content = f.read()

        if mime_type == "application/pdf":
            return await self._extract_pdf(content)
        elif mime_type in ["text/markdown", "text/plain"]:
            return content.decode("utf-8")
        else:
            return content.decode("utf-8", errors="ignore")

    async def _fetch_s3(self, s3_uri: str) -> str:
        """Fetch from S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            boto3.setup_default_session()
            s3 = boto3.client("s3")

            parsed = urlparse(s3_uri)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")

            response = s3.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read()

            if key.endswith(".pdf"):
                return await self._extract_pdf(content)
            return content.decode("utf-8")

        except ImportError:
            raise ImportError("boto3 required for S3 support. Install with: pip install chunkup[all]")
        except ClientError as e:
            raise RuntimeError(f"S3 fetch failed: {e}")

    async def _fetch_notion(self, notion_uri: str) -> str:
        """Fetch from Notion pages"""
        try:
            from notion_client import AsyncClient

            # Extract page ID from notion://page-id
            page_id = notion_uri.replace("notion://", "")
            notion = AsyncClient(auth=os.getenv("NOTION_API_KEY"))

            page = await notion.pages.retrieve(page_id=page_id)
            blocks = await notion.blocks.children.list(block_id=page_id)

            return self._notion_blocks_to_text(blocks)

        except ImportError:
            raise ImportError("notion-client required. Install with: pip install chunkup[all]")

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

    def _notion_blocks_to_text(self, blocks: Dict) -> str:
        """Convert Notion blocks to plain text"""
        text_parts = []
        for block in blocks.get("results", []):
            block_type = block.get("type")
            content = block.get(block_type, {})

            if block_type == "paragraph":
                texts = content.get("rich_text", [])
                text_parts.append(" ".join(t["plain_text"] for t in texts))

        return "\n".join(text_parts)