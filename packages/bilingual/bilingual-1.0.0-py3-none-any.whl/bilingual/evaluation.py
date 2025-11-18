"""
Evaluation metrics and utilities for bilingual models.

Provides metrics for generation, translation, and classification tasks.
"""

import warnings
from typing import Any, Dict, List


def compute_bleu(
    predictions: List[str],
    references: List[List[str]],
) -> float:
    """
    Compute BLEU score for translation.
    Args:
        predictions: List of predicted translations
        references: List of reference translations (can have multiple refs per prediction)

    Returns:
        BLEU score (0-100)
    """
    try:
        from sacrebleu import corpus_bleu

        # Convert references format if needed
        if isinstance(references[0], str):
            references = [[ref] for ref in references]

        # Transpose references for sacrebleu format
        refs_transposed = list(zip(*references))

        bleu = corpus_bleu(predictions, refs_transposed)
        return float(bleu.score)

    except ImportError:
        warnings.warn("sacrebleu not installed. Install with: pip install sacrebleu")
        return 0.0


def compute_rouge(
    predictions: List[str],
    references: List[str],
) -> Dict[str, float]:
    """
    Compute ROUGE scores for generation.

    Args:
        predictions: List of predicted texts
        references: List of reference texts

    Returns:
        Dictionary with ROUGE-1, ROUGE-2, ROUGE-L scores
    """
    try:
        from rouge_score import rouge_scorer

        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

        scores = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}

        for pred, ref in zip(predictions, references):
            score = scorer.score(ref, pred)
            for key in scores:
                scores[key] += score[key].fmeasure

        # Average scores
        n = len(predictions)
        scores = {k: v / n for k, v in scores.items()}

        return scores

    except ImportError:
        warnings.warn("rouge-score not installed. Install with: pip install rouge-score")
        return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}


def compute_perplexity(
    model: Any,
    texts: List[str],
) -> float:
    """
    Compute perplexity of texts under a language model.

    Args:
        model: Language model
        texts: List of texts to evaluate

    Returns:
        Average perplexity
    """
    # Placeholder - will be implemented with actual model
    warnings.warn("Perplexity computation not yet implemented")
    return 0.0


def compute_accuracy(
    predictions: List[str],
    references: List[str],
) -> float:
    """
    Compute classification accuracy.

    Args:
        predictions: Predicted labels
        references: True labels

    Returns:
        Accuracy (0-1)
    """
    if len(predictions) != len(references):
        raise ValueError("Predictions and references must have same length")

    correct = sum(p == r for p, r in zip(predictions, references))
    return correct / len(predictions)


def compute_f1(
    predictions: List[str],
    references: List[str],
    average: str = "macro",
) -> float:
    """
    Compute F1 score for classification.

    Args:
        predictions: Predicted labels
        references: True labels
        average: Averaging method ('micro', 'macro', 'weighted')

    Returns:
        F1 score (0-1)
    """
    try:
        from sklearn.metrics import f1_score

        score = f1_score(references, predictions, average=average)
        return float(score)

    except ImportError:
        warnings.warn("scikit-learn not installed. Install with: pip install scikit-learn")
        return 0.0


def evaluate_model(
    dataset_path: str,
    model_name: str,
    metric: str = "all",
) -> Dict[str, Any]:
    """
    Evaluate a model on a dataset.

    Args:
        dataset_path: Path to evaluation dataset
        model_name: Name of model to evaluate
        metric: Metric to compute ('all', 'bleu', 'rouge', 'accuracy', etc.)

    Returns:
        Dictionary of evaluation results
    """
    from bilingual import bilingual_api as bb
    from bilingual.data_utils import BilingualDataset

    # Load dataset
    dataset = BilingualDataset(file_path=dataset_path)

    # Load model (not used yet in placeholder implementation)
    _ = bb.load_model(model_name)

    results = {}

    # Compute requested metrics
    # This is a placeholder - actual implementation depends on task type
    warnings.warn("Model evaluation not fully implemented yet")

    results["dataset"] = dataset_path
    results["model"] = model_name
    results["num_samples"] = str(len(dataset))


"""
Evaluation metrics and utilities for bilingual models.

Provides metrics for generation, translation, and classification tasks.
"""

import math
import re
import warnings
from collections import Counter
from typing import Any, Dict, List

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
    from nltk.translate.meteor_score import meteor_score

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available. Install with: pip install nltk")


class BilingualEvaluator:
    """
    Comprehensive evaluator for bilingual NLP tasks.
    """

    def __init__(self):
        """Initialize the evaluator."""
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data
                nltk.data.find("tokenizers/punkt")
                nltk.data.find("punkt_tab")
            except LookupError:
                print("Downloading NLTK punkt tokenizer...")
                nltk.download("punkt", quiet=True)
                nltk.download("punkt_tab", quiet=True)

        # Smoothing function for BLEU
        self.smoothing = SmoothingFunction().method4 if NLTK_AVAILABLE else None

    def tokenize_text(self, text: str, lang: str = "en") -> List[str]:
        """
        Tokenize text for evaluation.

        Args:
            text: Text to tokenize
            lang: Language ('en' or 'bn')

        Returns:
            List of tokens
        """
        if NLTK_AVAILABLE:
            try:
                return word_tokenize(text.lower())
            except:
                pass

        # Fallback tokenization
        # Remove punctuation and split
        text = re.sub(r"[^\w\s]", " ", text.lower())
        return text.split()

    def bleu_score(self, reference: str, candidate: str, n_gram: int = 4) -> float:
        """
        Calculate BLEU score for translation quality.

        Args:
            reference: Reference translation
            candidate: Generated translation
            n_gram: Maximum n-gram order (1-4)

        Returns:
            BLEU score (0-1)
        """
        if not NLTK_AVAILABLE:
            return self._simple_bleu_fallback(reference, candidate, n_gram)

        ref_tokens = [self.tokenize_text(reference)]
        cand_tokens = self.tokenize_text(candidate)

        if not ref_tokens[0] or not cand_tokens:
            return 0.0

        try:
            weights = tuple(1.0 / n_gram for _ in range(n_gram))
            return sentence_bleu(
                ref_tokens, cand_tokens, smoothing_function=self.smoothing, weights=weights
            )
        except:
            return self._simple_bleu_fallback(reference, candidate, n_gram)

    def _simple_bleu_fallback(self, reference: str, candidate: str, n_gram: int = 4) -> float:
        """Simple BLEU implementation when NLTK is not available."""
        ref_tokens = list(self.tokenize_text(reference))  # Convert to list
        cand_tokens = self.tokenize_text(candidate)

        if not ref_tokens or not cand_tokens:
            return 0.0

        # Calculate n-gram overlap
        matches = 0
        total = 0

        for n in range(1, n_gram + 1):
            ref_ngrams = self._get_ngrams(ref_tokens, n)
            cand_ngrams = self._get_ngrams(cand_tokens, n)

            matches += len(ref_ngrams & cand_ngrams)
            total += len(ref_ngrams)

        if total == 0:
            return 0.0

        precision = matches / total

        # Brevity penalty
        ref_len = len(ref_tokens)
        cand_len = len(cand_tokens)
        if cand_len > ref_len:
            brevity_penalty = 1.0
        else:
            brevity_penalty = math.exp(1 - ref_len / cand_len) if cand_len > 0 else 0.0

        return brevity_penalty * precision

    def _get_ngrams(self, tokens: List[str], n: int) -> set:
        """Get n-grams from token list."""
        ngrams = set()
        for i in range(len(tokens) - n + 1):
            ngram = " ".join(tokens[i : i + n])
            ngrams.add(ngram)
        return ngrams

    def rouge_score(self, reference: str, candidate: str, rouge_type: str = "rouge-l") -> float:
        """
        Calculate ROUGE score for text summarization/generation.

        Args:
            reference: Reference text
            candidate: Generated text
            rouge_type: Type of ROUGE ('rouge-1', 'rouge-2', 'rouge-l')

        Returns:
            ROUGE score (0-1)
        """
        ref_tokens = set(self.tokenize_text(reference))
        cand_tokens = set(self.tokenize_text(candidate))

        if rouge_type == "rouge-1":
            return self._rouge_n(ref_tokens, cand_tokens, 1)
        elif rouge_type == "rouge-2":
            return self._rouge_n(ref_tokens, cand_tokens, 2)
        elif rouge_type == "rouge-l":
            return self._rouge_l(reference, candidate)
        else:
            return 0.0

    def _rouge_n(self, ref_tokens: set, cand_tokens: set, n: int) -> float:
        """Calculate ROUGE-N score."""
        if n == 1:
            overlap = len(ref_tokens & cand_tokens)
            total = len(ref_tokens)
        else:
            ref_ngrams = self._get_ngrams(list(ref_tokens), n)
            cand_ngrams = self._get_ngrams(list(cand_tokens), n)
            overlap = len(ref_ngrams & cand_ngrams)
            total = len(ref_ngrams)

        return overlap / total if total > 0 else 0.0

    def _rouge_l(self, reference: str, candidate: str) -> float:
        """Calculate ROUGE-L (Longest Common Subsequence) score."""
        # Simplified LCS-based ROUGE-L
        ref_words = self.tokenize_text(reference)
        cand_words = self.tokenize_text(candidate)

        # Find LCS length
        lcs_length = self._lcs_length(ref_words, cand_words)

        # Calculate precision and recall
        precision = lcs_length / len(cand_words) if cand_words else 0.0
        recall = lcs_length / len(ref_words) if ref_words else 0.0

        # F1 score
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return f1

    def _lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """Calculate Longest Common Subsequence length."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    def meteor_score(self, reference: str, candidate: str) -> float:
        """
        Calculate METEOR score for machine translation evaluation.

        Args:
            reference: Reference translation
            candidate: Generated translation

        Returns:
            METEOR score (0-1)
        """
        if not NLTK_AVAILABLE:
            # Simplified METEOR fallback
            return self._simple_meteor_fallback(reference, candidate)

        try:
            ref_tokens = self.tokenize_text(reference)
            cand_tokens = self.tokenize_text(candidate)

            return meteor_score([ref_tokens], cand_tokens)
        except:
            return self._simple_meteor_fallback(reference, candidate)

    def _simple_meteor_fallback(self, reference: str, candidate: str) -> float:
        """Simple METEOR implementation fallback."""
        ref_tokens = set(self.tokenize_text(reference))
        cand_tokens = set(self.tokenize_text(candidate))

        # Exact matches
        exact_matches = len(ref_tokens & cand_tokens)

        # Calculate precision and recall
        precision = exact_matches / len(cand_tokens) if cand_tokens else 0.0
        recall = exact_matches / len(ref_tokens) if ref_tokens else 0.0

        # F-mean with alpha = 0.9 (as in original METEOR)
        alpha = 0.9
        if precision + recall == 0:
            return 0.0

        f_mean = (precision * recall) / (alpha * precision + (1 - alpha) * recall)

        # Penalty for longer candidates (brevity penalty)
        ref_len = len(ref_tokens)
        cand_len = len(cand_tokens)

        if cand_len <= ref_len:
            penalty = 1.0
        else:
            penalty = math.exp(1 - cand_len / ref_len) if ref_len > 0 else 0.0

        return penalty * f_mean

    def chrF_score(self, reference: str, candidate: str, beta: float = 2.0) -> float:
        """
        Calculate chrF (character n-gram F-score) for translation evaluation.

        Args:
            reference: Reference translation
            candidate: Generated translation
            beta: Beta parameter for F-score (default 2.0)

        Returns:
            chrF score (0-1)
        """
        ref_chars = list(reference.lower())
        cand_chars = list(candidate.lower())

        # Character 1-gram and 4-gram F-scores
        f1_1gram = self._char_f_score(ref_chars, cand_chars, 1, beta)
        f1_4gram = self._char_f_score(ref_chars, cand_chars, 4, beta)

        # Average the two scores
        return (f1_1gram + f1_4gram) / 2.0

    def _char_f_score(
        self, ref_chars: List[str], cand_chars: List[str], n: int, beta: float
    ) -> float:
        """Calculate character n-gram F-score."""
        ref_ngrams = self._get_char_ngrams(ref_chars, n)
        cand_ngrams = self._get_char_ngrams(cand_chars, n)

        matches = sum(
            min(ref_ngrams.get(ngram, 0), cand_ngrams.get(ngram, 0))
            for ngram in set(ref_ngrams) | set(cand_ngrams)
        )

        total_ref = sum(ref_ngrams.values())
        total_cand = sum(cand_ngrams.values())

        precision = matches / total_cand if total_cand > 0 else 0.0
        recall = matches / total_ref if total_ref > 0 else 0.0

        if precision + recall == 0:
            return 0.0

        beta_sq = beta**2
        f_score = (1 + beta_sq) * precision * recall / (beta_sq * precision + recall)

        return f_score

    def _get_char_ngrams(self, chars: List[str], n: int) -> Counter:
        """Get character n-grams."""
        ngrams = Counter()
        for i in range(len(chars) - n + 1):
            ngram = "".join(chars[i : i + n])
            ngrams[ngram] += 1
        return ngrams

    def diversity_metrics(self, texts: List[str]) -> Dict[str, float]:
        """
        Calculate diversity metrics for generated text.

        Args:
            texts: List of generated texts

        Returns:
            Dictionary of diversity metrics
        """
        if not texts:
            return {"unique_ngrams": 0.0, "distinct_ngrams": 0.0, "entropy": 0.0}

        all_ngrams = []
        for text in texts:
            tokens = self.tokenize_text(text)
            ngrams = self._get_ngrams(tokens, 2)  # Bigram diversity
            all_ngrams.extend(list(ngrams))

        if not all_ngrams:
            return {"unique_ngrams": 0.0, "distinct_ngrams": 0.0, "entropy": 0.0}

        # Unique n-grams ratio
        unique_ngrams = len(set(all_ngrams))
        total_ngrams = len(all_ngrams)
        unique_ratio = unique_ngrams / total_ngrams if total_ngrams > 0 else 0.0

        # Distinct n-grams (n-grams that appear only once)
        ngram_counts = Counter(all_ngrams)
        distinct_ngrams = len([ngram for ngram, count in ngram_counts.items() if count == 1])
        distinct_ratio = distinct_ngrams / unique_ngrams if unique_ngrams > 0 else 0.0

        # Entropy calculation
        entropy = 0.0
        for ngram, count in ngram_counts.items():
            prob = count / total_ngrams
            if prob > 0:
                entropy -= prob * math.log2(prob)

        return {
            "unique_ngrams": unique_ratio,
            "distinct_ngrams": distinct_ratio,
            "entropy": entropy,
        }

    def classification_metrics(self, y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
        """
        Calculate classification metrics (F1, precision, recall).

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary of classification metrics
        """
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have the same length")

        # Convert to sets for easier calculation
        true_set = set(y_true)
        pred_set = set(y_pred)

        # Calculate TP, FP, FN for each class
        metrics = {}

        for label in true_set | pred_set:
            tp = sum(1 for true, pred in zip(y_true, y_pred) if true == label and pred == label)
            fp = sum(1 for true, pred in zip(y_true, y_pred) if true != label and pred == label)
            fn = sum(1 for true, pred in zip(y_true, y_pred) if true == label and pred != label)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            )

            metrics[label] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": tp + fn,
            }

        # Macro-averaged metrics
        macro_precision = (
            sum(m["precision"] for m in metrics.values()) / len(metrics) if metrics else 0.0
        )
        macro_recall = sum(m["recall"] for m in metrics.values()) / len(metrics) if metrics else 0.0
        macro_f1 = sum(m["f1"] for m in metrics.values()) / len(metrics) if metrics else 0.0

        # Micro-averaged metrics (overall)
        total_tp = (
            sum(m["f1"] * m["support"] for m in metrics.values())
            / sum(m["support"] for m in metrics.values())
            if metrics
            else 0.0
        )

        return {
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
            "micro_f1": total_tp,
            "per_class": metrics,
        }

    def evaluate_translation(
        self, references: List[str], candidates: List[str]
    ) -> Dict[str, float]:
        """
        Comprehensive evaluation for translation tasks.

        Args:
            references: List of reference translations
            candidates: List of generated translations

        Returns:
            Dictionary of translation metrics
        """
        if len(references) != len(candidates):
            raise ValueError("References and candidates must have the same length")

        bleu_scores = []
        meteor_scores = []
        chrf_scores = []

        for ref, cand in zip(references, candidates):
            bleu_scores.append(self.bleu_score(ref, cand))
            meteor_scores.append(self.meteor_score(ref, cand))
            chrf_scores.append(self.chrF_score(ref, cand))

        return {
            "bleu": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0,
            "meteor": sum(meteor_scores) / len(meteor_scores) if meteor_scores else 0.0,
            "chrf": sum(chrf_scores) / len(chrf_scores) if chrf_scores else 0.0,
            "num_samples": len(references),
        }

    def evaluate_generation(self, references: List[str], candidates: List[str]) -> Dict[str, Any]:
        """
        Comprehensive evaluation for text generation tasks.

        Args:
            references: List of reference texts
            candidates: List of generated texts

        Returns:
            Dictionary of generation metrics
        """
        if len(references) != len(candidates):
            raise ValueError("References and candidates must have the same length")

        bleu_scores = []
        rouge1_scores = []
        rouge2_scores = []
        rougel_scores = []

        for ref, cand in zip(references, candidates):
            bleu_scores.append(self.bleu_score(ref, cand))
            rouge1_scores.append(self.rouge_score(ref, cand, "rouge-1"))
            rouge2_scores.append(self.rouge_score(ref, cand, "rouge-2"))
            rougel_scores.append(self.rouge_score(ref, cand, "rouge-l"))

        # Diversity metrics
        diversity = self.diversity_metrics(candidates)

        return {
            "bleu": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0,
            "rouge_1": sum(rouge1_scores) / len(rouge1_scores) if rouge1_scores else 0.0,
            "rouge_2": sum(rouge2_scores) / len(rouge2_scores) if rouge2_scores else 0.0,
            "rouge_l": sum(rougel_scores) / len(rougel_scores) if rougel_scores else 0.0,
            "diversity": diversity,
            "num_samples": len(references),
        }


# Global evaluator instance
_evaluator = None


def get_evaluator() -> BilingualEvaluator:
    """Get or create the global evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = BilingualEvaluator()
    return _evaluator


def evaluate_translation(references: List[str], candidates: List[str]) -> Dict[str, float]:
    """Convenience function for translation evaluation."""
    return get_evaluator().evaluate_translation(references, candidates)


def evaluate_generation(references: List[str], candidates: List[str]) -> Dict[str, Any]:
    """Convenience function for generation evaluation."""
    return get_evaluator().evaluate_generation(references, candidates)


def bleu_score(reference: str, candidate: str) -> float:
    """Convenience function for BLEU score calculation."""
    return get_evaluator().bleu_score(reference, candidate)


def rouge_score(reference: str, candidate: str, rouge_type: str = "rouge-l") -> float:
    """Convenience function for ROUGE score calculation."""
    return get_evaluator().rouge_score(reference, candidate, rouge_type)
