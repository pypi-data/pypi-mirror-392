"""All the CHONKING strategies in one place 🦛"""

from .recursive import RecursiveChunker
from .semantic import SemanticChunker
from .token import TokenChunker
from .markdown import MarkdownChunker
from .html import HTMLChunker
from .code import CodeChunker
from .pdf import PDFChunker

STRATEGY_MAP = {
    "recursive": RecursiveChunker,
    "semantic": SemanticChunker,
    "token": TokenChunker,
    "markdown": MarkdownChunker,
    "html": HTMLChunker,
    "code": CodeChunker,
    "pdf": PDFChunker,
}

def get_chunker(strategy: str, language: str, config):
    """Factory function to get the right chunker"""
    chunker_class = STRATEGY_MAP.get(strategy, RecursiveChunker)
    return chunker_class(language, config)