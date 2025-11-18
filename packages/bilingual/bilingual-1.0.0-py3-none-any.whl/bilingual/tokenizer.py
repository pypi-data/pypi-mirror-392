"""
Tokenization utilities using SentencePiece for Bangla and English.

Provides a unified tokenizer that handles both languages efficiently.
"""

import os
from pathlib import Path
from typing import List, Optional, Union, cast

try:
    import sentencepiece as spm

    SENTENCEPIECE_AVAILABLE = True
except ImportError:
    SENTENCEPIECE_AVAILABLE = False
    spm = None


class BilingualTokenizer:
    """
    Bilingual tokenizer for Bangla and English using SentencePiece.

    This tokenizer uses a shared vocabulary optimized for both Bangla and English,
    ensuring efficient representation of both scripts.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the tokenizer.

        Args:
            model_path: Path to the SentencePiece model file (.model)
        """
        if not SENTENCEPIECE_AVAILABLE:
            raise ImportError(
                "sentencepiece is required for tokenization. "
                "Install it with: pip install sentencepiece"
            )

        self.model_path = model_path
        self.sp = None

        if model_path and os.path.exists(model_path):
            self.load(model_path)

    def load(self, model_path: str) -> None:
        """
        Load a SentencePiece model.

        Args:
            model_path: Path to the .model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        if spm is None:
            raise ImportError("sentencepiece is not available")

        sp_processor = spm.SentencePieceProcessor()
        sp_processor.load(model_path)
        self.sp = sp_processor
        self.model_path = model_path

    def encode(
        self,
        text: Union[str, List[str]],
        add_bos: bool = False,
        add_eos: bool = False,
        as_ids: bool = True,
    ) -> Union[List[int], List[str], List[List[int]], List[List[str]]]:
        """
        Encode text into tokens or token IDs.

        Args:
            text: Input text or list of texts
            add_bos: Whether to add beginning-of-sequence token
            add_eos: Whether to add end-of-sequence token
            as_ids: If True, return token IDs; otherwise return token strings

        Returns:
            Encoded tokens or token IDs
        """
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded. Call load() first.")

        is_batched = isinstance(text, list)
        texts = text if is_batched else [text]

        results = []
        for t in texts:
            if as_ids:
                encoded = self.sp.encode(t, add_bos=add_bos, add_eos=add_eos)
            else:
                encoded = self.sp.encode(t, out_type=str, add_bos=add_bos, add_eos=add_eos)
            results.append(encoded)

        return results if is_batched else results[0]

    def decode(
        self,
        tokens: Union[List[int], List[List[int]]],
    ) -> Union[str, List[str]]:
        """
        Decode token IDs back to text.

        Args:
            tokens: Token IDs or list of token ID sequences

        Returns:
            Decoded text or list of texts
        """
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded. Call load() first.")

        is_batched = isinstance(tokens[0], list) if tokens else False
        token_seqs = tokens if is_batched else [tokens]

        results = [self.sp.decode(seq) for seq in token_seqs]

        return results if is_batched else results[0]

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into token strings.

        Args:
            text: Input text

        Returns:
            List of token strings
        """
        result = self.encode(text, as_ids=False)
        # Return List[str] by casting the result
        return cast(List[str], result)

    def get_vocab_size(self) -> int:
        """Get the vocabulary size."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.get_piece_size()

    def id_to_piece(self, token_id: int) -> str:
        """Convert a token ID to its string representation."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.id_to_piece(token_id)

    def piece_to_id(self, piece: str) -> int:
        """Convert a token string to its ID."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.piece_to_id(piece)

    @property
    def vocab_size(self) -> int:
        """Vocabulary size property."""
        return self.get_vocab_size()

    @property
    def bos_id(self) -> int:
        """Beginning-of-sequence token ID."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.bos_id()

    @property
    def eos_id(self) -> int:
        """End-of-sequence token ID."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.eos_id()

    @property
    def pad_id(self) -> int:
        """Padding token ID."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.pad_id()

    @property
    def unk_id(self) -> int:
        """Unknown token ID."""
        if self.sp is None:
            raise RuntimeError("Tokenizer model not loaded.")
        return self.sp.unk_id()


def load_tokenizer(model_name_or_path: str) -> BilingualTokenizer:
    """
    Load a bilingual tokenizer.

    Args:
        model_name_or_path: Name of a pretrained model or path to a .model file

    Returns:
        Loaded BilingualTokenizer instance

    Examples:
        >>> tokenizer = load_tokenizer("bilingual-tokenizer.model")
        >>> tokens = tokenizer.encode("আমি বই পড়ি।")
    """
    # Check if it's a path to a model file
    if os.path.exists(model_name_or_path):
        return BilingualTokenizer(model_name_or_path)

    # Check in package data directory
    package_dir = Path(__file__).parent
    model_dir = package_dir / "models"
    model_path = model_dir / f"{model_name_or_path}.model"

    if model_path.exists():
        return BilingualTokenizer(str(model_path))

    # Model not found
    raise FileNotFoundError(
        f"Tokenizer model '{model_name_or_path}' not found. "
        f"Checked: {model_name_or_path}, {model_path}"
    )


def train_tokenizer(
    input_files: List[str],
    model_prefix: str,
    vocab_size: int = 32000,
    model_type: str = "bpe",
    character_coverage: float = 0.9995,
    user_defined_symbols: Optional[List[str]] = None,
    **kwargs,
) -> None:
    """
    Train a SentencePiece tokenizer on bilingual data.

    Args:
        input_files: List of input text files
        model_prefix: Prefix for output model files
        vocab_size: Vocabulary size
        model_type: Model type ('bpe', 'unigram', 'char', 'word')
        character_coverage: Character coverage (0.9995 recommended for Bangla+English)
        user_defined_symbols: Additional symbols to include
        **kwargs: Additional arguments for SentencePiece trainer

    Examples:
        >>> train_tokenizer(
        ...     input_files=["corpus_bn.txt", "corpus_en.txt"],
        ...     model_prefix="bilingual_sp",
        ...     vocab_size=32000,
        ...     model_type="bpe"
        ... )
    """
    if not SENTENCEPIECE_AVAILABLE:
        raise ImportError(
            "sentencepiece is required for training. " "Install it with: pip install sentencepiece"
        )

    # Prepare training arguments
    train_args = {
        "input": ",".join(input_files),
        "model_prefix": model_prefix,
        "vocab_size": vocab_size,
        "model_type": model_type,
        "character_coverage": character_coverage,
        "pad_id": 0,
        "unk_id": 1,
        "bos_id": 2,
        "eos_id": 3,
    }

    if user_defined_symbols:
        train_args["user_defined_symbols"] = ",".join(user_defined_symbols)

    # Add any additional arguments
    train_args.update(kwargs)

    # Train the model
    spm.SentencePieceTrainer.train(**train_args)

    print(f"Tokenizer trained successfully: {model_prefix}.model")
