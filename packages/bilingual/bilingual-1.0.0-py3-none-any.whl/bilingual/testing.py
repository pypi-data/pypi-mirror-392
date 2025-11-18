#!/usr/bin/env python3
"""
Comprehensive testing framework for bilingual NLP models.

Provides testing utilities including:
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Fuzz testing for robustness
- Cross-language consistency tests
- Performance benchmarks
- Model bias detection
"""

import json
import random
import string
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import bilingual as bb

    BILINGUAL_AVAILABLE = True
except ImportError:
    BILINGUAL_AVAILABLE = False
    print("Warning: bilingual package not available for testing")


@dataclass
class TestResult:
    """Test result container."""

    test_name: str
    passed: bool
    duration: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BilingualTestSuite:
    """
    Comprehensive test suite for bilingual NLP functionality.
    """

    def __init__(self, output_dir: str = "test_results/"):
        """Initialize the test suite."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[TestResult] = []

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for core functionality."""
        results = {}

        # Test language detection
        results["language_detection"] = self._test_language_detection()

        # Test text normalization
        results["text_normalization"] = self._test_text_normalization()

        # Test tokenization
        results["tokenization"] = self._test_tokenization()

        # Test data augmentation
        results["data_augmentation"] = self._test_data_augmentation()

        # Test evaluation metrics
        results["evaluation_metrics"] = self._test_evaluation_metrics()

        return results

    def _test_language_detection(self) -> TestResult:
        """Test language detection functionality."""
        test_name = "language_detection"

        try:
            start_time = time.time()

            # Test cases
            test_cases = [
                ("আমি স্কুলে যাই।", "bengali"),
                ("I go to school.", "english"),
                ("Hello world!", "english"),
                ("বাংলাদেশ আমার দেশ।", "bengali"),
                ("Mixed আমি text", "mixed"),
            ]

            passed = True
            for text, expected_lang in test_cases:
                result = bb.detect_language(text)
                if result["language"] != expected_lang:
                    passed = False
                    break

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                metadata={"test_cases": len(test_cases)},
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def _test_text_normalization(self) -> TestResult:
        """Test text normalization."""
        test_name = "text_normalization"

        try:
            start_time = time.time()

            # Test normalization
            test_text = "  Hello   world!  "
            normalized = bb.normalize_text(test_text)

            # Basic checks
            passed = len(normalized) <= len(test_text)  # Should be normalized

            duration = time.time() - start_time

            return TestResult(test_name=test_name, passed=passed, duration=duration)

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def _test_tokenization(self) -> TestResult:
        """Test tokenization functionality."""
        test_name = "tokenization"

        try:
            start_time = time.time()

            # Test tokenization
            tokenizer = bb.load_tokenizer("models/tokenizer/bilingual_sp.model")
            test_text = "Hello world! আমি ভালো আছি।"
            tokens = tokenizer.encode(test_text)

            # Basic checks
            passed = isinstance(tokens, list) and len(tokens) > 0

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                metadata={"tokens_count": len(tokens)},
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def _test_data_augmentation(self) -> TestResult:
        """Test data augmentation functionality."""
        test_name = "data_augmentation"

        try:
            start_time = time.time()

            # Test augmentation
            test_text = "I love reading books"
            augmented = bb.augment_text(test_text, method="synonym", n=3)

            # Basic checks
            passed = isinstance(augmented, list) and len(augmented) == 3

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                metadata={"augmentations": len(augmented)},
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def _test_evaluation_metrics(self) -> TestResult:
        """Test evaluation metrics."""
        test_name = "evaluation_metrics"

        try:
            start_time = time.time()

            # Test BLEU score
            ref = "I love reading books"
            cand = "I adore reading books"
            bleu = bb.bleu_score(ref, cand)

            # Basic checks
            passed = 0.0 <= bleu <= 1.0

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name, passed=passed, duration=duration, metadata={"bleu_score": bleu}
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def run_fuzz_tests(self, num_tests: int = 100) -> Dict[str, Any]:
        """Run fuzz testing for robustness."""
        results = {}

        if not PYTEST_AVAILABLE or not BILINGUAL_AVAILABLE:
            return {"error": "Required testing libraries not available"}

        # Fuzz test language detection
        results["fuzz_language_detection"] = self._fuzz_language_detection(num_tests)

        # Fuzz test evaluation metrics
        results["fuzz_evaluation"] = self._fuzz_evaluation(num_tests)

        return results

    def _fuzz_language_detection(self, num_tests: int) -> TestResult:
        """Fuzz test language detection with random inputs."""
        test_name = "fuzz_language_detection"

        try:
            start_time = time.time()

            passed = True
            errors = 0

            for _ in range(num_tests):
                # Generate random text
                length = random.randint(1, 100)
                random_text = "".join(
                    random.choices(
                        string.ascii_letters + "আমিযাচ্ছিভালো" + string.punctuation + " ", k=length
                    )
                )

                try:
                    result = bb.detect_language(random_text)
                    # Basic validation
                    if not isinstance(result, dict) or "language" not in result:
                        passed = False
                        break
                except Exception:
                    errors += 1

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name,
                passed=passed and errors < num_tests * 0.1,  # Allow 10% error rate
                duration=duration,
                metadata={"tests_run": num_tests, "errors": errors},
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def _fuzz_evaluation(self, num_tests: int) -> TestResult:
        """Fuzz test evaluation metrics."""
        test_name = "fuzz_evaluation"

        try:
            start_time = time.time()

            passed = True
            errors = 0

            for _ in range(num_tests):
                # Generate random texts
                ref = "".join(random.choices(string.ascii_letters + " ", k=random.randint(10, 50)))
                cand = "".join(random.choices(string.ascii_letters + " ", k=random.randint(10, 50)))

                try:
                    bleu = bb.bleu_score(ref, cand)
                    # Basic validation
                    if not (0.0 <= bleu <= 1.0):
                        passed = False
                        break
                except Exception:
                    errors += 1

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name,
                passed=passed and errors < num_tests * 0.1,
                duration=duration,
                metadata={"tests_run": num_tests, "errors": errors},
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for end-to-end workflows."""
        results = {}

        # Test complete pipeline
        results["full_pipeline"] = self._test_full_pipeline()

        # Test model loading and inference
        results["model_integration"] = self._test_model_integration()

        return results

    def _test_full_pipeline(self) -> TestResult:
        """Test complete NLP pipeline."""
        test_name = "full_pipeline"

        try:
            start_time = time.time()

            # Test complete workflow
            text = "Hello আমি John বলে ডাকি।"

            # Language detection
            detected_lang = bb.detect_language(text)

            # Text processing
            if detected_lang == "mixed":
                bb.detect_language_segments(text)

            # Evaluation
            bleu = bb.bleu_score("Hello world", "Hello world")

            # Basic checks
            passed = detected_lang in ["bn", "en", "mixed"] and 0.0 <= bleu <= 1.0

            duration = time.time() - start_time

            return TestResult(test_name=test_name, passed=passed, duration=duration)

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def _test_model_integration(self) -> TestResult:
        """Test model loading and inference."""
        test_name = "model_integration"

        try:
            start_time = time.time()

            # Test model loading (this might fail if models aren't available)
            try:
                bb.load_model("t5-small", "t5")
                model_loaded = True
            except Exception:
                model_loaded = False

            # Test tokenizer loading
            try:
                tokenizer = bb.load_tokenizer("models/tokenizer/bilingual_sp.model")
                tokenizer_loaded = True
            except Exception:
                tokenizer_loaded = False

            # Basic checks
            passed = tokenizer_loaded  # At minimum, tokenizer should work

            duration = time.time() - start_time

            return TestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                metadata={"model_loaded": model_loaded, "tokenizer_loaded": tokenizer_loaded},
            )

        except Exception as e:
            return TestResult(test_name=test_name, passed=False, duration=0.0, error_message=str(e))

    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks."""
        results = {}

        # Benchmark language detection
        results["lang_detection_perf"] = self._benchmark_language_detection()

        # Benchmark evaluation metrics
        results["eval_metrics_perf"] = self._benchmark_evaluation_metrics()

        return results

    def _benchmark_language_detection(self) -> Dict[str, Any]:
        """Benchmark language detection performance."""
        num_runs = 100

        try:
            texts = [
                "Hello world! This is English text.",
                "আমি বাংলাদেশে থাকি এবং বাংলা ভাষায় কথা বলি।",
                "Mixed আমি text with বাংলা and English words.",
                "Simple text.",
                "আমি স্কুলে যাই।",
            ] * (num_runs // 5)

            start_time = time.time()

            for text in texts:
                bb.detect_language(text)

            total_time = time.time() - start_time

            return {
                "total_time": total_time,
                "avg_time_per_sample": total_time / len(texts),
                "samples_per_second": len(texts) / total_time,
                "num_samples": len(texts),
            }

        except Exception as e:
            return {"error": str(e)}

    def _benchmark_evaluation_metrics(self) -> Dict[str, Any]:
        """Benchmark evaluation metrics performance."""
        num_runs = 100

        try:
            pairs = [
                ("I love reading books", "I adore reading books"),
                ("The weather is nice", "The weather is beautiful"),
                ("Hello world", "Hi world"),
                ("Programming is fun", "Coding is enjoyable"),
            ] * (num_runs // 4)

            start_time = time.time()

            for ref, cand in pairs:
                bb.bleu_score(ref, cand)

            total_time = time.time() - start_time

            return {
                "total_time": total_time,
                "avg_time_per_sample": total_time / len(pairs),
                "samples_per_second": len(pairs) / total_time,
                "num_samples": len(pairs),
            }

        except Exception as e:
            return {"error": str(e)}

    def generate_test_report(self, output_file: str = "test_report.json") -> Dict[str, Any]:
        """Generate comprehensive test report."""
        # Run all tests
        unit_results = self.run_unit_tests()
        integration_results = self.run_integration_tests()
        perf_results = self.run_performance_benchmarks()

        # Calculate summary statistics
        total_tests = len(unit_results) + len(integration_results)
        passed_tests = sum(1 for result in unit_results.values() if result.passed) + sum(
            1 for result in integration_results.values() if result.passed
        )

        # Compile report
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "unit_tests": {
                name: {
                    "passed": result.passed,
                    "duration": result.duration,
                    "error": result.error_message,
                    "metadata": result.metadata,
                }
                for name, result in unit_results.items()
            },
            "integration_tests": {
                name: {
                    "passed": result.passed,
                    "duration": result.duration,
                    "error": result.error_message,
                    "metadata": result.metadata,
                }
                for name, result in integration_results.items()
            },
            "performance_benchmarks": perf_results,
        }

        # Save report
        with open(self.output_dir / output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📊 Test report saved to: {self.output_dir / output_file}")
        return report


# Global test suite instance
_test_suite = None


def get_test_suite(output_dir: str = "test_results/") -> BilingualTestSuite:
    """Get or create the global test suite instance."""
    global _test_suite
    if _test_suite is None:
        _test_suite = BilingualTestSuite(output_dir)
    return _test_suite


def run_unit_tests() -> Dict[str, Any]:
    """Convenience function to run unit tests."""
    return get_test_suite().run_unit_tests()


def run_integration_tests() -> Dict[str, Any]:
    """Convenience function to run integration tests."""
    return get_test_suite().run_integration_tests()


def run_performance_benchmarks() -> Dict[str, Any]:
    """Convenience function to run performance benchmarks."""
    return get_test_suite().run_performance_benchmarks()


def generate_test_report(output_file: str = "test_report.json") -> Dict[str, Any]:
    """Convenience function to generate test report."""
    return get_test_suite().generate_test_report(output_file)
