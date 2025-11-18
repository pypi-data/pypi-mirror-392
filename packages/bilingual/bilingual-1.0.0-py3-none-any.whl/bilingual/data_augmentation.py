#!/usr/bin/env python3
"""
Data augmentation techniques for bilingual text processing.

This module provides various augmentation methods to expand datasets:
- Paraphrasing
- Back-translation
- Noise addition
- Synonym replacement
- Text mixing
"""

import random
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


class DataAugmenter:
    """
    Data augmentation utilities for bilingual text processing.
    """

    def __init__(self):
        """Initialize the data augmenter."""
        # Common English synonyms
        self.english_synonyms = {
            "good": ["excellent", "great", "wonderful", "fantastic", "amazing"],
            "bad": ["terrible", "awful", "horrible", "dreadful", "poor"],
            "big": ["large", "huge", "enormous", "massive", "gigantic"],
            "small": ["tiny", "little", "miniature", "compact", "mini"],
            "happy": ["joyful", "cheerful", "delighted", "pleased", "glad"],
            "sad": ["unhappy", "sorrowful", "depressed", "miserable", "down"],
            "fast": ["quick", "rapid", "speedy", "swift", "hasty"],
            "slow": ["leisurely", "sluggish", "unhurried", "languid", "lazy"],
            "love": ["adore", "cherish", "worship", "treasure", "fancy"],
            "hate": ["despise", "detest", "loath", "abhor", "dislike"],
        }

        # Common Bengali synonyms (limited set for demo)
        self.bengali_synonyms = {
            "ভালো": ["উত্তম", "চমৎকার", "সুন্দর", "অসাধারণ"],
            "খারাপ": ["মন্দ", "নিকৃষ্ট", "ভয়ানক", "বাজে"],
            "বড়": ["বিশাল", "প্রকাণ্ড", "অতিকায়", "মহান"],
            "ছোট": ["ক্ষুদ্র", "ছোটখাটো", "ক্ষুদ্রাকার", "অণু"],
            "খুশি": ["আনন্দিত", "প্রফুল্ল", "উল্লসিত", "হর্ষিত"],
            "দুঃখিত": ["বিষণ্ণ", "শোকার্ত", "বেদনার্ত", "মর্মাহত"],
            "দ্রুত": ["তাড়াতাড়ি", "শীঘ্র", "চটপট", "জলদি"],
            "ধীরে": ["আস্তে", "শান্তভাবে", "সময় নিয়ে", "আরামে"],
        }

        # Noise patterns for text corruption
        self.noise_patterns = [
            ("keyboard_typos", self._add_keyboard_typos),
            ("punctuation_noise", self._add_punctuation_noise),
            ("spacing_noise", self._add_spacing_noise),
            ("character_noise", self._add_character_noise),
        ]

    def synonym_replacement(self, text: str, lang: str = "en", n: int = 1) -> List[str]:
        """
        Replace words with their synonyms.

        Args:
            text: Input text
            lang: Language ('en' or 'bn')
            n: Number of augmentations to create

        Returns:
            List of augmented texts
        """
        synonyms = self.english_synonyms if lang == "en" else self.bengali_synonyms
        words = text.split()

        augmented_texts = []

        for _ in range(n):
            new_words = words.copy()
            words_to_replace = min(len(words) // 3, 3)  # Replace up to 1/3 of words

            for _ in range(words_to_replace):
                # Find a word that has synonyms
                available_words = [
                    i for i, word in enumerate(new_words) if word.lower() in synonyms
                ]

                if available_words:
                    idx = random.choice(available_words)
                    original_word = new_words[idx].lower()
                    if original_word in synonyms:
                        new_words[idx] = random.choice(synonyms[original_word])

            augmented_texts.append(" ".join(new_words))

        return augmented_texts

    def back_translation_augmentation(self, text: str, intermediate_lang: str = "en") -> List[str]:
        """
        Simulate back-translation by converting to intermediate language and back.
        This is a simplified version - in practice, you'd use actual translation models.

        Args:
            text: Input text
            intermediate_lang: Intermediate language for translation

        Returns:
            List of back-translated texts
        """
        # This is a simplified simulation
        # In practice, you'd use translation APIs or models

        # Simple word reordering and slight modifications
        words = text.split()
        if len(words) > 3:
            # Swap some words around (simple paraphrase)
            for _ in range(min(2, len(words) // 2)):
                if len(words) > 1:
                    i, j = random.sample(range(len(words)), 2)
                    words[i], words[j] = words[j], words[i]

        # Add some variation in punctuation
        if random.random() > 0.7:
            words.append(random.choice([".", "!", "?"]))

        return [" ".join(words)]

    def add_noise(self, text: str, noise_type: str = "random", intensity: float = 0.1) -> str:
        """
        Add various types of noise to text.

        Args:
            text: Input text
            noise_type: Type of noise ('random', 'keyboard_typos', etc.)
            intensity: Noise intensity (0.0 to 1.0)

        Returns:
            Noisy text
        """
        if noise_type == "random":
            noise_types = [pattern[0] for pattern in self.noise_patterns]
            noise_func = random.choice([pattern[1] for pattern in self.noise_patterns])
        else:
            noise_func = next(
                pattern[1] for pattern in self.noise_patterns if pattern[0] == noise_type
            )

        return noise_func(text, intensity)

    def _add_keyboard_typos(self, text: str, intensity: float) -> str:
        """Add keyboard typo noise."""
        # Common keyboard adjacency typos
        keyboard_typos = {
            "a": "qwsz",
            "s": "qwaedzxc",
            "d": "wersfxcv",
            "f": "drtgvc",
            "g": "fthyvbn",
            "h": "gjuybnm",
            "j": "hikunm",
            "k": "jilom",
            "l": "kop",
            "q": "wa",
            "w": "qase",
            "e": "wsdr",
            "r": "edft",
            "t": "rfgy",
            "y": "tghu",
            "u": "yhji",
            "i": "ujko",
            "o": "iklp",
            "p": "ol",
        }

        result = []
        for char in text:
            if char.lower() in keyboard_typos and random.random() < intensity:
                typo_options = keyboard_typos[char.lower()]
                result.append(
                    random.choice(typo_options).upper()
                    if char.isupper()
                    else random.choice(typo_options)
                )
            else:
                result.append(char)

        return "".join(result)

    def _add_punctuation_noise(self, text: str, intensity: float) -> str:
        """Add random punctuation."""
        punctuation = ".,!?;:-()[]{}\"'"
        result = []

        for char in text:
            result.append(char)
            if char.isspace() and random.random() < intensity:
                result.append(random.choice(punctuation))

        return "".join(result)

    def _add_spacing_noise(self, text: str, intensity: float) -> str:
        """Add random spacing variations."""
        result = []
        for char in text:
            if char.isspace():
                # Add extra spaces randomly
                if random.random() < intensity:
                    result.append(" " * random.randint(1, 3))
                else:
                    result.append(char)
            else:
                result.append(char)

        return "".join(result)

    def _add_character_noise(self, text: str, intensity: float) -> str:
        """Add random character insertions/deletions."""
        result = list(text)
        chars_to_modify = max(1, int(len(text) * intensity))

        for _ in range(chars_to_modify):
            if random.random() < 0.5 and len(result) > 0:
                # Delete random character
                idx = random.randint(0, len(result) - 1)
                result.pop(idx)
            else:
                # Insert random character
                idx = random.randint(0, len(result))
                random_char = chr(random.randint(32, 126))  # Printable ASCII
                result.insert(idx, random_char)

        return "".join(result)

    def mix_languages(self, bn_text: str, en_text: str, ratio: float = 0.5) -> str:
        """
        Create mixed-language text by combining Bangla and English.

        Args:
            bn_text: Bengali text
            en_text: English text
            ratio: Ratio of Bengali to English content

        Returns:
            Mixed language text
        """
        bn_words = bn_text.split()
        en_words = en_text.split()

        mixed_words = []
        for i in range(max(len(bn_words), len(en_words))):
            if random.random() < ratio and i < len(bn_words):
                mixed_words.append(bn_words[i])
            elif i < len(en_words):
                mixed_words.append(en_words[i])

        return " ".join(mixed_words)

    def paraphrase_text(self, text: str, lang: str = "en", n: int = 3) -> List[str]:
        """
        Generate paraphrases of the input text.

        Args:
            text: Input text to paraphrase
            lang: Language ('en' or 'bn')
            n: Number of paraphrases to generate

        Returns:
            List of paraphrased texts
        """
        paraphrases = []

        for _ in range(n):
            # Apply multiple augmentation techniques
            paraphrase = text

            # Synonym replacement
            paraphrase = random.choice(self.synonym_replacement(paraphrase, lang, 1))

            # Add some noise (light)
            paraphrase = self.add_noise(paraphrase, intensity=0.05)

            paraphrases.append(paraphrase)

        return paraphrases

    def augment_dataset(self, dataset: List[Dict], augmentations_per_sample: int = 2) -> List[Dict]:
        """
        Augment an entire dataset.

        Args:
            dataset: List of text samples with metadata
            augmentations_per_sample: Number of augmentations per original sample

        Returns:
            Augmented dataset
        """
        augmented_dataset = []

        for sample in dataset:
            # Add original sample
            augmented_dataset.append(sample)

            # Detect language
            text = sample.get("text", "")
            lang = "en"  # Default, could be enhanced with language detection

            # Generate augmentations
            for _ in range(augmentations_per_sample):
                augmented_text = text

                # Apply random augmentation techniques
                techniques = ["synonym", "noise", "paraphrase"]
                technique = random.choice(techniques)

                if technique == "synonym":
                    augmented_texts = self.synonym_replacement(augmented_text, lang, 1)
                    augmented_text = augmented_texts[0] if augmented_texts else augmented_text

                elif technique == "noise":
                    augmented_text = self.add_noise(augmented_text, intensity=0.1)

                elif technique == "paraphrase":
                    paraphrases = self.paraphrase_text(augmented_text, lang, 1)
                    augmented_text = paraphrases[0] if paraphrases else augmented_text

                # Add augmented sample
                augmented_sample = sample.copy()
                augmented_sample["text"] = augmented_text
                augmented_sample["augmented"] = True
                augmented_sample["original_text"] = text

                augmented_dataset.append(augmented_sample)

        return augmented_dataset


# Global augmenter instance
_augmenter = None


def get_data_augmenter() -> DataAugmenter:
    """Get or create the global data augmenter instance."""
    global _augmenter
    if _augmenter is None:
        _augmenter = DataAugmenter()
    return _augmenter


def augment_text(text: str, method: str = "synonym", lang: str = "en", **kwargs) -> List[str]:
    """
    Convenience function to augment text.

    Args:
        text: Input text to augment
        method: Augmentation method ('synonym', 'noise', 'paraphrase', 'back_translate')
        lang: Language for augmentation
        **kwargs: Additional arguments for specific methods

    Returns:
        List of augmented texts
    """
    augmenter = get_data_augmenter()

    if method == "synonym":
        return augmenter.synonym_replacement(text, lang, kwargs.get("n", 1))
    elif method == "noise":
        return [
            augmenter.add_noise(
                text, kwargs.get("noise_type", "random"), kwargs.get("intensity", 0.1)
            )
        ]
    elif method == "paraphrase":
        return augmenter.paraphrase_text(text, lang, kwargs.get("n", 1))
    elif method == "back_translate":
        return augmenter.back_translation_augmentation(text, kwargs.get("intermediate_lang", "en"))
    else:
        return [text]
