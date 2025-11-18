"""
Enhanced literary analysis with caching and more sophisticated detection.
Supports both Bangla and English text.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class LiteraryAnalyzer:
    """Enhanced literary analysis with caching and more sophisticated detection."""

    def __init__(self, language: str = "en"):
        self.language = language
        self._compile_patterns()
        self._cache = {}

    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        self.metaphor_patterns = {
            "en": [
                re.compile(r"\b(\w+)\s+is\s+a\s+(\w+)\b", re.IGNORECASE),
                re.compile(r"\b(\w+)\s+are\s+(\w+)\b", re.IGNORECASE),
                re.compile(r"\b(\w+)\s+was\s+like\s+(\w+)\b", re.IGNORECASE),
            ],
            "bn": [
                re.compile(r"(\S+)\s+হল\s+(\S+)"),
                re.compile(r"(\S+)\s+যেন\s+(\S+)"),
                re.compile(r"(\S+)\s+সদৃশ\s+(\S+)"),
            ],
        }

    def detect_metaphors(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced metaphor detection with better pattern matching."""
        if text not in self._cache:
            self._cache[text] = self._detect_metaphors(text)
        return self._cache[text]

    def _detect_metaphors(self, text: str) -> List[Dict[str, Any]]:
        metaphors = []

        for pattern in self.metaphor_patterns.get(self.language, []):
            for match in pattern.finditer(text):
                subject, vehicle = match.groups()
                if subject.lower() != vehicle.lower():  # Basic metaphor check
                    metaphors.append(
                        {
                            "text": match.group(0),
                            "type": "metaphor",
                            "subject": subject,
                            "vehicle": vehicle,
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.8,  # Could be refined based on context
                        }
                    )

        return metaphors


def detect_similes(text: str, language: str = "en") -> List[Dict[str, Any]]:
    """
    Detect similes in text using pattern matching.

    Args:
        text: Input text to analyze
        language: Language code ('en' or 'bn')

    Returns:
        List of detected similes with positions and confidence
    """
    similes = []

    # Common simile patterns
    patterns = {
        "en": [
            (r"\b(as|like)\s+\w+", 0.8),
            (r"\bas\s+\w+\s+as\b", 0.9),
        ],
        "bn": [
            (r"[\u0980-\u09FF]+\s+(মত|যেমন)\s+[\u0980-\u09FF]+", 0.8),
            (r"[\u0980-\u09FF]+\s+যেমন\s+[\u0980-\u09FF]+\s+তেমন", 0.9),
        ],
    }

    for pattern, confidence in patterns.get(language, []):
        for match in re.finditer(pattern, text, re.IGNORECASE):
            similes.append(
                {
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": confidence,
                    "type": "simile",
                    "language": language,
                }
            )

    return similes


def analyze_tone(text: str, language: str = "en") -> Dict[str, float]:
    """
    Analyze the tone of the given text.

    Args:
        text: Input text to analyze
        language: Language code ('en' or 'bn')

    Returns:
        Dictionary with tone scores (positive, negative, neutral)
    """
    # Simple implementation - can be enhanced with ML
    positive_words = {
        "en": ["good", "great", "excellent", "wonderful", "happy", "love", "like"],
        "bn": ["ভালো", "চমৎকার", "দারুণ", "সুন্দর", "আনন্দ", "ভালবাসা"],
    }

    negative_words = {
        "en": ["bad", "terrible", "awful", "horrible", "hate", "sad", "angry"],
        "bn": ["খারাপ", "ভয়ানক", "ভীতিকর", "বাজে", "দুঃখ", "রাগ"],
    }

    words = text.lower().split()
    word_count = len(words)

    if word_count == 0:
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}

    pos_count = sum(1 for word in words if word in positive_words.get(language, []))
    neg_count = sum(1 for word in words if word in negative_words.get(language, []))

    # Calculate probabilities with Laplace smoothing
    alpha = 0.1
    pos_prob = (pos_count + alpha) / (word_count + 3 * alpha)
    neg_prob = (neg_count + alpha) / (word_count + 3 * alpha)
    neutral_prob = (word_count - pos_count - neg_count + alpha) / (word_count + 3 * alpha)

    # Normalize
    total = pos_prob + neg_prob + neutral_prob
    return {
        "positive": round(pos_prob / total, 3),
        "neutral": round(neutral_prob / total, 3),
        "negative": round(neg_prob / total, 3),
    }
