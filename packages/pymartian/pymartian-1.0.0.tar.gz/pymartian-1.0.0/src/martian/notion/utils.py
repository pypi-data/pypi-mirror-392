"""Notion utility functions."""

import json
import os
import re
from typing import Optional

from .common import ApiColor, EmojiRequest, SupportedCodeLang, SUPPORTED_EMOJI_COLOR_MAP

# Load language map
_current_dir = os.path.dirname(__file__)
_language_map_path = os.path.join(_current_dir, "language_map.json")
with open(_language_map_path, "r", encoding="utf-8") as f:
    _LANGUAGE_MAP = json.load(f)


def parse_code_language(lang: Optional[str] = None) -> Optional[SupportedCodeLang]:
    """Parse code language from markdown to Notion supported language.
    
    Args:
        lang: The markdown code block language identifier
        
    Returns:
        Notion supported language or None
    """
    if not lang:
        return None
    lang_lower = lang.lower()
    return _LANGUAGE_MAP.get(lang_lower)


def parse_callout_emoji(text: str) -> Optional[dict]:
    """Parse text to find a leading emoji and determine its callout color.
    
    Uses Unicode emoji pattern to detect emoji at start of text.
    
    Args:
        text: The text to parse
        
    Returns:
        Dict with 'emoji' and 'color' keys if text starts with an emoji, None otherwise
    """
    if not text:
        return None

    # Get the first line of text
    first_line = text.split("\n")[0]

    # Match text that starts with an emoji (with optional variation selector)
    # This regex matches emoji presentation and extended pictographic characters
    match = re.match(
        r"^([\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\U0001F100-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FAFF\U00002700-\U000027BF][\uFE0F\uFE0E]?).*",
        first_line,
    )

    if not match:
        return None

    emoji = match.group(1)

    return {
        "emoji": emoji,
        "color": SUPPORTED_EMOJI_COLOR_MAP.get(emoji, "default"),
    }

