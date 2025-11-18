"""
Literary Language Model for Bangla literature generation and analysis.
Fine-tuned on poetry, novels, and literary texts.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import torch
import torch.nn as nn
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    PreTrainedTokenizerFast,
    Trainer,
    TrainingArguments,
)

logger = logging.getLogger(__name__)


class LiteraryLanguageModel:
    """
    Fine-tuned language model for Bangla literary text generation.
    Specialized for poetry, novels, and literary analysis.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the Literary Language Model.

        Args:
            model_path: Path to pretrained model weights
            tokenizer_path: Path to tokenizer
            config_path: Path to model config
            device: Device to run model on (cuda/cpu)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if config_path:
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
            self.config = GPT2Config(**config_dict)
        else:
            self.config = GPT2Config(
                vocab_size=32000,
                n_positions=1024,
                n_ctx=1024,
                n_embd=768,
                n_layer=12,
                n_head=12,
            )

        if model_path and Path(model_path).exists():
            self.model = GPT2LMHeadModel.from_pretrained(model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self.model = GPT2LMHeadModel(self.config)
            logger.info("Initialized new model from config")

        self.model.to(self.device)
        self.model.eval()

        if tokenizer_path:
            self.tokenizer = PreTrainedTokenizerFast.from_pretrained(tokenizer_path)
        else:
            self.tokenizer = None
            logger.warning("No tokenizer provided")

    def generate(
        self,
        prompt: str,
        max_length: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.9,
        top_k: int = 50,
        num_return_sequences: int = 1,
        do_sample: bool = True,
        repetition_penalty: float = 1.2,
    ) -> List[str]:
        """
        Generate literary text from a prompt.

        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            num_return_sequences: Number of sequences to generate
            do_sample: Whether to use sampling
            repetition_penalty: Penalty for repetition

        Returns:
            List of generated texts
        """
        if not self.tokenizer:
            raise ValueError("Tokenizer not initialized")

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
                top_k=top_k,
                num_return_sequences=num_return_sequences,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated_texts = [
            self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs
        ]

        return generated_texts

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
            meter_type: Type of meter (অক্ষরবৃত্ত, মাত্রাবৃত্ত, etc.)
            max_length: Maximum length
            temperature: Sampling temperature

        Returns:
            Generated poetry
        """
        if meter_type:
            prompt = f"[{meter_type}] {prompt}"

        generated = self.generate(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_p=0.85,
            repetition_penalty=1.3,
        )

        return generated[0]

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
        generated = self.generate(
            prompt=text,
            max_length=len(self.tokenizer.encode(text)) + max_new_tokens,
            temperature=temperature,
            num_return_sequences=1,
        )

        return generated[0]

    def get_perplexity(self, text: str) -> float:
        """
        Calculate perplexity of text (lower is better for literary quality).

        Args:
            text: Input text

        Returns:
            Perplexity score
        """
        if not self.tokenizer:
            raise ValueError("Tokenizer not initialized")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss

        perplexity = torch.exp(loss).item()
        return perplexity

    def save(self, output_dir: str):
        """Save model and tokenizer."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.model.save_pretrained(output_dir)
        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)

        logger.info(f"Model saved to {output_dir}")

    @classmethod
    def from_pretrained(cls, model_path: str, tokenizer_path: Optional[str] = None):
        """Load pretrained model."""
        return cls(
            model_path=model_path,
            tokenizer_path=tokenizer_path or model_path,
        )
