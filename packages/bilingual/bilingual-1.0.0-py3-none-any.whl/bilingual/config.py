#!/usr/bin/env python3
"""
Configuration management for the Bilingual NLP toolkit.

Provides centralized configuration using Pydantic settings with
environment variable support and validation.
"""

import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseSettings, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    print("Warning: pydantic not available. Install with: pip install pydantic")
    PYDANTIC_AVAILABLE = False

if PYDANTIC_AVAILABLE:

    class ModelConfig(BaseSettings):
        """Configuration for language models."""

        # Model paths and settings
        default_model: str = Field(default="t5-small", description="Default model for generation")
        model_cache_dir: str = Field(default="models/cache", description="Model cache directory")
        tokenizer_path: str = Field(
            default="models/tokenizer/bilingual_sp.model", description="Tokenizer path"
        )

        # Training settings
        training_batch_size: int = Field(default=8, description="Training batch size")
        training_epochs: int = Field(default=3, description="Number of training epochs")
        learning_rate: float = Field(default=5e-5, description="Learning rate")
        max_seq_length: int = Field(default=512, description="Maximum sequence length")

        # LoRA settings
        lora_r: int = Field(default=16, description="LoRA rank")
        lora_alpha: int = Field(default=32, description="LoRA alpha")
        lora_dropout: float = Field(default=0.1, description="LoRA dropout")

        class Config:
            env_prefix = "BILINGUAL_MODEL_"

    class DataConfig(BaseSettings):
        """Configuration for data processing."""

        # Data directories
        raw_data_dir: str = Field(default="data/raw", description="Raw data directory")
        processed_data_dir: str = Field(
            default="datasets/processed", description="Processed data directory"
        )
        evaluations_dir: str = Field(
            default="data/evaluations", description="Evaluations directory"
        )

        # Data collection settings
        max_collection_items: int = Field(default=1000, description="Maximum items to collect")
        collection_timeout: int = Field(default=30, description="Collection timeout in seconds")

        # Data quality settings
        min_text_length: int = Field(default=10, description="Minimum text length")
        max_text_length: int = Field(default=10000, description="Maximum text length")
        language_detection_threshold: float = Field(
            default=0.7, description="Language detection confidence threshold"
        )

        class Config:
            env_prefix = "BILINGUAL_DATA_"

    class APIConfig(BaseSettings):
        """Configuration for API and serving."""

        # Server settings
        host: str = Field(default="localhost", description="Server host")
        port: int = Field(default=8000, description="Server port")
        workers: int = Field(default=1, description="Number of workers")

        # API settings
        api_title: str = Field(default="Bilingual API", description="API title")
        api_description: str = Field(default="Bilingual NLP API", description="API description")
        api_version: str = Field(default="1.0.0", description="API version")

        # Rate limiting
        rate_limit_per_minute: int = Field(default=60, description="Requests per minute limit")

        class Config:
            env_prefix = "BILINGUAL_API_"

    class EvaluationConfig(BaseSettings):
        """Configuration for evaluation and metrics."""

        # Evaluation settings
        bleu_ngram_order: int = Field(default=4, description="BLEU n-gram order")
        rouge_types: List[str] = Field(
            default=["rouge-1", "rouge-2", "rouge-l"], description="ROUGE types"
        )
        meteor_alpha: float = Field(default=0.9, description="METEOR alpha parameter")

        # Benchmark settings
        benchmark_runs: int = Field(default=100, description="Number of benchmark runs")
        benchmark_warmup: int = Field(default=10, description="Warmup runs for benchmarking")

        class Config:
            env_prefix = "BILINGUAL_EVAL_"

    class Settings(BaseSettings):
        """Main application settings combining all configurations."""

        # Core settings
        debug: bool = Field(default=False, description="Debug mode")
        log_level: str = Field(default="INFO", description="Logging level")

        # Component configurations
        model: ModelConfig = Field(default_factory=ModelConfig)
        data: DataConfig = Field(default_factory=DataConfig)
        api: APIConfig = Field(default_factory=APIConfig)
        evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False

        def save_to_file(self, file_path: str = ".bilingual_config.json") -> None:
            """Save current settings to a JSON file."""
            config_data = {
                "debug": self.debug,
                "log_level": self.log_level,
                "model": self.model.dict(),
                "data": self.data.dict(),
                "api": self.api.dict(),
                "evaluation": self.evaluation.dict(),
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Configuration saved to: {file_path}")

        @classmethod
        def load_from_file(cls, file_path: str = ".bilingual_config.json") -> "Settings":
            """Load settings from a JSON file."""
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                return cls(
                    debug=config_data.get("debug", False),
                    log_level=config_data.get("log_level", "INFO"),
                    model=ModelConfig(**config_data.get("model", {})),
                    data=DataConfig(**config_data.get("data", {})),
                    api=APIConfig(**config_data.get("api", {})),
                    evaluation=EvaluationConfig(**config_data.get("evaluation", {})),
                )
            except FileNotFoundError:
                print(f"⚠️  Configuration file not found: {file_path}")
                return cls()

    # Global settings instance
    _settings = None

    def get_settings() -> Settings:
        """Get or create the global settings instance."""
        global _settings
        if _settings is None:
            # Try to load from file first
            config_file = Path(".bilingual_config.json")
            if config_file.exists():
                _settings = Settings.load_from_file(str(config_file))
            else:
                _settings = Settings()
        return _settings

    def init_settings(debug: bool = False, log_level: str = "INFO", **kwargs) -> Settings:
        """Initialize settings with custom values."""
        global _settings
        _settings = Settings(debug=debug, log_level=log_level, **kwargs)
        return _settings

else:
    # Fallback when pydantic is not available
    class Settings:
        """Basic settings fallback."""

        def __init__(self):
            self.debug = False
            self.log_level = "INFO"
            self.model = type(
                "ModelConfig",
                (),
                {
                    "default_model": "t5-small",
                    "model_cache_dir": "models/cache",
                    "tokenizer_path": "models/tokenizer/bilingual_sp.model",
                },
            )()
            self.data = type(
                "DataConfig",
                (),
                {"raw_data_dir": "data/raw", "processed_data_dir": "datasets/processed"},
            )()
            self.api = type("APIConfig", (), {"host": "localhost", "port": 8000})()
            self.evaluation = type("EvaluationConfig", (), {"bleu_ngram_order": 4})()

    def get_settings() -> Settings:
        """Get settings instance."""
        return Settings()
