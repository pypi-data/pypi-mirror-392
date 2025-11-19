"""
CHUNKUP 🦛⚡
The ultimate CHONKING library that just works!
"""

from .core.chunker import CHONK
from .utils.constants import MASCOT, CHONK_SPEED

__version__ = "1.0.0"
__author__ = "CHONK Team"
__email__ = "chonk@chunkup.dev"

__all__ = ["CHONK", "MASCOT", "CHONK_SPEED"]

# 🦛 Welcome message
print(MASCOT)  # Shows cute hippo on import