#!/usr/bin/env python3
"""
Multi-input processing for mixed-language text.

This module provides capabilities to handle mixed-language content
where Bangla and English text appear together in the same input.
"""

import re
from typing import Any, Dict, List


class MultiInputProcessor:
    """
    Processor for handling mixed-language text input.
    """

    def __init__(self):
        """Initialize the multi-input processor."""
        # Language-specific processing rules
        self.language_patterns = {
            "bengali": re.compile(r"[\u0980-\u09FF]+"),
            "english": re.compile(r"[a-zA-Z]+"),
            "mixed": re.compile(r"[\u0980-\u09FFa-zA-Z]+"),
        }

        # Common mixed-language patterns
        self.mixed_patterns = [
            (r"(\w+)[\u0980-\u09FF]+(\w+)", "word_bengali_word"),
            (r"[\u0980-\u09FF]+(\w+)", "bengali_word"),
            (r"(\w+)[\u0980-\u09FF]+", "word_bengali"),
        ]

    def detect_language_segments(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect and segment text by language.

        Args:
            text: Input text that may contain mixed languages

        Returns:
            List of segments with language information
        """
        segments = []

        # Find all language segments
        for match in self.language_patterns["mixed"].finditer(text):
            segment_text = match.group()
            segment_start = match.start()
            segment_end = match.end()

            # Determine primary language in segment
            bengali_chars = len([c for c in segment_text if "\u0980" <= c <= "\u09ff"])
            english_chars = len([c for c in segment_text if "a" <= c.lower() <= "z"])

            if bengali_chars > english_chars:
                primary_lang = "bengali"
            elif english_chars > bengali_chars:
                primary_lang = "english"
            else:
                primary_lang = "mixed"

            segments.append(
                {
                    "text": segment_text,
                    "start": segment_start,
                    "end": segment_end,
                    "language": primary_lang,
                    "length": len(segment_text),
                }
            )

        return segments

    def split_mixed_text(self, text: str) -> Dict[str, List[str]]:
        """
        Split mixed text into separate language components.

        Args:
            text: Mixed language text

        Returns:
            Dictionary with 'bengali' and 'english' keys containing text segments
        """
        result = {"bengali": [], "english": [], "mixed": []}

        # Extract Bengali text
        bengali_text = "".join(self.language_patterns["bengali"].findall(text))
        if bengali_text:
            result["bengali"].append(bengali_text)

        # Extract English text
        english_text = " ".join(self.language_patterns["english"].findall(text))
        if english_text:
            result["english"].append(english_text)

        # Extract mixed segments
        mixed_segments = []
        for match in re.finditer(r"[\u0980-\u09FF]+[a-zA-Z]+|[\u0980-\u09FF]+", text):
            segment = match.group()
            if len(segment) > 1:  # Only substantial segments
                mixed_segments.append(segment)

        if mixed_segments:
            result["mixed"] = mixed_segments

        return result

    def process_mixed_input(self, text: str, operation: str = "segment") -> Dict[str, Any]:
        """
        Process mixed-language input with various operations.

        Args:
            text: Input text
            operation: Type of processing ('segment', 'translate', 'analyze')

        Returns:
            Processing results
        """
        if operation == "segment":
            return self._segment_mixed_text(text)
        elif operation == "analyze":
            return self._analyze_mixed_text(text)
        elif operation == "translate":
            return self._translate_mixed_text(text)
        else:
            return {"error": f"Unknown operation: {operation}"}

    def _segment_mixed_text(self, text: str) -> Dict[str, Any]:
        """Segment mixed text into language-specific parts."""
        segments = self.detect_language_segments(text)

        # Group consecutive segments of same language
        grouped_segments = []
        current_group = None

        for segment in segments:
            if current_group is None:
                current_group = {
                    "language": segment["language"],
                    "text": segment["text"],
                    "start": segment["start"],
                    "end": segment["end"],
                }
            elif current_group["language"] == segment["language"]:
                # Extend current group
                current_group["text"] += segment["text"]
                current_group["end"] = segment["end"]
            else:
                # Save current group and start new one
                grouped_segments.append(current_group)
                current_group = {
                    "language": segment["language"],
                    "text": segment["text"],
                    "start": segment["start"],
                    "end": segment["end"],
                }

        # Add final group
        if current_group:
            grouped_segments.append(current_group)

        return {
            "original_text": text,
            "segments": grouped_segments,
            "segment_count": len(grouped_segments),
        }

    def _analyze_mixed_text(self, text: str) -> Dict[str, Any]:
        """Analyze mixed text characteristics."""
        segments = self.detect_language_segments(text)
        split_result = self.split_mixed_text(text)

        # Calculate statistics
        total_length = len(text)
        bengali_length = sum(
            len(segment["text"]) for segment in segments if segment["language"] == "bengali"
        )
        english_length = sum(
            len(segment["text"]) for segment in segments if segment["language"] == "english"
        )

        analysis = {
            "original_text": text,
            "total_length": total_length,
            "bengali_ratio": bengali_length / total_length if total_length > 0 else 0,
            "english_ratio": english_length / total_length if total_length > 0 else 0,
            "mixed_ratio": len(split_result["mixed"]) / total_length if total_length > 0 else 0,
            "language_distribution": {
                "bengali_segments": len(split_result["bengali"]),
                "english_segments": len(split_result["english"]),
                "mixed_segments": len(split_result["mixed"]),
            },
            "dominant_language": "bengali" if bengali_length > english_length else "english",
        }

        return analysis

    def _translate_mixed_text(self, text: str) -> Dict[str, Any]:
        """
        Simulate translation of mixed text.
        In practice, this would use actual translation models.
        """
        # This is a placeholder - real implementation would use translation APIs
        segments = self.detect_language_segments(text)

        translated_segments = []
        for segment in segments:
            if segment["language"] == "bengali":
                # Simulate Bengali to English translation
                translated_segments.append(
                    {
                        "original": segment["text"],
                        "translated": f"[BN->EN: {segment['text']}]",
                        "source_lang": "bengali",
                        "target_lang": "english",
                    }
                )
            elif segment["language"] == "english":
                # Simulate English to Bengali translation
                translated_segments.append(
                    {
                        "original": segment["text"],
                        "translated": f"[EN->BN: {segment['text']}]",
                        "source_lang": "english",
                        "target_lang": "bengali",
                    }
                )
            else:
                translated_segments.append(
                    {
                        "original": segment["text"],
                        "translated": segment["text"],  # No translation for mixed
                        "source_lang": "mixed",
                        "target_lang": "mixed",
                    }
                )

        return {
            "original_text": text,
            "translated_segments": translated_segments,
            "translation_count": len(
                [s for s in translated_segments if s["source_lang"] != s["target_lang"]]
            ),
        }

    def create_training_pairs(
        self, mixed_text: str, target_language: str = "english"
    ) -> List[Dict[str, str]]:
        """
        Create training pairs from mixed text for translation tasks.

        Args:
            mixed_text: Mixed language text
            target_language: Target language for translation

        Returns:
            List of source-target pairs for training
        """
        segments = self.detect_language_segments(mixed_text)
        training_pairs = []

        for segment in segments:
            if segment["language"] == "bengali" and target_language == "english":
                # Bengali source -> English target (placeholder)
                training_pairs.append(
                    {
                        "source": segment["text"],
                        "target": f"[Translation of: {segment['text']}]",
                        "source_lang": "bengali",
                        "target_lang": "english",
                    }
                )
            elif segment["language"] == "english" and target_language == "bengali":
                # English source -> Bengali target (placeholder)
                training_pairs.append(
                    {
                        "source": segment["text"],
                        "target": f"[বাংলায় অনুবাদ: {segment['text']}]",
                        "source_lang": "english",
                        "target_lang": "bengali",
                    }
                )

        return training_pairs

    def extract_code_switched_text(self, text: str) -> List[str]:
        """
        Extract examples of code-switching (language mixing).

        Args:
            text: Input text that may contain code-switching

        Returns:
            List of code-switched segments
        """
        code_switched = []

        # Pattern for English words in Bengali context
        english_in_bengali = re.findall(r"[\u0980-\u09FF\s]*[a-zA-Z]+[\u0980-\u09FF\s]*", text)

        # Pattern for Bengali words in English context
        bengali_in_english = re.findall(r"[a-zA-Z\s]*[\u0980-\u09FF]+[a-zA-Z\s]*", text)

        # Filter substantial examples
        for example in english_in_bengali + bengali_in_english:
            if len(example.strip()) > 3:
                code_switched.append(example.strip())

        return list(set(code_switched))  # Remove duplicates


# Global processor instance
_processor = None


def get_multi_input_processor() -> MultiInputProcessor:
    """Get or create the global multi-input processor instance."""
    global _processor
    if _processor is None:
        _processor = MultiInputProcessor()
    return _processor


def process_mixed_text(text: str, operation: str = "analyze") -> Dict[str, Any]:
    """
    Convenience function to process mixed-language text.

    Args:
        text: Input mixed-language text
        operation: Processing operation ('analyze', 'segment', 'translate')

    Returns:
        Processing results
    """
    return get_multi_input_processor().process_mixed_input(text, operation)


def detect_language_segments(text: str) -> List[Dict[str, Any]]:
    """
    Convenience function to detect language segments in text.

    Args:
        text: Input text

    Returns:
        List of language segments
    """
    return get_multi_input_processor().detect_language_segments(text)


def split_mixed_text(text: str) -> Dict[str, List[str]]:
    """
    Convenience function to split mixed text by language.

    Args:
        text: Mixed language text

    Returns:
        Dictionary with language-specific text segments
    """
    return get_multi_input_processor().split_mixed_text(text)
