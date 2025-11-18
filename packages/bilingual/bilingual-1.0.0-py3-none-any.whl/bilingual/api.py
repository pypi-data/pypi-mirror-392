"""
High-level API for bilingual package.

Provides simple functions for common NLP tasks in Bangla and English.
"""

import warnings
from typing import Any, Dict, List, Optional, Union

from bilingual.normalize import detect_language
from bilingual.normalize import normalize_text as _normalize_text
from bilingual.tokenizer import BilingualTokenizer
from bilingual.tokenizer import load_tokenizer as _load_tokenizer

# Global cache for loaded models and tokenizers
_TOKENIZER_CACHE: Dict[str, BilingualTokenizer] = {}
_MODEL_CACHE: Dict[str, Any] = {}


def load_tokenizer(
    model_name: str = "bilingual-tokenizer", force_reload: bool = False
) -> BilingualTokenizer:
    """
    Load a tokenizer (with caching).

    Args:
        model_name: Name or path of the tokenizer model
        force_reload: Force reload even if cached

    Returns:
        BilingualTokenizer instance
    """
    if model_name not in _TOKENIZER_CACHE or force_reload:
        _TOKENIZER_CACHE[model_name] = _load_tokenizer(model_name)
    return _TOKENIZER_CACHE[model_name]


def load_model(model_name: str, force_reload: bool = False, **kwargs) -> Any:
    """
    Load a language model (with caching).

    Args:
        model_name: Name or path of the model
        force_reload: Force reload even if cached
        **kwargs: Additional arguments for model loading

    Returns:
        Loaded model instance
    """
    if model_name not in _MODEL_CACHE or force_reload:
        # Import here to avoid circular dependencies
        from bilingual.models.loader import load_model_from_name

        _MODEL_CACHE[model_name] = load_model_from_name(model_name, **kwargs)
    return _MODEL_CACHE[model_name]


def normalize_text(text: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Normalize text for Bangla or English.

    Args:
        text: Input text
        lang: Language code ('bn' or 'en'), auto-detected if None
        **kwargs: Additional normalization options

    Returns:
        Normalized text

    Examples:
        >>> normalize_text("আমি   স্কুলে যাচ্ছি।", lang="bn")
        'আমি স্কুলে যাচ্ছি.'
    """
    return _normalize_text(text, lang=lang, **kwargs)


def tokenize(
    text: str,
    tokenizer: Optional[Union[str, BilingualTokenizer]] = None,
    return_ids: bool = False,
) -> Union[List[str], List[int]]:
    """
    Tokenize text.

    Args:
        text: Input text
        tokenizer: Tokenizer name/path or instance (default: "bilingual-tokenizer")
        return_ids: If True, return token IDs instead of strings

    Returns:
        List of tokens or token IDs

    Examples:
        >>> tokenize("আমি বই পড়ি।")
        ['▁আমি', '▁বই', '▁পড়ি', '.']
    """
    if tokenizer is None:
        tokenizer = "bilingual-tokenizer"

    if isinstance(tokenizer, str):
        tokenizer = load_tokenizer(tokenizer)

    result = tokenizer.encode(text, as_ids=return_ids)
    # Return appropriate type based on return_ids
    if return_ids:
        return result  # type: ignore[return-value]
    return result  # type: ignore[return-value]


def generate(
    prompt: str,
    model_name: str = "bilingual-small-lm",
    max_tokens: int = 100,
    temperature: float = 0.7,
    top_p: float = 0.9,
    **kwargs,
) -> str:
    """
    Generate text continuation from a prompt.

    Args:
        prompt: Input prompt text
        model_name: Name of the generation model
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (higher = more random)
        top_p: Nucleus sampling parameter
        **kwargs: Additional generation parameters

    Returns:
        Generated text

    Examples:
        >>> generate("Once upon a time, there was a brave rabbit")
        'Once upon a time, there was a brave rabbit who lived in a forest...'
    """
    model = load_model(model_name)

    # Import here to avoid circular dependencies
    from bilingual.models.lm import generate_text

    return generate_text(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        **kwargs,
    )


def translate(
    text: str, src: str = "bn", tgt: str = "en", model_name: str = "bilingual-translate", **kwargs
) -> str:
    """
    Translate text between Bangla and English.

    Args:
        text: Input text to translate
        src: Source language code ('bn' or 'en')
        tgt: Target language code ('bn' or 'en')
        model_name: Name of the translation model
        **kwargs: Additional translation parameters

    Returns:
        Translated text

    Examples:
        >>> translate("আমি বই পড়তে ভালোবাসি।", src="bn", tgt="en")
        'I love to read books.'
    """
    if src == tgt:
        warnings.warn(f"Source and target languages are the same ({src}). Returning original text.")
        return text

    model = load_model(model_name)

    # Import here to avoid circular dependencies
    from bilingual.models.translate import translate_text

    return translate_text(model=model, text=text, src_lang=src, tgt_lang=tgt, **kwargs)


def readability_check(
    text: str,
    lang: Optional[str] = None,
    model_name: str = "bilingual-readability",
) -> Dict[str, Any]:
    """
    Check readability level of text.

    Args:
        text: Input text
        lang: Language code ('bn' or 'en'), auto-detected if None
        model_name: Name of the readability model

    Returns:
        Dictionary with readability metrics:
            - level: Reading level (e.g., "elementary", "intermediate", "advanced")
            - age_range: Suggested age range
            - score: Numerical readability score

    Examples:
        >>> readability_check("আমি স্কুলে যাই।", lang="bn")
        {'level': 'elementary', 'age_range': '6-8', 'score': 2.5}
    """
    if lang is None:
        lang = detect_language(text)

    # Implement actual readability checking using linguistic features
    # Extract features for better readability assessment
    features = _extract_readability_features(text, lang)
    return _calculate_readability_score(features, lang)


def _extract_readability_features(text: str, lang: str) -> Dict[str, float]:
    """
    Extract features for readability scoring.

    Args:
        text: Input text
        lang: Language code

    Returns:
        Dictionary of readability features
    """
    import re

    # Split into sentences and words
    if lang == "bn":
        # For Bangla, use simple sentence splitting
        sentences = re.split(r"[।!?]", text)
        words = re.findall(r"\w+", text)
    else:
        sentences = re.split(r"[.!?]+", text)
        words = re.findall(r"\b\w+\b", text)

    sentences = [s.strip() for s in sentences if s.strip()]
    words = [w for w in words if w.strip()]

    num_sentences = len(sentences)
    num_words = len(words)

    if num_words == 0:
        return {
            "avg_words_per_sentence": 0,
            "avg_word_length": 0,
            "avg_syllables_per_word": 0,
            "complexity_ratio": 0,
        }

    # Average words per sentence
    avg_words_per_sentence = num_words / max(num_sentences, 1)

    # Average word length
    avg_word_length = sum(len(w) for w in words) / num_words

    # Simple syllable estimation (works for both languages approximately)
    def estimate_syllables(word):
        # Simple heuristic: count vowel groups
        vowels = "aeiou" if lang == "en" else "অআইঈউঊএঐওঔ"
        syllables = 0
        prev_vowel = False
        for char in word:
            is_vowel = char.lower() in vowels if lang == "en" else char in vowels
            if is_vowel and not prev_vowel:
                syllables += 1
            prev_vowel = is_vowel
        return max(syllables, 1)

    syllables = sum(estimate_syllables(w) for w in words)
    avg_syllables_per_word = syllables / num_words

    # Complexity ratio (words with >6 characters / total words)
    complex_words = sum(1 for w in words if len(w) > 6)
    complexity_ratio = complex_words / num_words

    return {
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_word_length": avg_word_length,
        "avg_syllables_per_word": avg_syllables_per_word,
        "complexity_ratio": complexity_ratio,
    }


def _calculate_readability_score(features: Dict[str, float], lang: str) -> Dict[str, Any]:
    """
    Calculate readability score based on extracted features.

    Args:
        features: Dictionary of readability features
        lang: Language code

    Returns:
        Readability assessment dictionary
    """
    # Simple scoring model (can be replaced with trained model)
    score = 0.0

    # Weight different features
    score += features["avg_words_per_sentence"] * 0.3
    score += features["avg_word_length"] * 0.2
    score += features["avg_syllables_per_word"] * 0.3
    score += features["complexity_ratio"] * 0.2

    # Normalize score to 0-10 scale
    score = min(max(score, 0), 10)

    # Determine level based on score
    if score < 3:
        level = "elementary"
        age_range = "6-8"
    elif score < 6:
        level = "intermediate"
        age_range = "9-12"
    else:
        level = "advanced"
        age_range = "13+"

    return {
        "level": level,
        "age_range": age_range,
        "score": score,
        "language": lang,
    }


def safety_check(
    text: str,
    lang: Optional[str] = None,
    model_name: str = "bilingual-safety",
) -> Dict[str, Any]:
    """
    Check if text is safe and appropriate for children.

    Args:
        text: Input text
        lang: Language code ('bn' or 'en'), auto-detected if None
        model_name: Name of the safety model

    Returns:
        Dictionary with safety assessment:
            - is_safe: Boolean indicating if content is safe
            - confidence: Confidence score (0-1)
            - flags: List of any safety concerns
            - recommendation: Action recommendation

    Examples:
        >>> safety_check("This is a nice story about rabbits.")
        {'is_safe': True, 'confidence': 0.95, 'flags': [], 'recommendation': 'approved'}
    """
    if lang is None:
        lang = detect_language(text)

    # Implement actual safety checking with keyword-based filtering
    # Enhanced safety check for child-friendly content
    unsafe_keywords = {
        "en": ["violence", "hate", "kill", "death", "blood", "weapon", "drug", "alcohol"],
        "bn": ["হিংসা", "ঘৃণা", "মারা", "মৃত্যু", "রক্ত", "অস্ত্র", "মাদক", "মদ"],
    }

    text_lower = text.lower()
    flags = []

    # Check for unsafe keywords
    keywords = unsafe_keywords.get(lang, unsafe_keywords["en"])
    for keyword in keywords:
        if keyword in text_lower:
            flags.append(f"Contains potentially unsafe content: {keyword}")

    # Basic safety assessment
    is_safe = len(flags) == 0
    confidence = 0.9 if is_safe else 0.6

    return {
        "is_safe": is_safe,
        "confidence": confidence,
        "flags": flags,
        "recommendation": "approved" if is_safe else "review_required",
        "language": lang,
    }


def classify(
    text: str, labels: List[str], model_name: str = "bilingual-classifier", **kwargs
) -> Dict[str, float]:
    """
    Classify text into one or more categories.

    Args:
        text: Input text
        labels: List of possible labels
        model_name: Name of the classification model
        **kwargs: Additional classification parameters

    Returns:
        Dictionary mapping labels to confidence scores

    Examples:
        >>> classify("This is a story about animals.", labels=["story", "news", "dialogue"])
        {'story': 0.85, 'news': 0.05, 'dialogue': 0.10}
    """
    # Implement actual text classification using simple heuristics
    # Simple rule-based classification for common categories
    text_lower = text.lower()
    scores = {}

    # Define category keywords
    category_keywords = {
        "story": ["story", "tale", "once upon", "গল্প", "কাহিনী", "একদা"],
        "news": ["news", "report", "announce", "খবর", "সংবাদ", "রিপোর্ট"],
        "dialogue": ["said", "asked", "replied", "বলল", "জিজ্ঞাসা", "উত্তর"],
        "poetry": ["poem", "verse", "rhyme", "কবিতা", "ছন্দ", "পদ্য"],
        "instruction": ["how to", "step by step", "guide", "কীভাবে", "ধাপে ধাপে", "নির্দেশনা"],
    }

    # Calculate scores based on keyword matches
    for label in labels:
        keywords = category_keywords.get(label.lower(), [])
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        # Normalize score based on number of keywords
        score = matches / max(len(keywords), 1) if keywords else 0
        scores[label] = min(score, 1.0)  # Cap at 1.0

    # Ensure at least some score is distributed if no matches
    if sum(scores.values()) == 0:
        base_score = 1.0 / len(labels)
        scores = {label: base_score for label in labels}
    else:
        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        scores = {label: score / total for label, score in scores.items()}

    return scores


def batch_process(texts: List[str], operation: str, **kwargs) -> List[Any]:
    """
    Process multiple texts in batch for improved efficiency.

    Args:
        texts: List of input texts to process
        operation: Type of operation ('tokenize', 'normalize', 'generate',
            'translate', 'readability_check', 'safety_check', 'classify')
        **kwargs: Additional arguments for the operation

    Returns:
        List of results corresponding to each input text

    Examples:
        >>> texts = ["Hello world", "আমি বাংলায় কথা বলি"]
        >>> results = batch_process(texts, 'tokenize')
        >>> len(results)
        2
    """
    if operation == "tokenize":
        tokenizer = kwargs.get("tokenizer", "bilingual-tokenizer")
        return_ids = kwargs.get("return_ids", False)
        return [tokenize(text, tokenizer, return_ids) for text in texts]

    elif operation == "normalize":
        lang = kwargs.get("lang")
        return [normalize_text(text, lang) for text in texts]

    elif operation == "generate":
        model_name = kwargs.get("model_name", "bilingual-small-lm")
        max_tokens = kwargs.get("max_tokens", 100)
        return [generate(text, model_name, max_tokens, **kwargs) for text in texts]

    elif operation == "translate":
        src = kwargs.get("src", "bn")
        tgt = kwargs.get("tgt", "en")
        model_name = kwargs.get("model_name", "bilingual-translate")
        return [translate(text, src, tgt, model_name) for text in texts]

    elif operation == "readability_check":
        lang = kwargs.get("lang")
        model_name = kwargs.get("model_name", "bilingual-readability")
        return [readability_check(text, lang, model_name) for text in texts]

    elif operation == "safety_check":
        lang = kwargs.get("lang")
        model_name = kwargs.get("model_name", "bilingual-safety")
        return [safety_check(text, lang, model_name) for text in texts]

    elif operation == "classify":
        labels = kwargs.get("labels", [])
        model_name = kwargs.get("model_name", "bilingual-classifier")
        return [classify(text, labels, model_name) for text in texts]

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def fine_tune_model(
    model_name: str,
    train_data: List[Dict[str, str]],
    output_dir: str,
    epochs: int = 3,
    learning_rate: float = 5e-5,
    batch_size: int = 8,
    **kwargs,
) -> str:
    """
    Fine-tune a language model on custom data.

    Args:
        model_name: Name of the base model to fine-tune
        train_data: List of training examples, each dict with 'input' and 'output' keys
        output_dir: Directory to save the fine-tuned model
        epochs: Number of training epochs
        learning_rate: Learning rate for training
        batch_size: Batch size for training
        **kwargs: Additional training parameters

    Returns:
        Path to the fine-tuned model

    Examples:
        >>> train_data = [
        ...     {"input": "Hello, how are you?", "output": "I'm doing well, thank you!"},
        ...     {"input": "আমি কেমন আছি?", "output": "আমি ভালো আছি, ধন্যবাদ!"}
        ... ]
        >>> model_path = fine_tune_model("bilingual-small-lm", train_data, "my_model/")
    """
    try:
        from torch.utils.data import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    except ImportError:
        raise ImportError(
            "PyTorch and transformers are required for fine-tuning. "
            "Install with: pip install torch transformers"
        )

    # Load base model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Prepare dataset
    class CustomDataset(Dataset):
        def __init__(self, data, tokenizer, max_length=512):
            self.data = data
            self.tokenizer = tokenizer
            self.max_length = max_length

        def __len__(self):
            return len(self.data)

        def __getitem__(self, idx):
            item = self.data[idx]
            input_text = item["input"]
            target_text = item["output"]

            # Combine input and output for language modeling
            full_text = f"{input_text} {target_text}"

            encodings = self.tokenizer(
                full_text,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors="pt",
            )

            return {
                "input_ids": encodings["input_ids"].flatten(),
                "attention_mask": encodings["attention_mask"].flatten(),
                "labels": encodings["input_ids"].flatten(),
            }

    dataset = CustomDataset(train_data, tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        save_steps=500,
        save_total_limit=2,
        logging_dir=f"{output_dir}/logs",
        logging_steps=100,
        **kwargs,
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    # Train the model
    trainer.train()

    # Save the fine-tuned model
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    return output_dir


# Convenience aliases
normalize = normalize_text
tok = tokenize
gen = generate
trans = translate
