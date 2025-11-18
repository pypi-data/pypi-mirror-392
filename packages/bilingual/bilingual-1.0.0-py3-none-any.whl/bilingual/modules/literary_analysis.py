"""
Literary device detection and tone analysis for Bengali and English text.

This module provides simple rule-based detectors for common literary devices
and a basic tone classifier. These are lightweight stubs designed to be
extended with ML models in future iterations.
"""

import re
from typing import Dict, List


def metaphor_detector(text: str) -> List[Dict[str, str]]:
    """
    Detect potential metaphors in text using simple pattern matching.

    Args:
        text: Input text in Bengali or English

    Returns:
        List of dictionaries with 'text' and 'type' keys for detected metaphors

    Examples:
        >>> metaphor_detector("Life is a journey")
        [{'text': 'Life is a journey', 'type': 'metaphor'}]
    """
    metaphors = []

    # English patterns: "X is Y" where X != Y literally
    english_patterns = [
        r"\b(\w+)\s+is\s+a\s+(\w+)\b",
        r"\b(\w+)\s+are\s+(\w+)\b",
    ]

    # Bengali patterns: common metaphorical constructions
    bengali_patterns = [
        r"(\S+)\s+হল\s+(\S+)",  # X হল Y
        r"(\S+)\s+যেন\s+(\S+)",  # X যেন Y (like)
    ]

    all_patterns = english_patterns + bengali_patterns

    for pattern in all_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            metaphors.append(
                {
                    "text": match.group(0),
                    "type": "metaphor",
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    return metaphors


def simile_detector(text: str) -> List[Dict[str, str]]:
    """
    Detect similes in text using pattern matching for comparison words.

    Args:
        text: Input text in Bengali or English

    Returns:
        List of dictionaries with 'text' and 'type' keys for detected similes

    Examples:
        >>> simile_detector("She runs like the wind")
        [{'text': 'like the wind', 'type': 'simile'}]
    """
    similes = []

    # English patterns: "like", "as...as"
    english_patterns = [
        r"\blike\s+(\w+(?:\s+\w+){0,3})\b",
        r"\bas\s+(\w+)\s+as\s+(\w+)\b",
    ]

    # Bengali patterns: common simile markers
    bengali_patterns = [
        r"যেমন\s+(\S+)",  # যেমন (like)
        r"মতো\s+(\S+)",  # মতো (like)
        r"(\S+)\s+মত\b",  # X মত
    ]

    all_patterns = english_patterns + bengali_patterns

    for pattern in all_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            similes.append(
                {
                    "text": match.group(0),
                    "type": "simile",
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    return similes


def tone_classifier(text: str) -> Dict[str, float]:
    """
    Classify the tone of text into positive, neutral, or negative.

    This is a simple keyword-based classifier. Returns normalized probabilities.

    Args:
        text: Input text in Bengali or English

    Returns:
        Dictionary with 'positive', 'neutral', 'negative' probability scores

    Examples:
        >>> tone_classifier("This is wonderful!")
        {'positive': 0.8, 'neutral': 0.1, 'negative': 0.1}
    """
    text_lower = text.lower()

    # Simple keyword lists (expandable)
    positive_keywords = [
        "good",
        "great",
        "wonderful",
        "excellent",
        "happy",
        "joy",
        "love",
        "ভালো",
        "সুন্দর",
        "চমৎকার",
        "আনন্দ",
        "খুশি",
        "ভালোবাসা",
    ]

    negative_keywords = [
        "bad",
        "terrible",
        "awful",
        "sad",
        "angry",
        "hate",
        "pain",
        "খারাপ",
        "দুঃখ",
        "রাগ",
        "ঘৃণা",
        "কষ্ট",
        "বিষাদ",
    ]

    positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

    # Calculate raw scores
    total = positive_count + negative_count

    if total == 0:
        # No sentiment keywords found - neutral
        return {"positive": 0.1, "neutral": 0.8, "negative": 0.1}

    # Normalize to probabilities
    positive_score = positive_count / total if total > 0 else 0.0
    negative_score = negative_count / total if total > 0 else 0.0
    neutral_score = 1.0 - positive_score - negative_score

    # Ensure neutral has minimum weight
    if neutral_score < 0.1:
        adjustment = 0.1 - neutral_score
        positive_score -= adjustment / 2
        negative_score -= adjustment / 2
        neutral_score = 0.1

    # Clip scores to be non-negative
    positive_score = max(0, positive_score)
    negative_score = max(0, negative_score)

    # Normalize to sum to 1.0
    total_score = positive_score + neutral_score + negative_score

    return {
        "positive": round(positive_score / total_score, 3),
        "neutral": round(neutral_score / total_score, 3),
        "negative": round(negative_score / total_score, 3),
    }
