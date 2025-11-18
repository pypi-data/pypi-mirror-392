"""
Translation Module - English ↔ Telugu
Uses googletrans with deep-translator as fallback
"""

from googletrans import Translator as GoogleTranslator
from deep_translator import GoogleTranslator as DeepGoogleTranslator

# Initialize translators
_google_trans = GoogleTranslator()
_deep_trans_en2te = DeepGoogleTranslator(source='en', target='te')
_deep_trans_te2en = DeepGoogleTranslator(source='te', target='en')


def en2te(text):
    """
    Translate English to Telugu

    Args:
        text (str): English text

    Returns:
        str: Telugu translation

    Example:
        >>> en2te("Hello")
        'హలో'
    """
    try:
        # Try googletrans first
        result = _google_trans.translate(text, src='en', dest='te')
        return result.text
    except Exception as e:
        # Fallback to deep-translator
        try:
            return _deep_trans_en2te.translate(text)
        except Exception:
            return f"Translation failed: {str(e)}"


def te2en(text):
    """
    Translate Telugu to English

    Args:
        text (str): Telugu text

    Returns:
        str: English translation

    Example:
        >>> te2en("రాము")
        'Ramu'
    """
    try:
        # Try googletrans first
        result = _google_trans.translate(text, src='te', dest='en')
        return result.text
    except Exception as e:
        # Fallback to deep-translator
        try:
            return _deep_trans_te2en.translate(text)
        except Exception:
            return f"Translation failed: {str(e)}"


def translate(text, source='auto', target='te'):
    """
    Generic translation function

    Args:
        text (str): Text to translate
        source (str): Source language code (default: 'auto')
        target (str): Target language code (default: 'te')

    Returns:
        str: Translated text

    Example:
        >>> translate("Hello", source='en', target='te')
        'హలో'
    """
    try:
        result = _google_trans.translate(text, src=source, dest=target)
        return result.text
    except Exception as e:
        try:
            translator = DeepGoogleTranslator(source=source, target=target)
            return translator.translate(text)
        except Exception:
            return f"Translation failed: {str(e)}"
