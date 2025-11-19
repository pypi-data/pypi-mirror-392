"""Code-aware chunking 💻"""

from typing import List
import re
from .base import BaseChunker


class CodeChunker(BaseChunker):
    """Chunk code files by functions/classes"""

    def __init__(self, language: str, config):
        super().__init__(language, config)
        self.code_patterns = {
            "python": {
                "function": r"def\s+\w+\s*\([^)]*\)\s*:",
                "class": r"class\s+\w+\s*[\(:]",
                "comment": r"#.*$",
            },
            "javascript": {
                "function": r"(function\s+\w+|const\s+\w+\s*=\s*function|\w+\s*=>\s*)",
                "class": r"class\s+\w+",
                "comment": r"//.*$",
            }
        }

    def split(self, text: str) -> List[str]:
        """Split code by functions, classes, etc."""
        # Detect language from extension or content
        lang = self._detect_language(text)

        if lang in self.code_patterns:
            return self._split_by_structure(text, lang)
        else:
            # Fallback to recursive for unknown languages
            from .recursive import RecursiveChunker
            return RecursiveChunker(self.language, self.config).split(text)

    def _detect_language(self, text: str) -> str:
        """Detect programming language"""
        if "def " in text and "import " in text:
            return "python"
        elif "function" in text or "const" in text:
            return "javascript"
        return "generic"

    def _split_by_structure(self, text: str, lang: str) -> List[str]:
        """Split code by functions and classes"""
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Check if this is a function/class definition
            if self._is_definition(stripped, lang):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []

            current_chunk.append(line)

        # Add final chunk
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _is_definition(self, line: str, lang: str) -> bool:
        """Check if line is a function/class definition"""
        patterns = self.code_patterns.get(lang, {})

        for pattern_type, pattern in patterns.items():
            if pattern_type in ["function", "class"]:
                if re.match(pattern, line):
                    return True

        return False