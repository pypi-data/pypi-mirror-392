#!/usr/bin/env python3
"""
ONNX model conversion for lightweight deployment.

This module provides utilities to convert Transformer models to ONNX format
for faster inference in production environments.
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import onnx
    import onnxruntime as ort
    import torch
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        BartForConditionalGeneration,
        BartTokenizer,
        MT5ForConditionalGeneration,
        MT5Tokenizer,
        T5ForConditionalGeneration,
        T5Tokenizer,
    )

    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("Warning: ONNX not available. Install with: pip install onnx onnxruntime")


class ONNXConverter:
    """
    Converter for Transformer models to ONNX format.
    """

    def __init__(self):
        """Initialize the ONNX converter."""
        if not ONNX_AVAILABLE:
            warnings.warn("ONNX not available. Install with: pip install onnx onnxruntime")

        self.converted_models = {}

    def convert_model(
        self,
        model_name: str,
        pytorch_model_path: str,
        onnx_output_path: str,
        model_type: str = "auto",
        opset_version: int = 11,
        **kwargs,
    ) -> str:
        """
        Convert a PyTorch model to ONNX format.

        Args:
            model_name: Name of the model (for reference)
            pytorch_model_path: Path to the PyTorch model
            onnx_output_path: Path to save the ONNX model
            model_type: Type of model ('t5', 'bart', 'mt5', 'auto')
            opset_version: ONNX opset version
            **kwargs: Additional conversion parameters

        Returns:
            Path to the converted ONNX model
        """
        if not ONNX_AVAILABLE:
            raise ImportError("ONNX not available")

        try:
            # Load the PyTorch model
            if model_type == "auto":
                model_type = self._detect_model_type(model_name)

            if model_type == "t5":
                model = T5ForConditionalGeneration.from_pretrained(pytorch_model_path)
                tokenizer = T5Tokenizer.from_pretrained(pytorch_model_path)
            elif model_type == "bart":
                model = BartForConditionalGeneration.from_pretrained(pytorch_model_path)
                tokenizer = BartTokenizer.from_pretrained(pytorch_model_path)
            elif model_type == "mt5":
                model = MT5ForConditionalGeneration.from_pretrained(pytorch_model_path)
                tokenizer = MT5Tokenizer.from_pretrained(pytorch_model_path)
            else:
                model = AutoModelForSeq2SeqLM.from_pretrained(pytorch_model_path)
                tokenizer = AutoTokenizer.from_pretrained(pytorch_model_path)

            model.eval()

            # Prepare sample input for tracing
            sample_text = "Hello, this is a sample input for model conversion."
            inputs = tokenizer(sample_text, return_tensors="pt", padding=True, truncation=True)

            # Convert to ONNX
            onnx_path = Path(onnx_output_path)
            onnx_path.parent.mkdir(parents=True, exist_ok=True)

            torch.onnx.export(
                model,
                (inputs["input_ids"], inputs["attention_mask"]),
                str(onnx_path),
                export_params=True,
                opset_version=opset_version,
                do_constant_folding=True,
                input_names=["input_ids", "attention_mask"],
                output_names=["output"],
                dynamic_axes={
                    "input_ids": {0: "batch_size", 1: "sequence_length"},
                    "attention_mask": {0: "batch_size", 1: "sequence_length"},
                    "output": {0: "batch_size", 1: "sequence_length"},
                },
                **kwargs,
            )

            # Verify the ONNX model
            onnx_model = onnx.load(str(onnx_path))
            onnx.checker.check_model(onnx_model)

            self.converted_models[model_name] = {
                "onnx_path": str(onnx_path),
                "model_type": model_type,
                "tokenizer_path": pytorch_model_path,
            }

            print(f"✅ Converted {model_type.upper()} model to ONNX: {onnx_path}")
            return str(onnx_path)

        except Exception as e:
            print(f"❌ Failed to convert model {model_name}: {e}")
            raise

    def _detect_model_type(self, model_name: str) -> str:
        """Auto-detect model type from name."""
        name_lower = model_name.lower()

        if "t5" in name_lower:
            return "t5"
        elif "bart" in name_lower:
            return "bart"
        elif "mt5" in name_lower:
            return "mt5"
        elif "mbart" in name_lower:
            return "mbart"
        else:
            return "auto"

    def create_inference_session(
        self, model_name: str, providers: Optional[List[str]] = None
    ) -> Any:
        """
        Create an ONNX Runtime inference session.

        Args:
            model_name: Name of the converted model
            providers: List of execution providers (e.g., ['CUDAExecutionProvider', 'CPUExecutionProvider'])

        Returns:
            ONNX Runtime inference session
        """
        if model_name not in self.converted_models:
            raise ValueError(f"Model {model_name} not converted to ONNX")

        if not ONNX_AVAILABLE:
            raise ImportError("ONNX Runtime not available")

        model_info = self.converted_models[model_name]

        if providers is None:
            providers = ["CPUExecutionProvider"]

        try:
            session = ort.InferenceSession(model_info["onnx_path"], providers=providers)

            print(f"✅ Created ONNX Runtime session for {model_name}")
            return session

        except Exception as e:
            print(f"❌ Failed to create inference session: {e}")
            raise

    def benchmark_onnx_model(
        self, model_name: str, sample_inputs: List[str], num_runs: int = 100
    ) -> Dict[str, float]:
        """
        Benchmark ONNX model performance.

        Args:
            model_name: Name of the ONNX model
            sample_inputs: List of sample input texts
            num_runs: Number of benchmark runs

        Returns:
            Dictionary of performance metrics
        """
        if model_name not in self.converted_models:
            raise ValueError(f"Model {model_name} not converted to ONNX")

        model_info = self.converted_models[model_name]

        # Load tokenizer
        model_type = model_info["model_type"]
        if model_type == "t5":
            tokenizer = T5Tokenizer.from_pretrained(model_info["tokenizer_path"])
        elif model_type == "bart":
            tokenizer = BartTokenizer.from_pretrained(model_info["tokenizer_path"])
        elif model_type == "mt5":
            tokenizer = MT5Tokenizer.from_pretrained(model_info["tokenizer_path"])
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_info["tokenizer_path"])

        # Create inference session
        session = self.create_inference_session(model_name)

        # Prepare inputs
        import time

        import numpy as np

        latencies = []
        throughputs = []

        for sample_text in sample_inputs:
            # Tokenize
            inputs = tokenizer(sample_text, return_tensors="pt", padding=True, truncation=True)
            input_ids = inputs["input_ids"].numpy()
            attention_mask = inputs["attention_mask"].numpy()

            # Measure inference time
            start_time = time.time()

            # Run inference
            session.run(None, {"input_ids": input_ids, "attention_mask": attention_mask})

            end_time = time.time()

            # Calculate metrics
            latency = (end_time - start_time) * 1000  # ms
            throughput = len(sample_text) / (end_time - start_time)  # chars/sec

            latencies.append(latency)
            throughputs.append(throughput)

        return {
            "average_latency_ms": np.mean(latencies),
            "latency_std_ms": np.std(latencies),
            "min_latency_ms": np.min(latencies),
            "max_latency_ms": np.max(latencies),
            "average_throughput_chars_per_sec": np.mean(throughputs),
            "throughput_std_chars_per_sec": np.std(throughputs),
            "num_runs": num_runs,
        }

    def optimize_onnx_model(self, model_name: str, optimization_level: str = "basic") -> str:
        """
        Optimize ONNX model for better performance.

        Args:
            model_name: Name of the model to optimize
            optimization_level: Level of optimization ('basic', 'extended', 'all')

        Returns:
            Path to optimized model
        """
        if model_name not in self.converted_models:
            raise ValueError(f"Model {model_name} not converted to ONNX")

        if not ONNX_AVAILABLE:
            raise ImportError("ONNX not available")

        try:
            from onnxruntime.tools.onnx_model_utils import optimize_model

            model_info = self.converted_models[model_name]
            input_path = model_info["onnx_path"]

            # Define optimization settings
            optimizations = {
                "basic": [
                    "eliminate_identity",
                    "eliminate_nop_transpose",
                    "fuse_consecutive_transposes",
                ],
                "extended": [
                    "eliminate_identity",
                    "eliminate_nop_transpose",
                    "fuse_consecutive_transposes",
                    "fuse_transpose_into_gemm",
                    "enable_gelu_approximation",
                ],
                "all": [],  # Use all available optimizations
            }

            if optimization_level == "all":
                optimized_model = optimize_model(input_path)
            else:
                optimized_model = optimize_model(input_path, optimizations[optimization_level])

            # Save optimized model
            optimized_path = input_path.replace(".onnx", f"_optimized_{optimization_level}.onnx")
            optimized_model.save_model_to_file(optimized_path)

            print(f"✅ Optimized ONNX model saved to: {optimized_path}")
            return optimized_path

        except Exception as e:
            print(f"❌ Failed to optimize model {model_name}: {e}")
            raise

    def list_converted_models(self) -> List[str]:
        """List all converted ONNX models."""
        return list(self.converted_models.keys())

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a converted model."""
        if model_name not in self.converted_models:
            return {"error": "Model not converted"}

        return self.converted_models[model_name].copy()


# Global ONNX converter instance
_onnx_converter = None


def get_onnx_converter() -> ONNXConverter:
    """Get or create the global ONNX converter instance."""
    global _onnx_converter
    if _onnx_converter is None:
        _onnx_converter = ONNXConverter()
    return _onnx_converter


def convert_to_onnx(
    model_name: str,
    pytorch_model_path: str,
    onnx_output_path: str,
    model_type: str = "auto",
    **kwargs,
) -> str:
    """Convenience function to convert a model to ONNX."""
    return get_onnx_converter().convert_model(
        model_name, pytorch_model_path, onnx_output_path, model_type, **kwargs
    )


def create_onnx_session(model_name: str, **kwargs) -> Any:
    """Convenience function to create an ONNX inference session."""
    return get_onnx_converter().create_inference_session(model_name, **kwargs)


def benchmark_onnx_model(model_name: str, sample_inputs: List[str], **kwargs) -> Dict[str, float]:
    """Convenience function to benchmark an ONNX model."""
    return get_onnx_converter().benchmark_onnx_model(model_name, sample_inputs, **kwargs)


def optimize_onnx_model(model_name: str, optimization_level: str = "basic") -> str:
    """Convenience function to optimize an ONNX model."""
    return get_onnx_converter().optimize_onnx_model(model_name, optimization_level)
