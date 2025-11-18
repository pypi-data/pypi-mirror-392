"""
Sentiment and Tone Classification for Bangla text.

This module provides functionality to classify sentiment and tone
in Bangla literary and general text using both lexicon-based and ML approaches.
"""

import logging
from typing import Dict, Optional

try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    torch = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None

logger = logging.getLogger(__name__)


class SentimentToneClassifier:
    """
    Classifier for sentiment and tone in Bangla text.

    Supports both:
    1. Lexicon-based classification (rule-based with word lists)
    2. ML-based classification (fine-tuned transformer models)
    """

    # Bangla sentiment lexicons (simplified)
    POSITIVE_WORDS = [
        "ভালো",
        "সুন্দর",
        "চমৎকার",
        "দারুণ",
        "অসাধারণ",
        "মনোমুগ্ধকর",
        "আনন্দ",
        "খুশি",
        "প্রীতি",
        "ভালোবাসা",
        "সুখ",
        "হাসি",
        "উজ্জ্বল",
        "সফল",
        "জয়",
        "বিজয়",
        "শান্তি",
        "স্বস্তি",
    ]

    NEGATIVE_WORDS = [
        "খারাপ",
        "দুঃখ",
        "কষ্ট",
        "ব্যথা",
        "যন্ত্রণা",
        "বেদনা",
        "রাগ",
        "ক্রোধ",
        "ভয়",
        "আতঙ্ক",
        "দুশ্চিন্তা",
        "চিন্তা",
        "অন্ধকার",
        "ব্যর্থ",
        "পরাজয়",
        "হতাশ",
        "নিরাশ",
        "বিষণ্ণ",
    ]

    # Emotion-specific words
    EMOTION_LEXICON = {
        "joy": ["আনন্দ", "খুশি", "হাসি", "উল্লাস", "প্রফুল্ল", "উৎসাহ"],
        "sadness": ["দুঃখ", "কষ্ট", "বেদনা", "বিষণ্ণ", "হতাশ", "নিরাশ"],
        "anger": ["রাগ", "ক্রোধ", "ক্ষোভ", "বিরক্ত", "ঘৃণা"],
        "fear": ["ভয়", "আতঙ্ক", "ভীত", "শঙ্কা", "আশঙ্কা"],
        "surprise": ["অবাক", "চমক", "বিস্ময়", "আশ্চর্য"],
        "love": ["ভালোবাসা", "প্রেম", "স্নেহ", "প্রীতি", "মমতা"],
    }

    def __init__(self, model_path: Optional[str] = None, use_ml: bool = False):
        """
        Initialize the classifier.

        Args:
            model_path: Path to fine-tuned sentiment model (optional)
            use_ml: Whether to use ML-based classification
        """
        self.use_ml = use_ml and HAS_TRANSFORMERS
        self.model_path = model_path
        self._model = None
        self._tokenizer = None

        if self.use_ml and not HAS_TRANSFORMERS:
            logger.warning(
                "transformers not available, falling back to lexicon-based classification"
            )
            self.use_ml = False

    def load_model(self):
        """Load the ML model for classification."""
        if not self.use_ml:
            return

        if self._model is not None:
            return  # Already loaded

        if not self.model_path:
            logger.warning("No model path provided for ML classification")
            return

        logger.info(f"Loading sentiment classifier from {self.model_path}")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self._model.eval()

    def classify_tone(self, text: str) -> Dict[str, float]:
        """
        Classify the tone of the given text.

        Args:
            text: Input Bangla text

        Returns:
            Dictionary with tone probabilities (positive, neutral, negative)
        """
        if self.use_ml:
            return self._classify_tone_ml(text)
        else:
            return self._classify_tone_lexicon(text)

    def _classify_tone_lexicon(self, text: str) -> Dict[str, float]:
        """Lexicon-based tone classification."""
        # Count positive and negative words
        pos_count = sum(1 for word in self.POSITIVE_WORDS if word in text)
        neg_count = sum(1 for word in self.NEGATIVE_WORDS if word in text)

        total = pos_count + neg_count

        if total == 0:
            # Neutral by default
            return {
                "positive": 0.1,
                "neutral": 0.8,
                "negative": 0.1,
            }

        # Calculate probabilities
        pos_ratio = pos_count / total
        neg_ratio = neg_count / total

        # Normalize to probabilities
        positive = pos_ratio * 0.8 + 0.1
        negative = neg_ratio * 0.8 + 0.1
        neutral = 1.0 - positive - negative

        return {
            "positive": round(positive, 3),
            "neutral": round(max(0, neutral), 3),
            "negative": round(negative, 3),
        }

    def _classify_tone_ml(self, text: str) -> Dict[str, float]:
        """ML-based tone classification."""
        if self._model is None:
            self.load_model()

        if self._model is None:
            return self._classify_tone_lexicon(text)

        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]

            # Assuming labels: 0=negative, 1=neutral, 2=positive
            return {
                "negative": round(probs[0].item(), 3),
                "neutral": round(probs[1].item(), 3),
                "positive": round(probs[2].item(), 3),
            }

    def classify_emotion(self, text: str) -> Dict[str, float]:
        """
        Classify emotions in the given text.

        Args:
            text: Input Bangla text

        Returns:
            Dictionary with emotion probabilities
        """
        if self.use_ml:
            return self._classify_emotion_ml(text)
        else:
            return self._classify_emotion_lexicon(text)

    def _classify_emotion_lexicon(self, text: str) -> Dict[str, float]:
        """Lexicon-based emotion classification."""
        emotion_scores = {}

        for emotion, words in self.EMOTION_LEXICON.items():
            count = sum(1 for word in words if word in text)
            emotion_scores[emotion] = count

        total = sum(emotion_scores.values())

        if total == 0:
            # Neutral by default
            return {
                "joy": 0.1,
                "sadness": 0.1,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.1,
                "love": 0.1,
                "neutral": 0.4,
            }

        # Normalize to probabilities
        probs = {
            emotion: round(score / total * 0.8 + 0.05, 3)
            for emotion, score in emotion_scores.items()
        }

        # Add neutral
        probs["neutral"] = round(1.0 - sum(probs.values()), 3)

        return probs

    def _classify_emotion_ml(self, text: str) -> Dict[str, float]:
        """ML-based emotion classification."""
        if self._model is None:
            self.load_model()

        if self._model is None:
            return self._classify_emotion_lexicon(text)

        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]

            # Map to emotion labels (depends on model training)
            emotion_labels = ["joy", "sadness", "anger", "fear", "surprise", "love", "neutral"]

            return {
                label: round(probs[i].item(), 3)
                for i, label in enumerate(emotion_labels[: len(probs)])
            }

    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Comprehensive sentiment analysis.

        Args:
            text: Input Bangla text

        Returns:
            Dictionary containing tone and emotion analysis
        """
        tone = self.classify_tone(text)
        emotion = self.classify_emotion(text)

        # Determine overall sentiment
        if tone["positive"] > tone["negative"]:
            overall = "positive"
            score = tone["positive"]
        elif tone["negative"] > tone["positive"]:
            overall = "negative"
            score = tone["negative"]
        else:
            overall = "neutral"
            score = tone["neutral"]

        # Find dominant emotion
        dominant_emotion = max(emotion.items(), key=lambda x: x[1])

        return {
            "tone": tone,
            "emotion": emotion,
            "overall_sentiment": overall,
            "sentiment_score": score,
            "dominant_emotion": dominant_emotion[0],
            "emotion_score": dominant_emotion[1],
        }

    @classmethod
    def from_pretrained(cls, model_path: str):
        """Load a pretrained sentiment classifier."""
        instance = cls(model_path=model_path, use_ml=True)
        instance.load_model()
        return instance


# Convenience functions for backward compatibility
_default_classifier = None


def _get_default_classifier():
    """Get or create default classifier instance."""
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = SentimentToneClassifier(use_ml=False)
    return _default_classifier


def classify_tone(text: str) -> Dict[str, float]:
    """
    Classify the tone of the given text using lexicon-based approach.

    Args:
        text: Input Bangla text

    Returns:
        Dictionary with tone probabilities (positive, neutral, negative)
    """
    classifier = _get_default_classifier()
    return classifier.classify_tone(text)


def classify_emotion(text: str) -> Dict[str, float]:
    """
    Classify emotions in the given text using lexicon-based approach.

    Args:
        text: Input Bangla text

    Returns:
        Dictionary with emotion probabilities
    """
    classifier = _get_default_classifier()
    return classifier.classify_emotion(text)


def analyze_sentiment(text: str) -> Dict[str, any]:
    """
    Comprehensive sentiment analysis using lexicon-based approach.

    Args:
        text: Input Bangla text

    Returns:
        Dictionary containing tone and emotion analysis
    """
    classifier = _get_default_classifier()
    return classifier.analyze_sentiment(text)
