"""AWS S3 content loader ☁️"""

from .http import LoaderIntegration
from typing import Dict, Any, Optional
import os
import asyncio


class S3Integration(LoaderIntegration):
    """AWS S3 loader"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = None

    def _get_client(self):
        """Lazy-load S3 client"""
        if self._client is None:
            try:
                import boto3

                self._client = boto3.client(
                    "s3",
                    aws_access_key_id=self.config.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=self.config.get("aws_secret_access_key") or os.getenv(
                        "AWS_SECRET_ACCESS_KEY"),
                    region_name=self.config.get("region_name") or os.getenv("AWS_REGION", "us-east-1")
                )

            except ImportError:
                raise ImportError("boto3 required for S3 support. Install with: pip install chunkup[all]")

        return self._client

    async def afetch(self, uri: str) -> str:
        """Fetch from S3"""
        import asyncio

        # Parse s3://bucket/key
        path = uri.replace("s3://", "")
        bucket, key = path.split("/", 1)

        client = self._get_client()

        # boto3 is sync, run in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            client.get_object,
            {"Bucket": bucket, "Key": key}
        )

        content = response["Body"].read()

        # Handle different file types
        if key.endswith(".pdf"):
            return await self._extract_pdf(content)
        elif key.endswith((".md", ".txt", ".csv")):
            return content.decode("utf-8")
        else:
            return content.decode("utf-8", errors="ignore")

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