"""
Telugu Translation & Transliteration Package

Complete Pre-loaded Telugu Translation Package
Combines 3 libraries for comprehensive Telugu language support:
- googletrans: English ↔ Telugu translation (needs internet)
- deep-translator: Backup translation service
- indic-transliteration: Roman ↔ Telugu script conversion (offline)
- Built-in typing tool: Type in Roman, press SPACE to convert!
"""

from .translator import en2te, te2en, translate
from .transliterator import (
    roman_to_telugu,
    telugu_to_roman,
    english_to_telugu_script
)
from .typing_tool import (
    start_typing_tool,
    typing_tool,
    convert_on_space,
    interactive_typing
)

__version__ = "1.0.0"
__all__ = [
    # Translation functions (online)
    'en2te',
    'te2en',
    'translate',

    # Transliteration functions (offline)
    'roman_to_telugu',
    'telugu_to_roman',
    'english_to_telugu_script',

    # Typing tool functions (NEW!)
    'start_typing_tool',
    'typing_tool',
    'convert_on_space',
    'interactive_typing',
]
