"""
Style Transfer using GPT-based models.

This module provides functionality to convert text between different styles
such as formal, informal, and poetic in Bangla using sequence-to-sequence
models or prompt-based generation.
"""

import logging
from typing import Dict, List, Optional

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        GenerationConfig,
    )

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None
    AutoModelForCausalLM = None
    GenerationConfig = None

logger = logging.getLogger(__name__)


class StyleTransferGPT:
    """
    Convert text between formal, informal, poetic styles using GPT-based models.

    Supports both:
    1. Fine-tuned seq2seq models (e.g., mT5, mBART)
    2. Prompt-based generation with causal LMs (e.g., GPT-2, GPT-J)
    """

    # Style markers for prompt-based generation
    STYLE_MARKERS = {
        "formal": "আনুষ্ঠানিক",
        "informal": "অনানুষ্ঠানিক",
        "poetic": "কাব্যিক",
        "colloquial": "কথ্য",
        "literary": "সাহিত্যিক",
    }

    # List of supported styles
    STYLES = list(STYLE_MARKERS.keys())

    def __init__(
        self,
        model_path: Optional[str] = None,
        model_type: str = "seq2seq",
        device: Optional[str] = None,
    ):
        """
        Initialize the Style Transfer model.

        Args:
            model_path: Path to the pre-trained model (or HuggingFace model ID)
            model_type: Type of model ('seq2seq' or 'causal')
            device: Device to run on ('cuda' or 'cpu', auto-detected if None)
        """
        if not HAS_TRANSFORMERS:
            raise ImportError(
                "transformers and torch are required for StyleTransferGPT. "
                "Install with: pip install transformers torch"
            )

        self.model_path = model_path
        self.model_type = model_type
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model = None
        self._tokenizer = None

    def load_model(self):
        """Load the style transfer model."""
        if self._model is not None:
            return  # Already loaded

        if not self.model_path:
            # Use a default model for demonstration
            logger.warning("No model path provided, using default model")
            if self.model_type == "seq2seq":
                self.model_path = "google/mt5-small"  # Multilingual T5
            else:
                self.model_path = "gpt2"  # For demonstration

        logger.info(f"Loading {self.model_type} model from {self.model_path}")

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)

            if self.model_type == "seq2seq":
                self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
            else:
                self._model = AutoModelForCausalLM.from_pretrained(self.model_path)

            self._model.to(self.device)
            self._model.eval()

            logger.info(f"Model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    @property
    def model(self):
        """Get the underlying model, loading it if necessary."""
        if self._model is None:
            self.load_model()
        return self._model

    @property
    def tokenizer(self):
        """Get the tokenizer, loading it if necessary."""
        if self._tokenizer is None:
            self.load_model()
        return self._tokenizer

    def convert(
        self,
        text: str,
        target_style: str,
        source_style: Optional[str] = None,
        max_length: int = 512,
        temperature: float = 0.7,
        num_beams: int = 4,
    ) -> str:
        """
        Convert text to the target style.

        Args:
            text: Input text to convert
            target_style: Target style (e.g., 'formal', 'informal', 'poetic')
            source_style: Source style (optional, for explicit conversion)
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            num_beams: Number of beams for beam search

        Returns:
            Text converted to the target style
        """
        if target_style not in self.available_styles():
            logger.warning(f"Unknown style '{target_style}', proceeding anyway")

        if self.model_type == "seq2seq":
            return self._convert_seq2seq(text, target_style, source_style, max_length, num_beams)
        else:
            return self._convert_causal(text, target_style, source_style, max_length, temperature)

    def batch_convert(
        self,
        texts: List[str],
        target_style: str,
        source_style: Optional[str] = None,
        max_length: int = 512,
        temperature: float = 0.7,
        num_beams: int = 4,
    ) -> List[str]:
        """
        Convert a batch of texts to the target style.

        Args:
            texts: List of input texts to convert
            target_style: Target style (e.g., 'formal', 'informal', 'poetic')
            source_style: Source style (optional, for explicit conversion)
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            num_beams: Number of beams for beam search

        Returns:
            List of texts converted to the target style
        """
        if not texts:
            return []

        if target_style not in self.available_styles():
            logger.warning(f"Unknown style '{target_style}', proceeding anyway")

        if self.model_type == "seq2seq":
            return [
                self._convert_seq2seq(text, target_style, source_style, max_length, num_beams)
                for text in texts
            ]
        else:
            return [
                self._convert_causal(text, target_style, source_style, max_length, temperature)
                for text in texts
            ]

    def _convert_seq2seq(
        self,
        text: str,
        target_style: str,
        source_style: Optional[str],
        max_length: int,
        num_beams: int,
    ) -> str:
        """Convert using seq2seq model."""
        # Format input with style markers
        if source_style:
            input_text = f"convert from {source_style} to {target_style}: {text}"
        else:
            input_text = f"convert to {target_style}: {text}"

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )

        converted = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return converted

    def _convert_causal(
        self,
        text: str,
        target_style: str,
        source_style: Optional[str],
        max_length: int,
        temperature: float,
    ) -> str:
        """Convert using causal LM with prompting."""
        # Create a prompt for style transfer
        style_marker = self.STYLE_MARKERS.get(target_style, target_style)

        if source_style:
            source_marker = self.STYLE_MARKERS.get(source_style, source_style)
            prompt = f"{source_marker} ভাষা: {text}\n" f"{style_marker} ভাষা:"
        else:
            prompt = f"নিচের বাক্যটি {style_marker} ভাষায় লিখুন:\n" f"মূল: {text}\n" f"{style_marker}:"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the converted part (after the prompt)
        if style_marker in generated:
            parts = generated.split(style_marker + ":")
            if len(parts) > 1:
                return parts[-1].strip()

        return generated



    def available_styles(self) -> List[str]:
        """
        Get list of available styles.

        Returns:
            List of supported style names
        """
        return list(self.STYLE_MARKERS.keys())

    def get_style_info(self) -> Dict[str, str]:
        """
        Get information about available styles.

        Returns:
            Dictionary mapping style names to Bangla descriptions
        """
        return self.STYLE_MARKERS.copy()

    def save(self, save_directory: str):
        """
        Save the model and tokenizer to a directory.

        Args:
            save_directory: Directory to save the model and tokenizer
        """
        if self._model is None or self._tokenizer is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        self._model.save_pretrained(save_directory)
        self._tokenizer.save_pretrained(save_directory)
        logger.info(f"Model saved to {save_directory}")
