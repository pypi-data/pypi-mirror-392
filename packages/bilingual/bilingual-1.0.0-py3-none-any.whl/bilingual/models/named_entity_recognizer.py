"""
Named Entity Recognition for Bangla Text.
Detects entities like persons, organizations, locations, works, events, etc.
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


class BanglaNER:
    """
    Named Entity Recognition model for Bangla text.
    Supports entities: PER, ORG, LOC, DATE, TIME, WORK, EVENT, LANG, MISC.
    """

    LABEL_NAMES = [
        "O",  # Outside
        "B-PER",  # Person
        "I-PER",
        "B-ORG",  # Organization
        "I-ORG",
        "B-LOC",  # Location
        "I-LOC",
        "B-DATE",  # Date
        "I-DATE",
        "B-TIME",  # Time
        "I-TIME",
        "B-WORK",  # Literary work
        "I-WORK",
        "B-EVENT",  # Event
        "I-EVENT",
        "B-LANG",  # Language
        "I-LANG",
        "B-MISC",  # Miscellaneous
        "I-MISC",
    ]

    ENTITY_TYPES = [
        "PER",  # Person (e.g., রবীন্দ্রনাথ ঠাকুর)
        "ORG",  # Organization (e.g., বিশ্বভারতী)
        "LOC",  # Location (e.g., শান্তিনিকেতন)
        "DATE",  # Date
        "TIME",  # Time
        "WORK",  # Literary work (e.g., গীতাঞ্জলি)
        "EVENT",  # Event (e.g., নোবেল পুরস্কার)
        "LANG",  # Language (e.g., বাংলা)
        "MISC",  # Miscellaneous
    ]

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize Bangla NER model.

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

    def recognize(self, text: str) -> Dict[str, Any]:
        """
        Recognize named entities in text.

        Args:
            text: Input text

        Returns:
            Dictionary with recognized entities
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
            probs = torch.softmax(outputs.logits, dim=-1)[0]

        # Convert predictions to labels
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predicted_labels = [self.id2label[pred.item()] for pred in predictions]
        confidences = [probs[i, pred].item() for i, pred in enumerate(predictions)]

        # Extract entities by type
        entities_by_type = {entity_type: [] for entity_type in self.ENTITY_TYPES}

        for entity_type in self.ENTITY_TYPES:
            entities = self._extract_entities(
                text, tokens, predicted_labels, confidences, offset_mapping, entity_type
            )
            entities_by_type[entity_type] = entities

        # Flatten all entities
        all_entities = []
        for entity_type, entities in entities_by_type.items():
            all_entities.extend(entities)

        # Sort by position
        all_entities.sort(key=lambda x: x["start"])

        return {
            "text": text,
            "entities": all_entities,
            "entities_by_type": entities_by_type,
            "total_entities": len(all_entities),
        }

    def _extract_entities(
        self,
        text: str,
        tokens: List[str],
        labels: List[str],
        confidences: List[float],
        offset_mapping: torch.Tensor,
        entity_type: str,
    ) -> List[Dict[str, Any]]:
        """Extract entities of specific type from BIO labels."""
        entities = []
        current_entity = None

        for i, (token, label, conf, offset) in enumerate(
            zip(tokens, labels, confidences, offset_mapping)
        ):
            start, end = offset.tolist()

            if label == f"B-{entity_type}":
                # Save previous entity if exists
                if current_entity:
                    entities.append(current_entity)

                # Start new entity
                current_entity = {
                    "text": text[start:end],
                    "type": entity_type,
                    "start": start,
                    "end": end,
                    "confidence": conf,
                }

            elif label == f"I-{entity_type}" and current_entity:
                # Continue current entity
                current_entity["text"] = text[current_entity["start"] : end]
                current_entity["end"] = end
                current_entity["confidence"] = (current_entity["confidence"] + conf) / 2

            elif current_entity:
                # End current entity
                entities.append(current_entity)
                current_entity = None

        # Add last entity if exists
        if current_entity:
            entities.append(current_entity)

        return entities

    def batch_recognize(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Recognize entities in multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of recognition results
        """
        return [self.recognize(text) for text in texts]

    def get_entity_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get entity statistics for text.

        Args:
            text: Input text

        Returns:
            Statistics dictionary
        """
        result = self.recognize(text)

        entity_counts = {entity_type: 0 for entity_type in self.ENTITY_TYPES}
        for entity in result["entities"]:
            entity_counts[entity["type"]] += 1

        return {
            "total_entities": result["total_entities"],
            "entity_counts": entity_counts,
            "entity_density": result["total_entities"] / len(text.split()) if text else 0,
            "most_common_type": (
                max(entity_counts.items(), key=lambda x: x[1])[0]
                if result["total_entities"] > 0
                else None
            ),
        }

    def extract_literary_references(self, text: str) -> Dict[str, List[str]]:
        """
        Extract literary references (persons, works, events).

        Args:
            text: Input text

        Returns:
            Dictionary with literary references
        """
        result = self.recognize(text)

        return {
            "authors": [e["text"] for e in result["entities_by_type"]["PER"]],
            "works": [e["text"] for e in result["entities_by_type"]["WORK"]],
            "events": [e["text"] for e in result["entities_by_type"]["EVENT"]],
            "locations": [e["text"] for e in result["entities_by_type"]["LOC"]],
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
