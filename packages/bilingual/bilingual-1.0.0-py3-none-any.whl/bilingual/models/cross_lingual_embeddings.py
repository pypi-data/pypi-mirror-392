"""
Cross-Lingual Embeddings for Bangla ↔ English.
Sentence-level embeddings for semantic similarity across languages.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from transformers import (
    AutoModel,
    AutoTokenizer,
)

logger = logging.getLogger(__name__)


class CrossLingualEmbeddings:
    """
    Cross-lingual sentence embeddings for Bangla and English.
    Maps sentences from both languages into a shared semantic space.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
        pooling_mode: str = "mean",
    ):
        """
        Initialize Cross-Lingual Embeddings model.

        Args:
            model_path: Path to pretrained model
            tokenizer_path: Path to tokenizer
            config_path: Path to config
            device: Device to run on
            pooling_mode: Pooling strategy ('mean', 'max', 'cls')
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pooling_mode = pooling_mode

        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "pooling_mode": pooling_mode,
                "languages": ["bn", "en"],
            }

        if model_path and Path(model_path).exists():
            self.model = AutoModel.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = None
            self.tokenizer = None
            logger.warning("No pretrained model found")

        if self.model:
            self.model.to(self.device)
            self.model.eval()

    def encode(
        self,
        sentences: Union[str, List[str]],
        batch_size: int = 32,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Encode sentences into embeddings.

        Args:
            sentences: Single sentence or list of sentences
            batch_size: Batch size for encoding
            normalize: Whether to normalize embeddings

        Returns:
            Sentence embeddings as numpy array
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")

        if isinstance(sentences, str):
            sentences = [sentences]

        all_embeddings = []

        for i in range(0, len(sentences), batch_size):
            batch = sentences[i : i + batch_size]

            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = self._pool_embeddings(
                    outputs.last_hidden_state, inputs["attention_mask"]
                )

            all_embeddings.append(embeddings.cpu().numpy())

        embeddings = np.vstack(all_embeddings)

        if normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        return embeddings

    def _pool_embeddings(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Pool token embeddings to sentence embeddings."""
        if self.pooling_mode == "cls":
            # Use [CLS] token
            return hidden_states[:, 0, :]

        elif self.pooling_mode == "max":
            # Max pooling
            hidden_states[attention_mask == 0] = -1e9
            return torch.max(hidden_states, dim=1)[0]

        else:  # mean pooling
            # Mean pooling with attention mask
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
            sum_embeddings = torch.sum(hidden_states * input_mask_expanded, dim=1)
            sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
            return sum_embeddings / sum_mask

    def similarity(
        self,
        sentences1: Union[str, List[str]],
        sentences2: Union[str, List[str]],
    ) -> Union[float, np.ndarray]:
        """
        Calculate cosine similarity between sentences.

        Args:
            sentences1: First sentence(s)
            sentences2: Second sentence(s)

        Returns:
            Similarity score(s)
        """
        emb1 = self.encode(sentences1)
        emb2 = self.encode(sentences2)

        # Cosine similarity
        similarity = np.sum(emb1 * emb2, axis=1)

        if len(similarity) == 1:
            return float(similarity[0])
        return similarity

    def find_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Find most similar sentences to query.

        Args:
            query: Query sentence
            candidates: List of candidate sentences
            top_k: Number of top results to return

        Returns:
            List of (sentence, similarity_score) tuples
        """
        query_emb = self.encode(query)
        candidate_embs = self.encode(candidates)

        # Calculate similarities
        similarities = np.dot(candidate_embs, query_emb.T).flatten()

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = [(candidates[idx], float(similarities[idx])) for idx in top_indices]

        return results

    def translate_search(
        self,
        query: str,
        target_sentences: List[str],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Cross-lingual semantic search.
        Find semantically similar sentences in target language.

        Args:
            query: Query in source language
            target_sentences: Sentences in target language
            top_k: Number of results

        Returns:
            List of (sentence, similarity_score) tuples
        """
        return self.find_similar(query, target_sentences, top_k)

    def align_sentences(
        self,
        sentences_lang1: List[str],
        sentences_lang2: List[str],
        threshold: float = 0.7,
    ) -> List[Tuple[int, int, float]]:
        """
        Align sentences between two languages based on semantic similarity.

        Args:
            sentences_lang1: Sentences in first language
            sentences_lang2: Sentences in second language
            threshold: Minimum similarity threshold

        Returns:
            List of (idx1, idx2, similarity) tuples
        """
        emb1 = self.encode(sentences_lang1)
        emb2 = self.encode(sentences_lang2)

        # Calculate similarity matrix
        similarity_matrix = np.dot(emb1, emb2.T)

        alignments = []
        for i in range(len(sentences_lang1)):
            for j in range(len(sentences_lang2)):
                sim = similarity_matrix[i, j]
                if sim >= threshold:
                    alignments.append((i, j, float(sim)))

        # Sort by similarity
        alignments.sort(key=lambda x: x[2], reverse=True)

        return alignments

    def save(self, output_dir: str):
        """Save model and tokenizer."""
        if not self.model or not self.tokenizer:
            raise ValueError("No model to save")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        # Save config
        with open(output_path / "config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

        logger.info(f"Model saved to {output_dir}")

    @classmethod
    def from_pretrained(cls, model_path: str, **kwargs):
        """Load pretrained model."""
        return cls(model_path=model_path, tokenizer_path=model_path, **kwargs)
