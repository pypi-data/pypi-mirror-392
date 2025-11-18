"""
Wikipedia Language Model Module

Provides utilities for loading and using Wikipedia-trained language models.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoModelForMaskedLM,
    AutoTokenizer,
    pipeline,
)

logger = logging.getLogger(__name__)


class WikipediaLanguageModel:
    """
    Wikipedia-trained language model for Bangla/bilingual text.

    Supports both Masked Language Models (MLM) and Causal Language Models (CLM).
    """

    def __init__(
        self,
        model_path: Union[str, Path],
        device: Optional[str] = None,
        model_type: Optional[str] = None,
    ):
        """
        Initialize Wikipedia Language Model.

        Args:
            model_path: Path to trained model or HuggingFace model name
            device: Device to use ('cuda', 'cpu', or None for auto)
            model_type: Model type ('mlm' or 'clm', or None for auto-detect)
        """
        self.model_path = Path(model_path) if isinstance(model_path, str) else model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_type = model_type

        self.tokenizer = None
        self.model = None

        self._load_model()

    def _load_model(self) -> None:
        """Load model and tokenizer."""
        logger.info(f"Loading Wikipedia LM from {self.model_path}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

        # Load model
        if self.model_type == "mlm":
            self.model = AutoModelForMaskedLM.from_pretrained(self.model_path)
        elif self.model_type == "clm":
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
        else:
            # Auto-detect
            try:
                self.model = AutoModelForMaskedLM.from_pretrained(self.model_path)
                self.model_type = "mlm"
            except Exception:
                self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
                self.model_type = "clm"

        self.model.to(self.device)
        self.model.eval()

        logger.info(f"Model loaded: {self.model_type} on {self.device}")

    def fill_mask(self, text: str, top_k: int = 5) -> List[Dict]:
        """
        Fill masked tokens in text (MLM only).

        Args:
            text: Text with [MASK] tokens
            top_k: Number of top predictions to return

        Returns:
            List of predictions with 'sequence', 'token', 'score'

        Example:
            >>> model.fill_mask("আমি [MASK] খাই", top_k=3)
            [
                {'sequence': 'আমি ভাত খাই', 'token': 'ভাত', 'score': 0.85},
                {'sequence': 'আমি রুটি খাই', 'token': 'রুটি', 'score': 0.10},
                ...
            ]
        """
        if self.model_type != "mlm":
            raise ValueError("fill_mask only works with MLM models")

        fill_mask_pipeline = pipeline(
            "fill-mask",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
        )

        results = fill_mask_pipeline(text, top_k=top_k)
        return results

    def generate_text(
        self,
        prompt: str,
        max_length: int = 100,
        num_return_sequences: int = 1,
        temperature: float = 0.8,
        top_k: int = 50,
        top_p: float = 0.95,
    ) -> List[str]:
        """
        Generate text from prompt (CLM only).

        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            num_return_sequences: Number of sequences to generate
            temperature: Sampling temperature
            top_k: Top-k sampling
            top_p: Nucleus sampling

        Returns:
            List of generated texts

        Example:
            >>> model.generate_text("আমি বাংলায়", max_length=50)
            ['আমি বাংলায় কথা বলি এবং লিখি...']
        """
        if self.model_type != "clm":
            raise ValueError("generate_text only works with CLM models")

        text_gen_pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
        )

        results = text_gen_pipeline(
            prompt,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
        )

        return [r["generated_text"] for r in results]

    def get_embeddings(self, texts: Union[str, List[str]]) -> torch.Tensor:
        """
        Get contextualized embeddings for text(s).

        Args:
            texts: Single text or list of texts

        Returns:
            Tensor of embeddings (batch_size, seq_len, hidden_size)

        Example:
            >>> embeddings = model.get_embeddings("আমি বাংলায় কথা বলি")
            >>> embeddings.shape
            torch.Size([1, 10, 768])
        """
        if isinstance(texts, str):
            texts = [texts]

        # Tokenize
        encodings = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        input_ids = encodings["input_ids"].to(self.device)
        attention_mask = encodings["attention_mask"].to(self.device)

        # Get embeddings
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
            )

            # Use last hidden state
            embeddings = outputs.hidden_states[-1]

        return embeddings

    def get_sentence_embedding(self, text: str, pooling: str = "mean") -> torch.Tensor:
        """
        Get sentence-level embedding.

        Args:
            text: Input text
            pooling: Pooling strategy ('mean', 'max', 'cls')

        Returns:
            Sentence embedding tensor (hidden_size,)

        Example:
            >>> embedding = model.get_sentence_embedding("আমি বাংলায় কথা বলি")
            >>> embedding.shape
            torch.Size([768])
        """
        embeddings = self.get_embeddings(text)  # (1, seq_len, hidden_size)

        if pooling == "mean":
            # Mean pooling
            sentence_embedding = embeddings.mean(dim=1).squeeze(0)
        elif pooling == "max":
            # Max pooling
            sentence_embedding = embeddings.max(dim=1).values.squeeze(0)
        elif pooling == "cls":
            # CLS token (first token)
            sentence_embedding = embeddings[:, 0, :].squeeze(0)
        else:
            raise ValueError(f"Invalid pooling strategy: {pooling}")

        return sentence_embedding

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score (0-1)

        Example:
            >>> similarity = model.compute_similarity("আমি ভাত খাই", "আমি খাবার খাই")
            >>> print(f"Similarity: {similarity:.4f}")
            Similarity: 0.8532
        """
        # Get sentence embeddings
        emb1 = self.get_sentence_embedding(text1)
        emb2 = self.get_sentence_embedding(text2)

        # Compute cosine similarity
        similarity = torch.nn.functional.cosine_similarity(
            emb1.unsqueeze(0),
            emb2.unsqueeze(0),
        ).item()

        return similarity

    def predict_next_word(self, text: str, top_k: int = 5) -> List[Dict]:
        """
        Predict next word(s) given context.

        Args:
            text: Input context
            top_k: Number of top predictions

        Returns:
            List of predictions with 'word' and 'score'

        Example:
            >>> predictions = model.predict_next_word("আমি ভাত", top_k=3)
            [{'word': 'খাই', 'score': 0.85}, ...]
        """
        if self.model_type == "mlm":
            # For MLM, append [MASK] and predict
            masked_text = text + " [MASK]"
            results = self.fill_mask(masked_text, top_k=top_k)

            predictions = []
            for result in results:
                # Extract the predicted token
                predicted_token = result["token_str"].strip()
                predictions.append(
                    {
                        "word": predicted_token,
                        "score": result["score"],
                    }
                )

            return predictions

        else:
            # For CLM, generate and extract next token
            # This is a simplified version
            generated = self.generate_text(
                text,
                max_length=len(text.split()) + 2,
                num_return_sequences=top_k,
            )

            predictions = []
            for gen_text in generated:
                # Extract next word
                words = gen_text[len(text) :].strip().split()
                if words:
                    predictions.append(
                        {
                            "word": words[0],
                            "score": 1.0 / (len(predictions) + 1),  # Placeholder score
                        }
                    )

            return predictions


def load_model(model_path: Union[str, Path], **kwargs) -> WikipediaLanguageModel:
    """
    Load Wikipedia language model.

    Args:
        model_path: Path to model or HuggingFace model name
        **kwargs: Additional arguments for WikipediaLanguageModel

    Returns:
        Loaded model instance

    Example:
        >>> from bilingual.modules.wikipedia_lm import load_model
        >>> model = load_model("models/wikipedia/base")
        >>> result = model.fill_mask("আমি [MASK] খাই")
    """
    return WikipediaLanguageModel(model_path, **kwargs)


# Convenience functions
def fill_mask(model_path: Union[str, Path], text: str, top_k: int = 5) -> List[Dict]:
    """Convenience function to fill masked text."""
    model = load_model(model_path)
    return model.fill_mask(text, top_k)


def generate_text(model_path: Union[str, Path], prompt: str, **kwargs) -> List[str]:
    """Convenience function to generate text."""
    model = load_model(model_path)
    return model.generate_text(prompt, **kwargs)


def get_embeddings(model_path: Union[str, Path], texts: Union[str, List[str]]) -> torch.Tensor:
    """Convenience function to get embeddings."""
    model = load_model(model_path)
    return model.get_embeddings(texts)


def compute_similarity(model_path: Union[str, Path], text1: str, text2: str) -> float:
    """Convenience function to compute similarity."""
    model = load_model(model_path)
    return model.compute_similarity(text1, text2)
