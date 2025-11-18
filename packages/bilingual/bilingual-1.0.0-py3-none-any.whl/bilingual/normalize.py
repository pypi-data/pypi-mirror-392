"""
Text normalization utilities for Bangla and English.

Handles Unicode normalization, punctuation, numerals, and script-specific cleaning.
"""

import re
import unicodedata
from typing import List, Literal, Optional, cast

# Bangla Unicode ranges
BANGLA_RANGE = (0x0980, 0x09FF)
BANGLA_DIGITS = "০১২৩৪৫৬৭৮৯"
ARABIC_DIGITS = "0123456789"

# Common Bangla punctuation mappings
BANGLA_PUNCTUATION_MAP = {
    "।": ".",  # Dari/Full stop
    "॥": ".",  # Double dari
    "৷": ".",  # Alternative dari
}

# Romanization patterns for common Bangla words (for fallback)
ROMANIZATION_PATTERNS = {
    "ami": "আমি",
    "tumi": "তুমি",
    "apni": "আপনি",
    # Add more as needed
}


def normalize_unicode(text: str, form: str = "NFC") -> str:
    """
    Normalize Unicode text to a standard form.

    Args:
        text: Input text to normalize
        form: Unicode normalization form (NFC, NFD, NFKC, NFKD)

    Returns:
        Normalized text
    """
    normalized_form = cast(Literal["NFC", "NFD", "NFKC", "NFKD"], form)
    return unicodedata.normalize(normalized_form, text)


def is_bangla_char(char: str) -> bool:
    """Check if a character is in the Bangla Unicode range."""
    if not char:
        return False
    code_point = ord(char)
    return BANGLA_RANGE[0] <= code_point <= BANGLA_RANGE[1]


def contains_bangla(text: str) -> bool:
    """Check if text contains any Bangla characters."""
    return any(is_bangla_char(char) for char in text)


def normalize_bangla_digits(text: str, to_arabic: bool = True) -> str:
    """
    Convert between Bangla and Arabic numerals.

    Args:
        text: Input text
        to_arabic: If True, convert Bangla digits to Arabic; otherwise reverse

    Returns:
        Text with converted digits
    """
    if to_arabic:
        trans_table = str.maketrans(BANGLA_DIGITS, ARABIC_DIGITS)
    else:
        trans_table = str.maketrans(ARABIC_DIGITS, BANGLA_DIGITS)
    return text.translate(trans_table)


def normalize_bangla_punctuation(text: str) -> str:
    """
    Normalize Bangla punctuation to standard forms.

    Args:
        text: Input text

    Returns:
        Text with normalized punctuation
    """
    for bangla_punct, standard_punct in BANGLA_PUNCTUATION_MAP.items():
        text = text.replace(bangla_punct, standard_punct)
    return text


def remove_extra_whitespace(text: str) -> str:
    """Remove extra whitespace and normalize spacing."""
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def clean_text(text: str, lang: Optional[str] = None) -> str:
    """
    Clean text by removing unwanted characters and normalizing.

    Args:
        text: Input text
        lang: Language code ('bn' for Bangla, 'en' for English, None for auto-detect)

    Returns:
        Cleaned text
    """
    # Auto-detect language if not specified
    if lang is None:
        lang = "bn" if contains_bangla(text) else "en"

    # Remove control characters except newlines and tabs
    text = "".join(char for char in text if unicodedata.category(char)[0] != "C" or char in "\n\t")

    # Remove zero-width characters
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

    return text


def normalize_text(
    text: str,
    lang: Optional[str] = None,
    unicode_form: str = "NFC",
    normalize_digits: bool = True,
    normalize_punctuation: bool = True,
    remove_extra_spaces: bool = True,
) -> str:
    """
    Comprehensive text normalization for Bangla and English.

    Args:
        text: Input text to normalize
        lang: Language code ('bn' for Bangla, 'en' for English, None for auto-detect)
        unicode_form: Unicode normalization form (NFC, NFD, NFKC, NFKD)
        normalize_digits: Whether to normalize digits to Arabic numerals
        normalize_punctuation: Whether to normalize punctuation
        remove_extra_spaces: Whether to remove extra whitespace

    Returns:
        Normalized text

    Examples:
        >>> normalize_text("আমি   স্কুলে যাচ্ছি।", lang="bn")
        'আমি স্কুলে যাচ্ছি.'

        >>> normalize_text("I am going to school.", lang="en")
        'I am going to school.'
    """
    if not text:
        return text

    # Auto-detect language if not specified
    if lang is None:
        lang = "bn" if contains_bangla(text) else "en"

    # Unicode normalization
    text = normalize_unicode(text, form=unicode_form)

    # Clean unwanted characters
    text = clean_text(text, lang=lang)

    # Language-specific normalization
    if lang == "bn":
        if normalize_digits:
            text = normalize_bangla_digits(text, to_arabic=True)
        if normalize_punctuation:
            text = normalize_bangla_punctuation(text)

    # Remove extra whitespace
    if remove_extra_spaces:
        text = remove_extra_whitespace(text)

    return text


def detect_language(text: str) -> str:
    """
    Detect if text is primarily Bangla or English.

    Args:
        text: Input text

    Returns:
        Language code: 'bn', 'en', or 'mixed'
    """
    if not text:
        return "en"

    bangla_chars = sum(1 for char in text if is_bangla_char(char))
    total_alpha = sum(1 for char in text if char.isalpha())

    if total_alpha == 0:
        return "en"

    bangla_ratio = bangla_chars / total_alpha

    if bangla_ratio > 0.7:
        return "bn"
    elif bangla_ratio < 0.3:
        return "en"
    else:
        return "mixed"


def split_sentences(text: str, lang: Optional[str] = None) -> List[str]:
    """
    Split text into sentences.

    Args:
        text: Input text
        lang: Language code ('bn' for Bangla, 'en' for English, None for auto-detect)

    Returns:
        List of sentences
    """
    if lang is None:
        lang = detect_language(text)

    # Simple sentence splitting (can be improved with more sophisticated methods)
    if lang == "bn":
        # Split on Bangla dari and common punctuation
        sentences = re.split(r"[।.!?]+\s*", text)
    else:
        # Split on English punctuation
        sentences = re.split(r"[.!?]+\s*", text)

    # Filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences
