"""
Style transfer model for converting text between formal, informal, and poetic styles.

This module provides both rule-based and GPT-based neural style transfer.
Supports formal ↔ informal ↔ poetic style conversion for Bangla text.
"""

import logging
from pathlib import Path
from typing import Dict, List, Literal, Optional

# Optional ML imports - only needed for StyleTransferGPT class
try:
    import torch
    from transformers import GPT2LMHeadModel, PreTrainedTokenizerFast

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)


StyleType = Literal["formal", "informal", "poetic"]
ModelType = Literal["transformer", "gan", "rule_based"]


class StyleTransferModel:
    """
    Style transfer model for bilingual text.

    Currently implements rule-based transformations as a baseline.
    Designed to be extended with neural models (transformers, GANs).

    Attributes:
        model_type: Type of underlying model ('transformer', 'gan', 'rule_based')
        loaded: Whether model weights are loaded
    """

    def __init__(self, model_type: ModelType = "rule_based"):
        """
        Initialize the style transfer model.

        Args:
            model_type: Model architecture to use
        """
        self.model_type = model_type
        self.loaded = False
        self._rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Dict[str, str]]:
        """
        Initialize rule-based transformation dictionaries.

        Returns:
            Nested dict mapping style -> (pattern -> replacement)
        """
        return {
            "formal": {
                # English
                "don't": "do not",
                "can't": "cannot",
                "won't": "will not",
                "it's": "it is",
                "I'm": "I am",
                # Bengali
                "আমি": "আমরা",  # Informal -> formal plural
                "তুমি": "আপনি",  # You (informal) -> You (formal)
            },
            "informal": {
                # English
                "do not": "don't",
                "cannot": "can't",
                "will not": "won't",
                "it is": "it's",
                "I am": "I'm",
                # Bengali
                "আপনি": "তুমি",
            },
            "poetic": {
                # Add poetic flourishes (simplified)
                "the": "the gentle",
                "night": "moonlit night",
                "day": "bright day",
                "রাত": "চাঁদনী রাত",
                "দিন": "সোনালী দিন",
            },
        }

    def load(self, model_path: Optional[str] = None) -> None:
        """
        Load model weights from disk.

        For rule-based models, this is a no-op. For neural models,
        this would load checkpoint files.

        Args:
            model_path: Path to model checkpoint (optional)
        """
        if self.model_type == "rule_based":
            self.loaded = True
            return

        # Placeholder for future neural model loading
        if model_path:
            # TODO: Load transformer/GAN weights
            pass

        self.loaded = True

    def convert(
        self, text: str, target_style: StyleType = "formal", preserve_meaning: bool = True
    ) -> str:
        """
        Convert text to target style.

        Args:
            text: Input text to transform
            target_style: Desired output style ('formal', 'informal', 'poetic')
            preserve_meaning: Whether to preserve semantic meaning (default True)

        Returns:
            Transformed text in target style

        Examples:
            >>> model = StyleTransferModel()
            >>> model.load()
            >>> model.convert("I can't do this", target_style='formal')
            "I cannot do this"
        """
        if not self.loaded:
            self.load()

        if self.model_type == "rule_based":
            return self._rule_based_convert(text, target_style)

        # Placeholder for neural model inference
        # TODO: Implement transformer/GAN forward pass
        return text

    def _rule_based_convert(self, text: str, target_style: StyleType) -> str:
        """
        Apply rule-based transformations for style transfer.

        Args:
            text: Input text
            target_style: Target style

        Returns:
            Transformed text
        """
        result = text

        if target_style not in self._rules:
            return result

        # Apply substitution rules
        for pattern, replacement in self._rules[target_style].items():
            # Case-sensitive replacement for now
            result = result.replace(pattern, replacement)

        return result

    def batch_convert(self, texts: list[str], target_style: StyleType = "formal") -> list[str]:
        """
        Convert multiple texts in batch.

        Args:
            texts: List of input texts
            target_style: Desired output style

        Returns:
            List of transformed texts
        """
        return [self.convert(text, target_style) for text in texts]

    def available_styles(self) -> list[str]:
        """
        Get list of supported target styles.

        Returns:
            List of style names
        """
        return ["formal", "informal", "poetic"]

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"StyleTransferModel(model_type='{self.model_type}', loaded={self.loaded})"


class StyleTransferGPT:
    """
    GPT-based style transfer model for Bangla text.
    Converts between formal, informal, poetic, and literary styles.

    Requires torch and transformers to be installed:
        pip install torch transformers
    """

    STYLE_TOKENS = {
        "formal": "<|formal|>",
        "informal": "<|informal|>",
        "poetic": "<|poetic|>",
        "literary": "<|literary|>",
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize Style Transfer GPT model.

        Args:
            model_path: Path to pretrained model
            tokenizer_path: Path to tokenizer
            config_path: Path to config
            device: Device to run on

        Raises:
            ImportError: If torch or transformers not installed
        """
        if not _TORCH_AVAILABLE:
            raise ImportError(
                "StyleTransferGPT requires torch and transformers. "
                "Install with: pip install torch transformers"
            )

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if model_path and Path(model_path).exists():
            self.model = GPT2LMHeadModel.from_pretrained(model_path)
            self.tokenizer = PreTrainedTokenizerFast.from_pretrained(tokenizer_path or model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = None
            self.tokenizer = None
            logger.warning("No pretrained model found")

        if self.model:
            self.model.to(self.device)
            self.model.eval()

        # Add style tokens to tokenizer if not present
        if self.tokenizer:
            special_tokens = list(self.STYLE_TOKENS.values())
            self.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})
            if self.model:
                self.model.resize_token_embeddings(len(self.tokenizer))

    def transfer(
        self,
        text: str,
        source_style: str,
        target_style: str,
        max_length: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.85,
    ) -> str:
        """
        Transfer text from source style to target style.

        Args:
            text: Input text
            source_style: Source style (formal/informal/poetic/literary)
            target_style: Target style
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            Transferred text
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")

        # Format prompt with style tokens
        source_token = self.STYLE_TOKENS.get(source_style, "")
        target_token = self.STYLE_TOKENS.get(target_style, "")

        prompt = f"{source_token} {text} {target_token}"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove source text and style tokens from output
        generated_text = generated_text.replace(text, "").strip()
        for token in self.STYLE_TOKENS.values():
            generated_text = generated_text.replace(token, "").strip()

        return generated_text

    def formal_to_informal(self, text: str) -> str:
        """Convert formal text to informal style."""
        return self.transfer(text, "formal", "informal")

    def informal_to_formal(self, text: str) -> str:
        """Convert informal text to formal style."""
        return self.transfer(text, "informal", "formal")

    def to_poetic(self, text: str, source_style: str = "formal") -> str:
        """Convert text to poetic style."""
        return self.transfer(text, source_style, "poetic")

    def to_literary(self, text: str, source_style: str = "formal") -> str:
        """Convert text to literary style."""
        return self.transfer(text, source_style, "literary")

    def batch_transfer(
        self,
        texts: List[str],
        source_style: str,
        target_style: str,
    ) -> List[str]:
        """
        Transfer multiple texts in batch.

        Args:
            texts: List of input texts
            source_style: Source style
            target_style: Target style

        Returns:
            List of transferred texts
        """
        return [self.transfer(text, source_style, target_style) for text in texts]

    def save(self, output_dir: str):
        """Save model and tokenizer."""
        if not self.model or not self.tokenizer:
            raise ValueError("No model to save")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        logger.info(f"Model saved to {output_dir}")

    @classmethod
    def from_pretrained(cls, model_path: str):
        """Load pretrained model."""
        return cls(model_path=model_path, tokenizer_path=model_path)
