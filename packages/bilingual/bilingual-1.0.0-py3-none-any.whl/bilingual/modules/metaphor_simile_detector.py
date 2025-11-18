"""
Metaphor and Simile Detection for Bangla text.

This module provides functionality to detect and extract metaphors and similes
from Bangla literary text using both pattern-based and ML-based approaches.
"""

import logging
import re
from typing import Dict, List, Optional

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


class MetaphorSimileDetector:
    """
    Detector for metaphors and similes in Bangla text.

    Supports both:
    1. Pattern-based detection (rule-based)
    2. ML-based detection (fine-tuned classifier)
    """

    # Common Bangla simile markers
    SIMILE_MARKERS = [
        r"যেন",  # like, as if
        r"মতো",  # like
        r"মত",  # like
        r"সমান",  # equal to
        r"তুল্য",  # similar to
        r"ন্যায়",  # like
        r"প্রায়",  # almost like
        r"যথা",  # such as
        r"সদৃশ",  # similar
        r"অনুরূপ",  # analogous
    ]

    # Metaphor indicators (verbs often used metaphorically)
    METAPHOR_VERBS = [
        r"হয়ে যাওয়া",  # become
        r"পরিণত",  # transform
        r"রূপান্তর",  # metamorphose
        r"ছড়িয়ে",  # spread
        r"জ্বলছে",  # burning
        r"গলছে",  # melting
        r"ফুটছে",  # blooming
    ]

    def __init__(self, model_path: Optional[str] = None, use_ml: bool = False):
        """
        Initialize the detector.

        Args:
            model_path: Path to fine-tuned classifier (optional)
            use_ml: Whether to use ML-based detection
        """
        self.use_ml = use_ml and HAS_TRANSFORMERS
        self.model_path = model_path
        self._model = None
        self._tokenizer = None

        if self.use_ml and not HAS_TRANSFORMERS:
            logger.warning("transformers not available, falling back to pattern-based detection")
            self.use_ml = False

    def load_model(self):
        """Load the ML model for detection."""
        if not self.use_ml:
            return

        if self._model is not None:
            return  # Already loaded

        if not self.model_path:
            logger.warning("No model path provided for ML detection")
            return

        logger.info(f"Loading metaphor/simile classifier from {self.model_path}")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self._model.eval()

    def detect_similes(self, text: str) -> List[Dict[str, str]]:
        """
        Detect similes in the given text.

        Args:
            text: Input Bangla text

        Returns:
            List of detected similes with context
        """
        if self.use_ml:
            return self._detect_similes_ml(text)
        else:
            return self._detect_similes_pattern(text)

    def _detect_similes_pattern(self, text: str) -> List[Dict[str, str]]:
        """Pattern-based simile detection."""
        similes = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            for marker in self.SIMILE_MARKERS:
                pattern = rf"([^।]+{marker}[^।]+)"
                matches = re.finditer(pattern, sentence)

                for match in matches:
                    simile_text = match.group(1).strip()
                    if len(simile_text) > 5:  # Filter very short matches
                        similes.append(
                            {
                                "text": simile_text,
                                "marker": marker,
                                "type": "simile",
                                "confidence": 0.8,  # Pattern-based confidence
                                "method": "pattern",
                            }
                        )

        return similes

    def _detect_similes_ml(self, text: str) -> List[Dict[str, str]]:
        """ML-based simile detection."""
        if self._model is None:
            self.load_model()

        if self._model is None:
            return self._detect_similes_pattern(text)

        similes = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Classify sentence
            inputs = self._tokenizer(
                sentence,
                return_tensors="pt",
                truncation=True,
                max_length=128,
            )

            with torch.no_grad():
                outputs = self._model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)

                # Assuming labels: 0=literal, 1=simile, 2=metaphor
                simile_prob = probs[0][1].item()

                if simile_prob > 0.5:
                    similes.append(
                        {
                            "text": sentence,
                            "type": "simile",
                            "confidence": simile_prob,
                            "method": "ml",
                        }
                    )

        return similes

    def detect_metaphors(self, text: str) -> List[Dict[str, str]]:
        """
        Detect metaphors in the given text.

        Args:
            text: Input Bangla text

        Returns:
            List of detected metaphors with context
        """
        if self.use_ml:
            return self._detect_metaphors_ml(text)
        else:
            return self._detect_metaphors_pattern(text)

    def _detect_metaphors_pattern(self, text: str) -> List[Dict[str, str]]:
        """Pattern-based metaphor detection."""
        metaphors = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Look for metaphorical verb patterns
            for verb in self.METAPHOR_VERBS:
                if re.search(verb, sentence):
                    # Check if it's not a simile (no simile markers)
                    has_simile_marker = any(
                        re.search(marker, sentence) for marker in self.SIMILE_MARKERS
                    )

                    if not has_simile_marker:
                        metaphors.append(
                            {
                                "text": sentence,
                                "indicator": verb,
                                "type": "metaphor",
                                "confidence": 0.6,  # Lower confidence for pattern-based
                                "method": "pattern",
                            }
                        )
                        break  # One metaphor per sentence

        return metaphors

    def _detect_metaphors_ml(self, text: str) -> List[Dict[str, str]]:
        """ML-based metaphor detection."""
        if self._model is None:
            self.load_model()

        if self._model is None:
            return self._detect_metaphors_pattern(text)

        metaphors = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            inputs = self._tokenizer(
                sentence,
                return_tensors="pt",
                truncation=True,
                max_length=128,
            )

            with torch.no_grad():
                outputs = self._model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)

                # Assuming labels: 0=literal, 1=simile, 2=metaphor
                metaphor_prob = probs[0][2].item()

                if metaphor_prob > 0.5:
                    metaphors.append(
                        {
                            "text": sentence,
                            "type": "metaphor",
                            "confidence": metaphor_prob,
                            "method": "ml",
                        }
                    )

        return metaphors

    def extract_figurative_language(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract all figurative language (metaphors and similes).

        Args:
            text: Input Bangla text

        Returns:
            Dictionary containing metaphors and similes
        """
        return {
            "metaphors": self.detect_metaphors(text),
            "similes": self.detect_similes(text),
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using Bangla punctuation."""
        # Split by দাঁড়ি (।), question mark, exclamation
        sentences = re.split(r"[।?!]", text)
        return [s.strip() for s in sentences if s.strip()]

    @classmethod
    def from_pretrained(cls, model_path: str):
        """Load a pretrained metaphor/simile classifier."""
        instance = cls(model_path=model_path, use_ml=True)
        instance.load_model()
        return instance


# Convenience functions for backward compatibility
_default_detector = None


def _get_default_detector():
    """Get or create default detector instance."""
    global _default_detector
    if _default_detector is None:
        _default_detector = MetaphorSimileDetector(use_ml=False)
    return _default_detector


def detect_metaphors(text: str) -> List[Dict[str, str]]:
    """
    Detect metaphors in the given text using pattern-based approach.

    Args:
        text: Input Bangla text

    Returns:
        List of detected metaphors with context
    """
    detector = _get_default_detector()
    return detector.detect_metaphors(text)


def detect_similes(text: str) -> List[Dict[str, str]]:
    """
    Detect similes in the given text using pattern-based approach.

    Args:
        text: Input Bangla text

    Returns:
        List of detected similes with context
    """
    detector = _get_default_detector()
    return detector.detect_similes(text)


def extract_figurative_language(text: str) -> Dict[str, List[Dict]]:
    """
    Extract all figurative language (metaphors and similes).

    Args:
        text: Input Bangla text

    Returns:
        Dictionary containing metaphors and similes
    """
    detector = _get_default_detector()
    return detector.extract_figurative_language(text)
