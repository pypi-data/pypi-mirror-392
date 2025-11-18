"""
Poetic meter analysis for Bangla and English poetry.
Supports various traditional meters and patterns.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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


def count_syllables(word: str, language: str = "en") -> int:
    """
    Count syllables in a word using language-specific heuristics.

    Args:
        word: Input word
        language: Language code ('en' or 'bn')

    Returns:
        Number of syllables
    """
    word = word.lower().strip()
    if not word:
        return 0

    if language == "en":
        # English syllable counting
        word = re.sub(r"[^a-z]", "", word)
        if not word:
            return 0

        # Count vowel groups
        return len(re.findall(r"[aeiouy]+", word))

    elif language == "bn":
        # Bangla syllable counting (approximate)
        # Each vowel or matra typically represents a syllable
        return len(re.findall(r"[\u0985-\u0994\u09BE-\u09CC]", word))

    return 0


def detect_meter(text: str, language: str = "bn") -> Dict[str, Union[str, int, List[int]]]:
    """
    Analyze poetic meter in text.

    Args:
        text: Input text (poem)
        language: Language code ('en' or 'bn')

    Returns:
        Dictionary with meter analysis
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    syllable_counts = []

    for line in lines:
        words = re.findall(r"\w+", line)
        syllables = sum(count_syllables(word, language) for word in words)
        syllable_counts.append(syllables)

    # Determine meter type based on syllable pattern
    meter_type = "unknown"
    if len(set(syllable_counts)) == 1:
        meter_type = f"fixed_{syllable_counts[0]}_syllables"

    return {
        "meter_type": meter_type,
        "syllable_counts": syllable_counts,
        "line_count": len(lines),
        "avg_syllables": sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0,
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
