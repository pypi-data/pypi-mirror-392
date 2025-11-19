"""YouTube content loader 📺"""

from .http import LoaderIntegration
from typing import Dict, Any, Optional
import re
import asyncio


class YouTubeIntegration(LoaderIntegration):
    """YouTube transcript loader"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def afetch(self, uri: str) -> str:
        """Fetch YouTube transcript"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api.formatters import TextFormatter

        except ImportError:
            raise ImportError("youtube-transcript-api required. Install with: pip install chunkup[all]")

        # Extract video ID from URL
        video_id = self._extract_video_id(uri)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        try:
            # Fetch transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # Format as plain text
            formatter = TextFormatter()
            text = formatter.format_transcript(transcript)

            return text

        except Exception as e:
            raise RuntimeError(f"Failed to fetch YouTube transcript: {e}")

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None