"""
Text processing utilities for Bangla-English parallel corpus.
"""

import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import sentencepiece as spm
from tqdm import tqdm


class TextProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.sp_model_prefix = "bilingual_sp"
        self.vocab_size = config.get("vocab_size", 32000)
        self.max_seq_length = config.get("max_seq_length", 128)
        self.sp_model = None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not isinstance(text, str):
            return ""

        # Normalize unicode
        text = unicodedata.normalize("NFKC", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        # Add space around punctuation
        text = re.sub(r"([.,!?()])", r" \1 ", text)

        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def create_vocab(self, data_files: List[str], output_dir: Path):
        """Create vocabulary using SentencePiece."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare training file for SentencePiece
        train_file = output_dir / "spm_train.txt"
        with open(train_file, "w", encoding="utf-8") as f:
            for file in data_files:
                df = pd.read_parquet(file)
                for col in ["en", "bn"]:
                    if col in df.columns:
                        for text in df[col].dropna():
                            f.write(f"{self.clean_text(text)}\n")

        # Train SentencePiece model
        spm.SentencePieceTrainer.train(
            input=str(train_file),
            model_prefix=str(output_dir / self.sp_model_prefix),
            vocab_size=self.vocab_size,
            model_type="bpe",
            character_coverage=1.0,
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
            pad_piece="[PAD]",
            unk_piece="[UNK]",
            bos_piece="[BOS]",
            eos_piece="[EOS]",
            user_defined_symbols=["[SEP]", "[CLS]", "[MASK]"],
        )

        # Load the trained model
        self.sp_model = spm.SentencePieceProcessor()
        self.sp_model.load(str(output_dir / f"{self.sp_model_prefix}.model"))

        return self.sp_model

    def tokenize(self, text: str, lang: str = None) -> List[int]:
        """Tokenize text using the trained SentencePiece model."""
        if self.sp_model is None:
            raise ValueError("SentencePiece model not loaded. Call create_vocab first.")

        # Add language-specific tokens if needed
        if lang == "en":
            text = f"[EN] {text}"
        elif lang == "bn":
            text = f"[BN] {text}"

        return self.sp_model.encode_as_ids(text)

    def process_dataset(self, input_file: Path, output_file: Path) -> Tuple[Dict, Dict]:
        """Process a dataset file and save the tokenized version."""
        df = pd.read_parquet(input_file)

        # Initialize stats
        stats = {"total_examples": len(df), "en_tokens": [], "bn_tokens": [], "skipped_examples": 0}

        processed_data = []

        for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {input_file.name}"):
            try:
                en_text = self.clean_text(row.get("translation.en", row.get("en", "")))
                bn_text = self.clean_text(row.get("translation.bn", row.get("bn", "")))

                if not en_text or not bn_text:
                    stats["skipped_examples"] += 1
                    continue

                # Tokenize
                en_ids = self.tokenize(en_text, "en")
                bn_ids = self.tokenize(bn_text, "bn")

                # Update stats
                stats["en_tokens"].append(len(en_ids))
                stats["bn_tokens"].append(len(bn_ids))

                # Add to processed data
                processed_data.append(
                    {"en_ids": en_ids, "bn_ids": bn_ids, "en_text": en_text, "bn_text": bn_text}
                )

            except Exception:
                stats["skipped_examples"] += 1
                continue

        # Save processed data
        pd.DataFrame(processed_data).to_parquet(output_file)

        # Calculate final stats
        stats.update(
            {
                "processed_examples": len(processed_data),
                "avg_en_tokens": (
                    sum(stats["en_tokens"]) / len(stats["en_tokens"]) if stats["en_tokens"] else 0
                ),
                "avg_bn_tokens": (
                    sum(stats["bn_tokens"]) / len(stats["bn_tokens"]) if stats["bn_tokens"] else 0
                ),
                "max_en_tokens": max(stats["en_tokens"], default=0),
                "max_bn_tokens": max(stats["bn_tokens"], default=0),
            }
        )

        return stats
