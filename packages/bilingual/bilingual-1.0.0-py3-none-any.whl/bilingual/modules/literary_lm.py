"""
Literary Language Model for Bangla text generation.

This module provides a fine-tuned language model specifically designed
for generating and working with Bangla literary text. It wraps the full
implementation from bilingual.models.literary_lm.
"""

from typing import Optional

try:
    from bilingual.models.literary_lm import LiteraryLanguageModel as _LiteraryLanguageModel

    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False
    _LiteraryLanguageModel = None


class LiteraryLM:
    """
    Fine-tuned Language Model for Bangla literary text.

    This is a wrapper around the full LiteraryLanguageModel implementation
    that provides a simplified interface for common use cases.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the Literary Language Model.

        Args:
            model_path: Path to the pre-trained model checkpoint
            tokenizer_path: Path to the tokenizer (defaults to model_path)
            device: Device to run on ('cuda' or 'cpu', auto-detected if None)
        """
        if not HAS_MODELS:
            raise ImportError(
                "LiteraryLanguageModel not available. "
                "Make sure bilingual.models is properly installed."
            )

        self.model_path = model_path
        self.tokenizer_path = tokenizer_path or model_path
        self.device = device
        self._model = None

    def load_model(self):
        """Load the literary LM from the specified path."""
        if self._model is not None:
            return  # Already loaded

        self._model = _LiteraryLanguageModel(
            model_path=self.model_path,
            tokenizer_path=self.tokenizer_path,
            device=self.device,
        )

    @property
    def model(self):
        """Get the underlying model, loading it if necessary."""
        if self._model is None:
            self.load_model()
        return self._model

    def generate_text(
        self,
        prompt: str,
        max_length: int = 512,
        temperature: float = 0.8,
        num_return_sequences: int = 1,
    ) -> str:
        """
        Generate literary text based on the given prompt.

        Args:
            prompt: Input text prompt for generation
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more creative)
            num_return_sequences: Number of sequences to generate

        Returns:
            Generated literary text (first sequence if multiple)
        """
        results = self.model.generate(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            num_return_sequences=num_return_sequences,
        )
        return results[0] if results else ""

    def generate_poetry(
        self,
        prompt: str,
        meter_type: Optional[str] = None,
        max_length: int = 256,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate poetry with optional meter specification.

        Args:
            prompt: Poetry prompt
            meter_type: Type of meter (অক্ষরবৃত্ত, মাত্রাবৃত্ত, স্বরবৃত্ত, etc.)
            max_length: Maximum length
            temperature: Sampling temperature

        Returns:
            Generated poetry
        """
        return self.model.generate_poetry(
            prompt=prompt,
            meter_type=meter_type,
            max_length=max_length,
            temperature=temperature,
        )

    def complete_text(
        self,
        text: str,
        max_new_tokens: int = 100,
        temperature: float = 0.8,
    ) -> str:
        """
        Complete a literary text passage.

        Args:
            text: Incomplete text
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature

        Returns:
            Completed text
        """
        return self.model.complete_text(
            text=text,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )

    def get_perplexity(self, text: str) -> float:
        """
        Calculate perplexity of text (lower is better).

        Args:
            text: Input text

        Returns:
            Perplexity score
        """
        return self.model.get_perplexity(text)

    def fine_tune(
        self,
        dataset_path: str,
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 5e-5,
    ):
        """
        Fine-tune the model on a literary dataset.

        Args:
            dataset_path: Path to the training dataset
            output_dir: Directory to save the fine-tuned model
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate

        Note:
            This is a simplified interface. For advanced training,
            use the train_literary_lm.py script directly.
        """
        # This would require implementing a training loop
        # For now, users should use the training script
        raise NotImplementedError(
            "Fine-tuning through this interface is not yet implemented. "
            "Please use scripts/train_literary_lm.py for training."
        )

    def save(self, output_dir: str):
        """
        Save the model and tokenizer.

        Args:
            output_dir: Directory to save to
        """
        self.model.save(output_dir)

    @classmethod
    def from_pretrained(cls, model_path: str, tokenizer_path: Optional[str] = None):
        """
        Load a pretrained literary LM.

        Args:
            model_path: Path to the model
            tokenizer_path: Path to tokenizer (defaults to model_path)

        Returns:
            Loaded LiteraryLM instance
        """
        instance = cls(model_path=model_path, tokenizer_path=tokenizer_path)
        instance.load_model()
        return instance
