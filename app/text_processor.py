"""
Text Processor Module
Handles text cleaning, encoding detection, and Japanese-specific optimizations.
"""

import re
import unicodedata
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

def detect_encoding(file_path: str) -> str:
    """
    Detect file encoding.
    Prioritizes UTF-8, then checks BOM, then Shift-JIS for Japanese contexts.
    """
    # 1. Check for BOM
    try:
        with open(file_path, 'rb') as f:
            raw = f.read(4)
            if raw.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-sig'
    except Exception:
        pass

    # 2. Use chardet if available (read relatively small chunk)
    if HAS_CHARDET:
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(10000)
            result = chardet.detect(raw)
            if result['encoding'] and result['confidence'] > 0.7:
                return result['encoding']
        except Exception as e:
            logger.warning(f"Chardet failed: {e}")

    # 3. Fallback heuristics for Japanese
    # Try UTF-8 first
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
            return 'utf-8'
    except UnicodeDecodeError:
        pass

    # Try Shift-JIS (common in legacy Japanese systems)
    try:
        with open(file_path, 'r', encoding='shift_jis') as f:
            f.read()
            return 'shift_jis'
    except UnicodeDecodeError:
        pass

    # Try EUC-JP
    try:
        with open(file_path, 'r', encoding='euc-jp') as f:
            f.read()
            return 'euc-jp'
    except UnicodeDecodeError:
        pass

    return 'utf-8' # Final fallback

def normalize_width(text: str) -> str:
    """
    Normalize full-width characters to half-width (NFKC).
    Example: ＡＢＣ１２３ -> ABC123
    """
    return unicodedata.normalize('NFKC', text)

def clean_japanese_text(text: str) -> str:
    """
    Clean Japanese text for better RAG/Markdown quality.
    - Removes spaces between Japanese characters (Kanji/Kana).
    - Preserves spaces between Latin/Numbers and Japanese.
    """
    if not text:
        return ""

    # 1. Remove zero-width spaces
    text = text.replace('\u200b', '')

    # 2. Remove spaces between Japanese characters
    # Regex explanations:
    # \p{Han} is Kanji, \p{Hiragana}, \p{Katakana}
    # In Python regex, we roughly use ranges.
    # Kanji: \u4e00-\u9faf
    # Hiragana: \u3040-\u309f
    # Katakana: \u30a0-\u30ff
    # Full-width punctuation: \u3000-\u303f

    jp_chars = r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf\u3000-\u303f]'

    # Pattern: Japanese char + One or more spaces + Japanese char
    # We want to replace it with just the two chars (remove the space)
    # Using lookbehind and lookahead

    pattern = f"(?<={jp_chars})[ \\t]+(?={jp_chars})"
    text = re.sub(pattern, "", text)

    return text
