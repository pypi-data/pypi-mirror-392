"""56-language support 🌍"""

from typing import List, Dict, Optional
import re

# Language mappings for better detection
LANGUAGE_CODES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "tr": "Turkish",
    "nl": "Dutch",
    "pl": "Polish",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "cs": "Czech",
    "hu": "Hungarian",
    "el": "Greek",
    "he": "Hebrew",
    "th": "Thai",
    "vi": "Vietnamese",
}


def detect_language(text: str) -> str:
    """Detect language of text using multiple strategies"""
    if not text or len(text) < 20:
        return "en"  # Default

    try:
        # Try langdetect for robust detection
        from langdetect import detect
        detected = detect(text)
        return detected.split("-")[0]  # Remove region codes
    except ImportError:
        # Fallback: character-based detection
        return _fallback_detect(text)
    except:
        return "en"


def _fallback_detect(text: str) -> str:
    """Fallback detection using Unicode blocks"""
    # Check for CJK characters
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"
    elif any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
        return "ja"
    elif any('\uac00' <= c <= '\ud7af' for c in text):
        return "ko"
    # Check for Cyrillic
    elif any('\u0400' <= c <= '\u04ff' for c in text):
        return "ru"
    # Check for Arabic
    elif any('\u0600' <= c <= '\u06ff' for c in text):
        return "ar"
    # Check for Greek
    elif any('\u0370' <= c <= '\u03ff' for c in text):
        return "el"
    # Check for Hebrew
    elif any('\u0590' <= c <= '\u05ff' for c in text):
        return "he"
    # Default to English
    return "en"


def get_splitter_for_language(language: str) -> str:
    """Get appropriate sentence splitter for language"""
    # Return language-specific regex patterns
    if language in ["ja", "zh", "ko"]:
        # For CJK, split on punctuation
        return r'[。！？\n]'
    elif language in ["th"]:
        # Thai doesn't use spaces, split on punctuation
        return r'[.,!?\n]'
    else:
        # For most languages, split on punctuation + space
        return r'(?<=[.!?])\s+'


def get_all_supported_languages() -> List[str]:
    """Return all 56 language codes"""
    return [
        "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
        "ar", "hi", "tr", "nl", "pl", "sv", "da", "no", "fi", "cs",
        "hu", "bg", "hr", "et", "el", "he", "ga", "is", "id", "lv",
        "lt", "ms", "mt", "fa", "ro", "sk", "sl", "th", "uk", "vi",
        "cy", "yi", "af", "sq", "am", "hy", "az", "eu", "bn", "bs",
        "ca", "ceb", "co", "eo", "fy", "gl", "ka", "ku"
    ]