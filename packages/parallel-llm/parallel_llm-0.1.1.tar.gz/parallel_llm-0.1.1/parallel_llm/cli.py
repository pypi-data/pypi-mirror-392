"""
Command-line interface for Parallel-LLM
"""
import argparse
import sys
from pathlib import Path


def train_cli():
    """Command-line interface for training"""
    parser = argparse.ArgumentParser(
        description="Train a Parallel-LLM model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Model configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to model configuration YAML file"
    )
    parser.add_argument(
        "--model-type",
        choices=["unimodal", "multimodal"],
        default="unimodal",
        help="Type of model to train"
    )
    parser.add_argument(
        "--vocab-size",
        type=int,
        default=50257,
        help="Vocabulary size"
    )
    parser.add_argument(
        "--hidden-size",
        type=int,
        default=2048,
        help="Hidden size"
    )
    parser.add_argument(
        "--num-layers",
        type=int,
        default=24,
        help="Number of layers"
    )
    parser.add_argument(
        "--num-heads",
        type=int,
        default=16,
        help="Number of attention heads"
    )

    # Training configuration
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Training batch size"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=3e-4,
        help="Learning rate"
    )
    parser.add_argument(
        "--num-train-steps",
        type=int,
        default=100000,
        help="Number of training steps"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./checkpoints",
        help="Output directory for checkpoints"
    )

    # Distributed training
    parser.add_argument(
        "--use-fsdp",
        action="store_true",
        default=True,
        help="Use FSDP for distributed training"
    )
    parser.add_argument(
        "--fsdp-sharding-strategy",
        choices=["full", "shard_grad_op", "no_shard"],
        default="full",
        help="FSDP sharding strategy"
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=1,
        help="Tensor parallel size"
    )
    parser.add_argument(
        "--pipeline-parallel-size",
        type=int,
        default=1,
        help="Pipeline parallel size"
    )

    # Performance options
    parser.add_argument(
        "--mixed-precision",
        choices=["no", "fp16", "bf16", "fp8"],
        default="bf16",
        help="Mixed precision training"
    )
    parser.add_argument(
        "--use-torch-compile",
        action="store_true",
        default=True,
        help="Use torch.compile for optimization"
    )
    parser.add_argument(
        "--gradient-checkpointing",
        action="store_true",
        default=True,
        help="Use gradient checkpointing"
    )

    # Data
    parser.add_argument(
        "--train-data",
        type=str,
        required=True,
        help="Path to training data"
    )
    parser.add_argument(
        "--eval-data",
        type=str,
        help="Path to evaluation data"
    )

    # Logging
    parser.add_argument(
        "--logging-steps",
        type=int,
        default=10,
        help="Logging frequency"
    )
    parser.add_argument(
        "--save-steps",
        type=int,
        default=5000,
        help="Checkpoint saving frequency"
    )
    parser.add_argument(
        "--use-wandb",
        action="store_true",
        default=True,
        help="Use Weights & Biases logging"
    )
    parser.add_argument(
        "--wandb-project",
        type=str,
        default="parallel-llm",
        help="Weights & Biases project name"
    )

    args = parser.parse_args()

    # Import here to avoid circular imports
    from .config import ModelConfig, TrainingConfig, get_default_config
    from .diffusion_transformer import DiffusionTransformer
    from .trainer import DistributedTrainer

    try:
        # Load or create configuration
        if args.config:
            # TODO: Load from YAML
            print(f"Loading config from {args.config}")
            model_config = get_default_config(args.model_type)
        else:
            model_config = ModelConfig(
                vocab_size=args.vocab_size,
                hidden_size=args.hidden_size,
                num_hidden_layers=args.num_layers,
                num_attention_heads=args.num_heads,
            )

        train_config = TrainingConfig(
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            num_train_steps=args.num_train_steps,
            output_dir=args.output_dir,
            use_fsdp=args.use_fsdp,
            fsdp_sharding_strategy=args.fsdp_sharding_strategy,
            tensor_parallel_size=args.tensor_parallel_size,
            pipeline_parallel_size=args.pipeline_parallel_size,
            mixed_precision=args.mixed_precision,
            use_torch_compile=args.use_torch_compile,
            gradient_checkpointing=args.gradient_checkpointing,
            logging_steps=args.logging_steps,
            save_steps=args.save_steps,
            use_wandb=args.use_wandb,
            wandb_project=args.wandb_project,
        )

        # TODO: Load actual datasets
        print(f"Loading training data from {args.train_data}")
        print(f"Loading eval data from {args.eval_data}")

        # Create model and trainer
        model = DiffusionTransformer(model_config)

        # TODO: Create actual dataloaders
        train_dataloader = None
        eval_dataloader = None

        trainer = DistributedTrainer(
            model=model,
            train_config=train_config,
            model_config=model_config,
            train_dataloader=train_dataloader,
            eval_dataloader=eval_dataloader,
        )

        # Start training
        print("Starting training...")
        trainer.train()

    except Exception as e:
        print(f"Error during training: {e}", file=sys.stderr)
        sys.exit(1)


def infer_cli():
    """Command-line interface for inference"""
    parser = argparse.ArgumentParser(
        description="Run inference with a Parallel-LLM model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to trained model checkpoint"
    )
    parser.add_argument(
        "--input-text",
        type=str,
        help="Input text for generation"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="File containing input texts (one per line)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Output file for generated text"
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
        help="Maximum number of tokens to generate"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Sampling temperature"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=50,
        help="Top-k sampling"
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Top-p sampling"
    )
    parser.add_argument(
        "--num-parallel-tokens",
        type=int,
        default=64,
        help="Number of tokens to generate in parallel"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for inference"
    )

    args = parser.parse_args()

    # Import here to avoid circular imports
    from .parallel_generator import create_generator

    try:
        if not args.input_text and not args.input_file:
            print("Error: Must provide either --input-text or --input-file", file=sys.stderr)
            sys.exit(1)

        # Load model and create generator
        print(f"Loading model from {args.model_path}")
        generator = create_generator(
            model_path=args.model_path,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            num_parallel_tokens=args.num_parallel_tokens,
            batch_size=args.batch_size,
        )

        # Prepare inputs
        if args.input_text:
            inputs = [args.input_text]
        else:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                inputs = [line.strip() for line in f if line.strip()]

        # Generate
        print(f"Generating text for {len(inputs)} input(s)...")
        outputs = generator.generate_batch(inputs)

        # Output results
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                for input_text, output_text in zip(inputs, outputs):
                    f.write(f"Input: {input_text}\n")
                    f.write(f"Output: {output_text}\n")
                    f.write("-" * 50 + "\n")
        else:
            for i, (input_text, output_text) in enumerate(zip(inputs, outputs)):
                print(f"\nInput {i+1}: {input_text}")
                print(f"Output {i+1}: {output_text}")

    except Exception as e:
        print(f"Error during inference: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Allow running as python -m parallel_llm.cli <command>
    if len(sys.argv) < 2:
        print("Usage: python -m parallel_llm.cli <train|infer> [options]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove the command from argv

    if command == "train":
        train_cli()
    elif command == "infer":
        infer_cli()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Available commands: train, infer", file=sys.stderr)
        sys.exit(1)
