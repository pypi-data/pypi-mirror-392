"""
Metaphor and Simile Detection for Bangla Literary Text.
Detects figurative language using token classification.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from transformers import (
    AutoConfig,
    AutoModelForTokenClassification,
    AutoTokenizer,
)

logger = logging.getLogger(__name__)


class MetaphorSimileDetector:
    """
    Token classification model for detecting metaphors and similes in Bangla text.
    Uses BIO tagging scheme: B-METAPHOR, I-METAPHOR, B-SIMILE, I-SIMILE, O.
    """

    LABEL_NAMES = [
        "O",  # Outside
        "B-METAPHOR",  # Beginning of metaphor
        "I-METAPHOR",  # Inside metaphor
        "B-SIMILE",  # Beginning of simile
        "I-SIMILE",  # Inside simile
    ]

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize Metaphor and Simile Detector.

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
                "num_labels": len(self.LABEL_NAMES),
                "label_names": self.LABEL_NAMES,
            }

        self.id2label = {i: label for i, label in enumerate(self.LABEL_NAMES)}
        self.label2id = {label: i for i, label in enumerate(self.LABEL_NAMES)}

        if model_path and Path(model_path).exists():
            self.model = AutoModelForTokenClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = None
            self.tokenizer = None
            logger.warning("No pretrained model found")

        if self.model:
            self.model.to(self.device)
            self.model.eval()

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect metaphors and similes in text.

        Args:
            text: Input text

        Returns:
            Dictionary with detected figurative language spans
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
            return_offsets_mapping=True,
        )

        offset_mapping = inputs.pop("offset_mapping")[0]
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)[0]

        # Convert predictions to labels
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predicted_labels = [self.id2label[pred.item()] for pred in predictions]

        # Extract spans
        metaphors = self._extract_spans(text, tokens, predicted_labels, offset_mapping, "METAPHOR")
        similes = self._extract_spans(text, tokens, predicted_labels, offset_mapping, "SIMILE")

        return {
            "text": text,
            "metaphors": metaphors,
            "similes": similes,
            "total_figurative": len(metaphors) + len(similes),
        }

    def _extract_spans(
        self,
        text: str,
        tokens: List[str],
        labels: List[str],
        offset_mapping: torch.Tensor,
        entity_type: str,
    ) -> List[Dict[str, Any]]:
        """Extract entity spans from BIO labels."""
        spans = []
        current_span = None

        for i, (token, label, offset) in enumerate(zip(tokens, labels, offset_mapping)):
            start, end = offset.tolist()

            if label == f"B-{entity_type}":
                # Save previous span if exists
                if current_span:
                    spans.append(current_span)

                # Start new span
                current_span = {
                    "text": text[start:end],
                    "start": start,
                    "end": end,
                    "type": entity_type.lower(),
                }

            elif label == f"I-{entity_type}" and current_span:
                # Continue current span
                current_span["text"] = text[current_span["start"] : end]
                current_span["end"] = end

            elif label == "O" and current_span:
                # End current span
                spans.append(current_span)
                current_span = None

        # Add last span if exists
        if current_span:
            spans.append(current_span)

        return spans

    def batch_detect(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Detect figurative language in multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of detection results
        """
        return [self.detect(text) for text in texts]

    def get_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get figurative language statistics for text.

        Args:
            text: Input text

        Returns:
            Statistics dictionary
        """
        result = self.detect(text)

        words = text.split()
        total_words = len(words)

        metaphor_words = sum(len(m["text"].split()) for m in result["metaphors"])
        simile_words = sum(len(s["text"].split()) for s in result["similes"])

        return {
            "total_words": total_words,
            "metaphor_count": len(result["metaphors"]),
            "simile_count": len(result["similes"]),
            "figurative_word_count": metaphor_words + simile_words,
            "figurative_density": (
                (metaphor_words + simile_words) / total_words if total_words > 0 else 0
            ),
        }

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
