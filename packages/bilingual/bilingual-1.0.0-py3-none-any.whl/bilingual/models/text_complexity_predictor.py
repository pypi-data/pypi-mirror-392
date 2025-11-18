"""
Text Complexity Prediction for Bangla Text.
Multi-output regression model for various readability and complexity metrics.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
from transformers import (
    AutoConfig,
    AutoModel,
    AutoTokenizer,
)

logger = logging.getLogger(__name__)


class TextComplexityPredictor(nn.Module):
    """
    Multi-output regression model for text complexity prediction.
    Predicts multiple readability metrics simultaneously.
    """

    def __init__(
        self,
        base_model_name: str,
        num_outputs: int = 6,
        dropout: float = 0.1,
    ):
        """
        Initialize complexity predictor.

        Args:
            base_model_name: Name of base transformer model
            num_outputs: Number of complexity metrics to predict
            dropout: Dropout probability
        """
        super().__init__()

        self.base_model = AutoModel.from_pretrained(base_model_name)
        hidden_size = self.base_model.config.hidden_size

        # Regression head for multiple metrics
        self.regressor = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, num_outputs),
        )

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor, **kwargs
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs
            attention_mask: Attention mask

        Returns:
            Predicted complexity scores
        """
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

        # Use [CLS] token representation
        pooled_output = outputs.last_hidden_state[:, 0, :]

        # Predict complexity scores
        scores = self.regressor(pooled_output)

        return scores


class ComplexityAnalyzer:
    """
    Analyzer for text complexity and readability metrics in Bangla text.
    """

    METRICS = [
        "flesch_reading_ease",
        "gunning_fog_index",
        "smog_index",
        "coleman_liau_index",
        "automated_readability_index",
        "literary_complexity_score",
    ]

    COMPLEXITY_LEVELS = {
        "very_easy": (0, 30),
        "easy": (30, 50),
        "moderate": (50, 70),
        "difficult": (70, 90),
        "very_difficult": (90, 100),
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize Complexity Analyzer.

        Args:
            model_path: Path to pretrained model
            tokenizer_path: Path to tokenizer
            config_path: Path to task config
            device: Device to run on
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.task_config = json.load(f)
        else:
            self.task_config = {
                "metrics": self.METRICS,
                "num_outputs": len(self.METRICS),
            }

        if model_path and Path(model_path).exists():
            self.model = torch.load(Path(model_path) / "model.pt")
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = None
            self.tokenizer = None
            logger.warning("No pretrained model found, using rule-based metrics")

        if self.model:
            self.model.to(self.device)
            self.model.eval()

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text complexity.

        Args:
            text: Input text

        Returns:
            Dictionary with complexity metrics
        """
        if self.model and self.tokenizer:
            return self._ml_analyze(text)
        else:
            return self._rule_based_analyze(text)

    def _ml_analyze(self, text: str) -> Dict[str, Any]:
        """ML-based complexity analysis."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            scores = self.model(**inputs)[0]

        metrics = {metric: score.item() for metric, score in zip(self.METRICS, scores)}

        # Calculate overall complexity
        overall_complexity = metrics["literary_complexity_score"]
        complexity_level = self._get_complexity_level(overall_complexity)

        return {
            "text": text,
            "metrics": metrics,
            "overall_complexity": overall_complexity,
            "complexity_level": complexity_level,
            "method": "ml",
        }

    def _rule_based_analyze(self, text: str) -> Dict[str, Any]:
        """Rule-based complexity analysis using traditional formulas."""
        if not text.strip():
            return {
                "text": text,
                "metrics": {metric: 0.0 for metric in self.METRICS},
                "overall_complexity": 0.0,
                "complexity_level": "very_easy",
                "text_statistics": {
                    "total_words": 0,
                    "total_sentences": 0,
                    "avg_word_length": 0.0,
                    "avg_sentence_length": 0.0,
                },
                "method": "rule-based",
            }

        # Basic text statistics
        words = text.split()
        sentences = text.count("।") + text.count(".") + text.count("?") + text.count("!")
        sentences = max(sentences, 1)

        total_words = len(words)
        avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
        avg_sentence_length = total_words / sentences

        # Simplified readability metrics
        # Note: These are approximations for Bangla text
        flesch_reading_ease = max(
            0, min(100, 206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / 5))
        )
        gunning_fog = 0.4 * (avg_sentence_length + 100 * (avg_word_length / 10))
        smog = 1.0430 * ((avg_word_length / 5) * 30) ** 0.5 + 3.1291
        coleman_liau = (
            0.0588 * (avg_word_length * 100 / total_words)
            - 0.296 * (sentences * 100 / total_words)
            - 15.8
        )
        ari = 4.71 * (avg_word_length) + 0.5 * avg_sentence_length - 21.43

        # Literary complexity (custom metric)
        literary_complexity = min(100, (avg_sentence_length * 2 + avg_word_length * 10))

        metrics = {
            "flesch_reading_ease": round(flesch_reading_ease, 2),
            "gunning_fog_index": round(gunning_fog, 2),
            "smog_index": round(smog, 2),
            "coleman_liau_index": round(coleman_liau, 2),
            "automated_readability_index": round(ari, 2),
            "literary_complexity_score": round(literary_complexity, 2),
        }

        complexity_level = self._get_complexity_level(literary_complexity)

        return {
            "text": text,
            "metrics": metrics,
            "overall_complexity": literary_complexity,
            "complexity_level": complexity_level,
            "text_statistics": {
                "total_words": total_words,
                "total_sentences": sentences,
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2),
            },
            "method": "rule-based",
        }

    def _get_complexity_level(self, score: float) -> str:
        """Get complexity level from score."""
        for level, (min_score, max_score) in self.COMPLEXITY_LEVELS.items():
            if min_score <= score < max_score:
                return level
        return "very_difficult"

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of analysis results
        """
        return [self.analyze(text) for text in texts]

    def compare_texts(self, texts: List[str]) -> Dict[str, Any]:
        """
        Compare complexity of multiple texts.

        Args:
            texts: List of texts to compare

        Returns:
            Comparison results
        """
        results = self.batch_analyze(texts)

        complexities = [r["overall_complexity"] for r in results]

        return {
            "texts": [
                {"text": t[:50] + "...", "complexity": c} for t, c in zip(texts, complexities)
            ],
            "average_complexity": sum(complexities) / len(complexities),
            "min_complexity": min(complexities),
            "max_complexity": max(complexities),
            "complexity_range": max(complexities) - min(complexities),
        }

    def save(self, output_dir: str):
        """Save model and tokenizer."""
        if not self.model or not self.tokenizer:
            raise ValueError("No model to save")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save model
        torch.save(self.model, output_path / "model.pt")

        # Save tokenizer
        self.tokenizer.save_pretrained(output_dir)

        # Save task config
        with open(output_path / "task_config.json", "w", encoding="utf-8") as f:
            json.dump(self.task_config, f, ensure_ascii=False, indent=2)

        logger.info(f"Model saved to {output_dir}")

    @classmethod
    def from_pretrained(cls, model_path: str):
        """Load pretrained model."""
        return cls(model_path=model_path, tokenizer_path=model_path)
