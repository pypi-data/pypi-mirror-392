"""
Sentiment and Tone Classification for Bangla Literary Text.
Multi-label classification for sentiment (positive/neutral/negative)
and literary tone (formal/informal/poetic/dramatic/etc.).
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


class SentimentToneClassifier(nn.Module):
    """
    Multi-task model for sentiment and tone classification.
    Predicts both sentiment (3 classes) and tone (8 classes) simultaneously.
    """

    def __init__(
        self,
        base_model_name: str,
        num_sentiment_labels: int = 3,
        num_tone_labels: int = 8,
        dropout: float = 0.1,
    ):
        """
        Initialize multi-task classifier.

        Args:
            base_model_name: Name of base transformer model
            num_sentiment_labels: Number of sentiment classes
            num_tone_labels: Number of tone classes
            dropout: Dropout probability
        """
        super().__init__()

        self.base_model = AutoModel.from_pretrained(base_model_name)
        hidden_size = self.base_model.config.hidden_size

        # Sentiment classification head
        self.sentiment_classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_sentiment_labels),
        )

        # Tone classification head (multi-label)
        self.tone_classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_tone_labels),
        )

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor, **kwargs
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs
            attention_mask: Attention mask

        Returns:
            Dictionary with sentiment and tone logits
        """
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

        # Use [CLS] token representation
        pooled_output = outputs.last_hidden_state[:, 0, :]

        sentiment_logits = self.sentiment_classifier(pooled_output)
        tone_logits = self.tone_classifier(pooled_output)

        return {
            "sentiment_logits": sentiment_logits,
            "tone_logits": tone_logits,
        }


class SentimentToneAnalyzer:
    """
    Analyzer for sentiment and literary tone in Bangla text.
    """

    SENTIMENT_LABELS = ["positive", "neutral", "negative"]

    TONE_LABELS = [
        "formal",
        "informal",
        "poetic",
        "dramatic",
        "melancholic",
        "joyful",
        "satirical",
        "romantic",
    ]

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize Sentiment and Tone Analyzer.

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
                "sentiment_labels": self.SENTIMENT_LABELS,
                "tone_labels": self.TONE_LABELS,
            }

        if model_path and Path(model_path).exists():
            # Load custom multi-task model
            self.model = torch.load(Path(model_path) / "model.pt")
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = None
            self.tokenizer = None
            logger.warning("No pretrained model found")

        if self.model:
            self.model.to(self.device)
            self.model.eval()

    def analyze(
        self,
        text: str,
        tone_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment and tone of text.

        Args:
            text: Input text
            tone_threshold: Threshold for multi-label tone classification

        Returns:
            Dictionary with sentiment and tone predictions
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

            sentiment_logits = outputs["sentiment_logits"]
            tone_logits = outputs["tone_logits"]

            # Sentiment: single-label classification
            sentiment_probs = torch.softmax(sentiment_logits, dim=-1)[0]
            sentiment_idx = torch.argmax(sentiment_probs).item()
            sentiment = self.SENTIMENT_LABELS[sentiment_idx]
            sentiment_confidence = sentiment_probs[sentiment_idx].item()

            # Tone: multi-label classification
            tone_probs = torch.sigmoid(tone_logits)[0]
            detected_tones = []

            for i, (tone, prob) in enumerate(zip(self.TONE_LABELS, tone_probs)):
                if prob.item() >= tone_threshold:
                    detected_tones.append(
                        {
                            "tone": tone,
                            "confidence": prob.item(),
                        }
                    )

            # Sort by confidence
            detected_tones.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "text": text,
            "sentiment": {
                "label": sentiment,
                "confidence": sentiment_confidence,
                "all_scores": {
                    label: prob.item()
                    for label, prob in zip(self.SENTIMENT_LABELS, sentiment_probs)
                },
            },
            "tones": detected_tones,
            "primary_tone": detected_tones[0]["tone"] if detected_tones else "neutral",
        }

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of analysis results
        """
        return [self.analyze(text) for text in texts]

    def get_sentiment_distribution(self, texts: List[str]) -> Dict[str, float]:
        """
        Get sentiment distribution across multiple texts.

        Args:
            texts: List of texts

        Returns:
            Distribution of sentiments
        """
        results = self.batch_analyze(texts)

        sentiment_counts = {label: 0 for label in self.SENTIMENT_LABELS}
        for result in results:
            sentiment_counts[result["sentiment"]["label"]] += 1

        total = len(results)
        return {label: count / total for label, count in sentiment_counts.items()}

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
