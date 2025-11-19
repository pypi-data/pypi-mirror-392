"""
Parallel-LLM: Ultra-Fast Parallel Training and Inference for Language Models

A production-ready library for training and inference of language models with
revolutionary parallel token generation using hybrid diffusion-energy architecture.
"""

__version__ = "0.1.0"

# Configuration classes
from .config import (
    ModelConfig,
    MultimodalConfig,
    TrainingConfig,
    InferenceConfig,
    get_default_config,
)

# Core models
from .diffusion_transformer import DiffusionTransformer

# Training
from .trainer import DistributedTrainer

# Inference
from .parallel_generator import (
    ParallelGenerator,
    GenerationConfig,
    create_generator,
)

__all__ = [
    # Version
    "__version__",

    # Configuration
    "ModelConfig",
    "MultimodalConfig",
    "TrainingConfig",
    "InferenceConfig",
    "get_default_config",

    # Core models
    "DiffusionTransformer",

    # Training
    "DistributedTrainer",

    # Inference
    "ParallelGenerator",
    "GenerationConfig",
    "create_generator",
]
