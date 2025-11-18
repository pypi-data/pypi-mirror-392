#!/usr/bin/env python3
"""
Automatic language detection for bilingual text processing.

This module provides language detection capabilities for seamless
switching between Bangla and English content.
"""

import re
from collections import Counter
from typing import Dict, List, Optional, Tuple


class LanguageDetector:
    """
    Enhanced language detector for Bangla and English text.
    """

    def __init__(self):
        """Initialize the language detector with character sets and patterns."""
        # Bengali Unicode ranges
        self.bengali_ranges = [
            (0x0980, 0x09FF),  # Bengali block
            (0x200C, 0x200D),  # Zero-width joiner/non-joiner
            (0x0964, 0x0965),  # Danda (Bengali punctuation)
        ]

        # Common Bengali words/patterns
        self.bengali_indicators = [
            "আমি",
            "আমার",
            "আমাদের",
            "তুমি",
            "তোমার",
            "আপনি",
            "আপনার",
            "হ্যাঁ",
            "না",
            "কি",
            "কী",
            "কে",
            "কোথায়",
            "কখন",
            "কেন",
            "এটি",
            "এই",
            "ওই",
            "সেই",
            "যে",
            "যিনি",
            "যারা",
            "করা",
            "হওয়া",
            "যাওয়া",
            "আসা",
            "দেওয়া",
            "নেওয়া",
            "বাংলাদেশ",
            "ঢাকা",
            "কলকাতা",
            "ভারত",
            "পাকিস্তান",
        ]

        # Common English words/patterns
        self.english_indicators = [
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "her",
            "was",
            "one",
            "our",
            "had",
            "by",
            "word",
            "but",
            "what",
            "were",
            "we",
            "when",
            "your",
            "said",
            "there",
            "use",
            "each",
            "which",
            "their",
            "time",
            "hello",
            "world",
            "computer",
            "program",
            "language",
            "english",
        ]

        # Compile regex patterns
        bengali_chars = []
        for start, end in self.bengali_ranges:
            bengali_chars.extend(range(start, end + 1))

        self.bengali_pattern = re.compile(f"[{''.join(chr(code) for code in bengali_chars)}]+")

    def is_bengali_char(self, char: str) -> bool:
        """Check if a character is Bengali."""
        code = ord(char)
        return any(start <= code <= end for start, end in self.bengali_ranges)

    def detect_script(self, text: str) -> str:
        """
        Detect the primary script used in text.

        Args:
            text: Input text to analyze

        Returns:
            'bengali', 'english', 'mixed', or 'unknown'
        """
        if not text.strip():
            return "unknown"

        bengali_chars = sum(1 for char in text if self.is_bengali_char(char))
        total_chars = len([char for char in text if char.isalnum() or char.isspace()])

        if total_chars == 0:
            return "unknown"

        bengali_ratio = bengali_chars / total_chars

        if bengali_ratio > 0.7:
            return "bengali"
        elif bengali_ratio < 0.3:
            return "english"
        elif 0.3 <= bengali_ratio <= 0.7:
            return "mixed"
        else:
            return "unknown"

    def detect_language_by_words(self, text: str) -> str:
        """
        Detect language based on common word patterns.

        Args:
            text: Input text to analyze

        Returns:
            'bengali', 'english', or 'mixed'
        """
        words = re.findall(r"\b\w+\b", text.lower())

        bengali_score = 0
        english_score = 0

        for word in words:
            if word in self.bengali_indicators:
                bengali_score += 2  # Higher weight for exact matches
            elif any(bengali_word in word for bengali_word in self.bengali_indicators):
                bengali_score += 1

            if word in self.english_indicators:
                english_score += 2
            elif any(english_word in word for english_word in self.english_indicators):
                english_score += 1

        if bengali_score > english_score:
            return "bengali"
        elif english_score > bengali_score:
            return "english"
        else:
            return "mixed"

    def detect_language(self, text: str, method: str = "combined") -> Dict[str, any]:
        """
        Detect the language of input text using multiple methods.

        Args:
            text: Input text to analyze
            method: Detection method ('script', 'words', or 'combined')

        Returns:
            Dictionary with detection results
        """
        if method == "script":
            script_result = self.detect_script(text)
            confidence = 0.8 if script_result in ["bengali", "english"] else 0.5
            return {
                "language": script_result,
                "confidence": confidence,
                "method": "script_analysis",
            }

        elif method == "words":
            word_result = self.detect_language_by_words(text)
            confidence = 0.7 if word_result in ["bengali", "english"] else 0.4
            return {"language": word_result, "confidence": confidence, "method": "word_analysis"}

        else:  # combined
            script_result = self.detect_script(text)
            word_result = self.detect_language_by_words(text)

            # Combine results
            if script_result == word_result:
                confidence = 0.9
                final_result = script_result
            elif script_result == "mixed" or word_result == "mixed":
                confidence = 0.6
                final_result = "mixed"
            elif script_result == "unknown" or word_result == "unknown":
                confidence = 0.3
                final_result = script_result if script_result != "unknown" else word_result
            else:
                # Different results - use script as primary indicator
                confidence = 0.7
                final_result = script_result

            return {
                "language": final_result,
                "confidence": confidence,
                "method": "combined_analysis",
                "script_result": script_result,
                "word_result": word_result,
            }

    def extract_bengali_text(self, text: str) -> str:
        """Extract only Bengali text from mixed content."""
        return "".join(char for char in text if self.is_bengali_char(char))

    def extract_english_text(self, text: str) -> str:
        """Extract only English text from mixed content."""
        return "".join(
            char
            for char in text
            if not self.is_bengali_char(char) and char.isalnum() or char.isspace()
        )

    def split_by_language(self, text: str) -> List[Tuple[str, str]]:
        """
        Split mixed text into language segments.

        Returns:
            List of (language, text) tuples
        """
        segments = []
        current_lang = None
        current_text = ""

        for char in text:
            if self.is_bengali_char(char):
                if current_lang == "english" and current_text.strip():
                    segments.append(("english", current_text.strip()))
                    current_text = ""
                current_lang = "bengali"
                current_text += char
            else:
                if current_lang == "bengali" and current_text.strip():
                    segments.append(("bengali", current_text.strip()))
                    current_text = ""
                current_lang = "english"
                current_text += char

        # Add final segment
        if current_text.strip():
            segments.append((current_lang, current_text.strip()))

        return segments


# Global language detector instance
_detector = None


def get_language_detector() -> LanguageDetector:
    """Get or create the global language detector instance."""
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector


def detect_language(text: str, **kwargs) -> Dict[str, any]:
    """
    Convenience function to detect language of text.

    Args:
        text: Input text to analyze
        **kwargs: Additional arguments for detection

    Returns:
        Dictionary with detection results
    """
    return get_language_detector().detect_language(text, **kwargs)


def is_bengali(text: str, threshold: float = 0.7) -> bool:
    """
    Check if text is primarily Bengali.

    Args:
        text: Input text to check
        threshold: Confidence threshold (0.0 to 1.0)

    Returns:
        True if text is detected as Bengali with sufficient confidence
    """
    result = detect_language(text)
    return result["language"] == "bengali" and result["confidence"] >= threshold


def is_english(text: str, threshold: float = 0.7) -> bool:
    """
    Check if text is primarily English.

    Args:
        text: Input text to check
        threshold: Confidence threshold (0.0 to 1.0)

    Returns:
        True if text is detected as English with sufficient confidence
    """
    result = detect_language(text)
    return result["language"] == "english" and result["confidence"] >= threshold
