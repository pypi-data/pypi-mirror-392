"""
Poetic meter detection for Bengali and English text.

This module provides both rule-based and ML-based syllable and rhythm analysis
to detect traditional Bengali meter (মাত্রা/ছন্দ) and English metrical patterns.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional ML imports - only needed for PoeticMeterDetector class
try:
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)


def _count_syllables_english(word: str) -> int:
    """
    Estimate syllable count for English words using vowel clusters.

    This is a heuristic approximation, not linguistically precise.

    Args:
        word: English word

    Returns:
        Estimated syllable count
    """
    word = word.lower().strip()
    if len(word) == 0:
        return 0

    # Remove non-alphabetic characters
    word = re.sub(r"[^a-z]", "", word)

    # Count vowel groups
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith("e"):
        syllable_count -= 1

    # Ensure at least 1 syllable
    if syllable_count == 0:
        syllable_count = 1

    return syllable_count


def _count_matra_bengali(word: str) -> int:
    """
    Estimate মাত্রা (matra) count for Bengali words.

    This is a simplified character-based heuristic. Traditional মাত্রা
    counting requires phonetic analysis and linguistic rules.

    Args:
        word: Bengali word

    Returns:
        Estimated matra count
    """
    if not word:
        return 0

    # Bengali vowels and diacritics
    bengali_vowels = "অআইঈউঊঋএঐওঔ"
    bengali_consonants = "কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎ"

    # Count consonants as base units
    matra_count = 0
    for char in word:
        if char in bengali_consonants:
            matra_count += 1
        elif char in bengali_vowels:
            matra_count += 1

    return max(matra_count, 1)


def detect_meter(text: str, language: str = "auto") -> Dict[str, Any]:
    """
    Detect poetic meter in text by analyzing syllable/matra patterns per line.

    Args:
        text: Input text (can be multi-line)
        language: 'bengali', 'english', or 'auto' for automatic detection

    Returns:
        Dictionary containing:
        - 'lines': List of line-wise analysis
        - 'pattern': Detected meter pattern (if consistent)
        - 'language': Detected or specified language

    Examples:
        >>> detect_meter("Shall I compare thee to a summer's day?")
        {'lines': [...], 'pattern': 'iambic', 'language': 'english'}
    """
    lines = text.strip().split("\n")
    line_analysis = []

    # Auto-detect language from first line
    if language == "auto":
        first_line = lines[0] if lines else ""
        # Simple heuristic: check for Bengali characters
        has_bengali = bool(re.search(r"[\u0980-\u09FF]", first_line))
        language = "bengali" if has_bengali else "english"

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        words = line.split()

        if language == "bengali":
            # Count matra per word
            word_counts = [_count_matra_bengali(w) for w in words]
            total_units = sum(word_counts)
            unit_type = "matra"
        else:
            # Count syllables per word
            word_counts = [_count_syllables_english(w) for w in words]
            total_units = sum(word_counts)
            unit_type = "syllables"

        line_analysis.append(
            {
                "line_number": line_num,
                "text": line,
                "word_count": len(words),
                f"{unit_type}_per_word": word_counts,
                f"total_{unit_type}": total_units,
            }
        )

    # Detect pattern consistency
    if line_analysis:
        unit_counts = [la[f"total_{unit_type}"] for la in line_analysis]
        avg_units = sum(unit_counts) / len(unit_counts)
        variance = sum((x - avg_units) ** 2 for x in unit_counts) / len(unit_counts)

        # Simple pattern classification
        if variance < 2.0:
            pattern = "consistent"
        elif language == "english" and 8 <= avg_units <= 12:
            pattern = "iambic"  # Rough approximation
        elif language == "bengali" and 12 <= avg_units <= 16:
            pattern = "payar"  # পয়ার ছন্দ approximation
        else:
            pattern = "irregular"
    else:
        pattern = "unknown"

    return {
        "lines": line_analysis,
        "pattern": pattern,
        "language": language,
        "summary": {
            "total_lines": len(line_analysis),
            "avg_units_per_line": round(avg_units, 1) if line_analysis else 0,
        },
    }


class PoeticMeterDetector:
    """
    ML-based poetic meter detector for Bengali poetry.
    Classifies poems into traditional Bengali meter types.

    Requires torch and transformers to be installed:
        pip install torch transformers
    """

    METER_TYPES = [
        "অক্ষরবৃত্ত",  # Akshara-vritta
        "মাত্রাবৃত্ত",  # Matra-vritta
        "স্বরবৃত্ত",  # Svara-vritta
        "পয়ার",  # Payar
        "মুক্তক",  # Muktak (free verse)
        "গদ্যছন্দ",  # Gadya-chhanda (prose rhythm)
        "অমিত্রাক্ষর",  # Amitrakshar (blank verse)
        "other",
    ]

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the Poetic Meter Detector.

        Args:
            model_path: Path to pretrained model
            tokenizer_path: Path to tokenizer
            config_path: Path to task config
            device: Device to run on

        Raises:
            ImportError: If torch or transformers not installed
        """
        if not _TORCH_AVAILABLE:
            raise ImportError(
                "PoeticMeterDetector requires torch and transformers. "
                "Install with: pip install torch transformers"
            )

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.task_config = json.load(f)
        else:
            self.task_config = {
                "num_labels": len(self.METER_TYPES),
                "label_names": self.METER_TYPES,
            }

        if model_path and Path(model_path).exists():
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = None
            self.tokenizer = None
            logger.warning("No pretrained model found, using rule-based detection")

        if self.model:
            self.model.to(self.device)
            self.model.eval()

    def detect(self, poem: str) -> Dict[str, Any]:
        """
        Detect the meter type of a Bengali poem.

        Args:
            poem: Bengali poem text (can be multi-line)

        Returns:
            Dictionary with meter type and confidence scores
        """
        if self.model and self.tokenizer:
            return self._ml_detect(poem)
        else:
            return self._rule_based_detect(poem)

    def _ml_detect(self, poem: str) -> Dict[str, Any]:
        """ML-based meter detection."""
        inputs = self.tokenizer(
            poem,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)

        predicted_idx = torch.argmax(probs, dim=-1).item()
        confidence = probs[0, predicted_idx].item()

        # Get top 3 predictions
        top_probs, top_indices = torch.topk(probs[0], k=min(3, len(self.METER_TYPES)))
        top_predictions = [
            {
                "meter": self.METER_TYPES[idx],
                "confidence": prob.item(),
            }
            for prob, idx in zip(top_probs, top_indices)
        ]

        return {
            "meter_type": self.METER_TYPES[predicted_idx],
            "confidence": confidence,
            "top_predictions": top_predictions,
            "method": "ml",
        }

    def _rule_based_detect(self, poem: str) -> Dict[str, Any]:
        """Rule-based meter detection using traditional patterns."""
        analysis = detect_meter(poem, language="bengali")

        lines = analysis["lines"]
        if not lines:
            return {
                "meter_type": "unknown",
                "confidence": 0.0,
                "method": "rule-based",
            }

        # Analyze matra patterns
        matra_counts = [line["total_matra"] for line in lines]
        avg_matra = sum(matra_counts) / len(matra_counts)

        # Classify based on average matra count
        if 12 <= avg_matra <= 14:
            meter_type = "অক্ষরবৃত্ত"
            confidence = 0.7
        elif 14 <= avg_matra <= 16:
            meter_type = "পয়ার"
            confidence = 0.7
        elif 8 <= avg_matra <= 10:
            meter_type = "স্বরবৃত্ত"
            confidence = 0.6
        elif avg_matra > 20:
            meter_type = "গদ্যছন্দ"
            confidence = 0.6
        else:
            meter_type = "মুক্তক"
            confidence = 0.5

        return {
            "meter_type": meter_type,
            "confidence": confidence,
            "avg_matra": round(avg_matra, 1),
            "method": "rule-based",
            "analysis": analysis,
        }

    def batch_detect(self, poems: List[str]) -> List[Dict[str, Any]]:
        """
        Detect meter for multiple poems.

        Args:
            poems: List of poem texts

        Returns:
            List of detection results
        """
        return [self.detect(poem) for poem in poems]

    def save(self, output_dir: str):
        """Save model and tokenizer."""
        if not self.model or not self.tokenizer:
            raise ValueError("No model to save")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        # Save task config
        with open(output_path / "task_config.json", "w", encoding="utf-8") as f:
            json.dump(self.task_config, f, ensure_ascii=False, indent=2)

        logger.info(f"Model saved to {output_dir}")

    @classmethod
    def from_pretrained(cls, model_path: str):
        """Load pretrained model."""
        return cls(model_path=model_path, tokenizer_path=model_path)
