"""
Translation model implementations.

Handles Bangla ↔ English translation.
"""

import warnings
from typing import Any, List


def translate_text(
    model: Any, text: str, src_lang: str = "bn", tgt_lang: str = "en", **kwargs
) -> str:
    """
    Translate text using a translation model.

    Args:
        model: The translation model instance
        text: Input text to translate
        src_lang: Source language code
        tgt_lang: Target language code
        **kwargs: Additional translation parameters

    Returns:
        Translated text
    """
    # Check if model is a placeholder
    if hasattr(model, "__class__") and model.__class__.__name__ == "PlaceholderModel":
        result: str = model.translate(text, src_lang, tgt_lang)
        return result

    # Try to use transformers pipeline
    try:
        from transformers import pipeline

        translator = pipeline("translation", model=model, tokenizer=kwargs.get("tokenizer"))
        translation_result = translator(text, src_lang=src_lang, tgt_lang=tgt_lang, **kwargs)

        if isinstance(translation_result, list) and len(translation_result) > 0:
            return str(translation_result[0].get("translation_text", ""))
        return ""
    except ImportError:
        raise ImportError(
            "transformers is required for translation. " "Install it with: pip install transformers"
        )
    except Exception as e:
        warnings.warn(f"Error during translation: {e}")
        return text


def batch_translate(
    model: Any,
    texts: List[str],
    src_lang: str = "bn",
    tgt_lang: str = "en",
    batch_size: int = 8,
    **kwargs,
) -> List[str]:
    """
    Translate multiple texts in batches.

    Args:
        model: The translation model instance
        texts: List of texts to translate
        src_lang: Source language code
        tgt_lang: Target language code
        batch_size: Number of texts to translate at once
        **kwargs: Additional translation parameters

    Returns:
        List of translated texts
    """
    translations = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_translations = [
            translate_text(model, text, src_lang, tgt_lang, **kwargs) for text in batch
        ]
        translations.extend(batch_translations)

    return translations
