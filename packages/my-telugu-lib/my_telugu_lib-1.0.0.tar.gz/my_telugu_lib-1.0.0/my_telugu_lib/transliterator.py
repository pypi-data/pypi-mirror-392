"""
Transliteration Module - Roman ↔ Telugu Script
Uses indic-transliteration (works offline)
"""

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


def roman_to_telugu(text):
    """
    Convert Romanized Telugu to Telugu script

    Args:
        text (str): Roman text (e.g., "ramu")

    Returns:
        str: Telugu script (e.g., "రాము")

    Example:
        >>> roman_to_telugu("ramu pusthakam")
        'రాము పుస్తకం'
    """
    try:
        return transliterate(text, sanscript.ITRANS, sanscript.TELUGU)
    except Exception as e:
        return f"Transliteration failed: {str(e)}"


def telugu_to_roman(text):
    """
    Convert Telugu script to Roman transliteration

    Args:
        text (str): Telugu text (e.g., "రాము")

    Returns:
        str: Roman text (e.g., "rAmu")

    Example:
        >>> telugu_to_roman("రాము పుస్తకం")
        'rAmu pusthakam'
    """
    try:
        return transliterate(text, sanscript.TELUGU, sanscript.ITRANS)
    except Exception as e:
        return f"Transliteration failed: {str(e)}"


def english_to_telugu_script(text):
    """
    Convert English phonetic spelling to Telugu script
    (Approximate phonetic conversion)

    Args:
        text (str): English text

    Returns:
        str: Telugu script approximation

    Example:
        >>> english_to_telugu_script("hello")
        'హెల్లొ'
    """
    try:
        # Convert to lowercase for better matching
        text_lower = text.lower()
        return transliterate(text_lower, sanscript.ITRANS, sanscript.TELUGU)
    except Exception as e:
        return f"Transliteration failed: {str(e)}"
