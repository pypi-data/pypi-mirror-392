"""Fine-tune Vision-Language Models using Axolotl framework.

This workflow fine-tunes VLMs like LLaVA, Qwen-VL, etc. using the Axolotl framework.
It takes a mixtrain dataset, processes it, runs fine-tuning, and registers the
resulting model back to mixtrain.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from mixtrain import MixClient, MixFlow, mixparam


def install_package(packages):
    """Install Python packages using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
        print(f"Successfully installed {packages}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing {packages}: {e}")
        raise


mix = MixClient()


class AxolotlVLMFinetune(MixFlow):
    """Fine-tune Vision-Language Models using Axolotl framework.

    This workflow supports fine-tuning VLMs like LLaVA, Qwen-VL, Phi-3-Vision, etc.
    It takes a mixtrain dataset containing images and text prompts, converts it to
    the format expected by Axolotl, runs training, and registers the fine-tuned
    model back to mixtrain.

    Dataset format expectations:
        The input dataset should contain columns for:
        - image_path or image_url: Path/URL to images
        - prompt/instruction: Text prompt/instruction
        - response/output: Expected response (for supervised fine-tuning)
        - conversation: Optional full conversation in JSON format

    Args:
        dataset_name: Name of the mixtrain dataset containing training data
        output_model_name: Name for the fine-tuned model in mixtrain
        base_model: Base VLM model to fine-tune (e.g., "llava-hf/llava-1.5-7b-hf")
        model_type: Type of VLM architecture (e.g., "llava", "qwen2_vl", "phi3_v")
        num_epochs: Number of training epochs (default: 3)
        batch_size: Training batch size per device (default: 2)
        learning_rate: Learning rate for training (default: 2e-5)
        gradient_accumulation_steps: Gradient accumulation steps (default: 4)
        max_seq_length: Maximum sequence length (default: 2048)
        lora_r: LoRA rank (default: 64)
        lora_alpha: LoRA alpha (default: 16)
        lora_dropout: LoRA dropout (default: 0.05)
        use_flash_attention: Use FlashAttention-2 for faster training (default: True)
        deepspeed_config: Optional DeepSpeed configuration stage (e.g., "zero2", "zero3")
        wandb_project: Optional W&B project name for logging
        image_column: Column name containing image paths (default: "image_path")
        prompt_column: Column name containing prompts (default: "prompt")
        response_column: Column name containing responses (default: "response")
    """

    # Sandbox configuration - GPU required for VLM training
    _mixflow_image = "axolotlai/axolotl:main-latest"
    _mixflow_gpu = "a100"  # A100 recommended for VLM fine-tuning
    _mixflow_memory = 81920  # 80GB memory
    _mixflow_timeout = 14400  # 4 hours max
    _mixflow_cpu = 8.0

    # Dataset and model parameters
    dataset_name: str = mixparam(description="Name of the mixtrain input dataset")
    output_model_name: str = mixparam(
        description="Name for the fine-tuned model in mixtrain"
    )

    # Base model configuration
    base_model: str = mixparam(
        default="llava-hf/llava-1.5-7b-hf",
        description="Base VLM model to fine-tune (HuggingFace model ID)",
    )
    model_type: str = mixparam(
        default="llava", description="VLM architecture type (llava, qwen2_vl, phi3_v)"
    )

    # Training hyperparameters
    num_epochs: int = mixparam(default=3, description="Number of training epochs")
    batch_size: int = mixparam(
        default=2, description="Training batch size per device"
    )
    learning_rate: float = mixparam(
        default=2e-5, description="Learning rate for training"
    )
    gradient_accumulation_steps: int = mixparam(
        default=4, description="Gradient accumulation steps"
    )
    max_seq_length: int = mixparam(
        default=2048, description="Maximum sequence length"
    )

    # LoRA configuration
    lora_r: int = mixparam(default=64, description="LoRA rank")
    lora_alpha: int = mixparam(default=16, description="LoRA alpha")
    lora_dropout: float = mixparam(default=0.05, description="LoRA dropout")

    # Advanced options
    use_flash_attention: bool = mixparam(
        default=True, description="Use FlashAttention-2 for faster training"
    )
    deepspeed_config: str = mixparam(
        default="", description="DeepSpeed config stage (zero2, zero3, or empty)"
    )
    wandb_project: str = mixparam(
        default="", description="Weights & Biases project name (optional)"
    )

    # Dataset column mappings
    image_column: str = mixparam(
        default="image_path", description="Column name containing image paths"
    )
    prompt_column: str = mixparam(
        default="prompt", description="Column name containing prompts"
    )
    response_column: str = mixparam(
        default="response", description="Column name containing responses"
    )

    def __init__(self):
        super().__init__()
        self.work_dir = "."
        self.output_dir = None
        self.config_path = None

    def setup(self, run_config: dict[str, Any]):
        """Initialize the workflow with configuration."""
        print("=" * 80)
        print("Setting up Axolotl VLM Fine-tuning Workflow")
        print("=" * 80)

        # Set attributes from run config
        for key, value in run_config.items():
            setattr(self, key, value)

        print(f"\nBase model: {self.base_model}")
        print(f"Model type: {self.model_type}")
        print(f"Dataset: {self.dataset_name}")
        print(f"Output model: {self.output_model_name}")

        # Create workspace directory
        os.makedirs(self.work_dir, exist_ok=True)
        self.output_dir = os.path.join(self.work_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"\nWorkspace directory: {self.work_dir}")
        print(f"Output directory: {self.output_dir}")

        # Install Axolotl and dependencies
        print("\nInstalling Axolotl and dependencies...")
        install_package(
            [
                # "axolotl[flash-attn,deepspeed]",
                "transformers>=4.40.0",
                "peft>=0.10.0",
                "bitsandbytes>=0.43.0",
                "pillow",
                "pyarrow",
            ]
        )

        print("\n" + "=" * 80)
        print("Setup completed successfully!")
        print("=" * 80 + "\n")

    def _load_and_prepare_dataset(self) -> str:
        """Load mixtrain dataset and convert to Axolotl format."""
        print("\n" + "=" * 80)
        print("Loading and preparing dataset...")
        print("=" * 80 + "\n")

        # Load dataset from mixtrain
        print(f"Loading dataset: {self.dataset_name}")
        dataset = mix.get_dataset(self.dataset_name)
        df = dataset.scan().to_pandas()
        print(f"Loaded {len(df)} rows")

        # Validate required columns
        required_cols = [self.image_column, self.prompt_column, self.response_column]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {df.columns.tolist()}"
            )

        # Convert to Axolotl format (JSON Lines)
        # Format: {"image": "path/to/image.jpg", "conversations": [...]}
        axolotl_data = []
        for _, row in df.iterrows():
            conversations = [
                {"from": "human", "value": f"<image>\n{row[self.prompt_column]}"},
                {"from": "gpt", "value": row[self.response_column]},
            ]

            axolotl_data.append(
                {"image": row[self.image_column], "conversations": conversations}
            )

        # Save to JSON Lines format
        dataset_path = os.path.join(self.work_dir, "train_data.jsonl")
        with open(dataset_path, "w") as f:
            for item in axolotl_data:
                f.write(json.dumps(item) + "\n")

        print(f"Prepared dataset saved to: {dataset_path}")
        print(f"Total samples: {len(axolotl_data)}")

        # Show sample for verification
        if axolotl_data:
            print("\n" + "-" * 80)
            print("Sample training example:")
            print("-" * 80)
            print(json.dumps(axolotl_data[0], indent=2))
            print("-" * 80 + "\n")

        return dataset_path

    def _create_axolotl_config(self, dataset_path: str) -> str:
        """Create Axolotl configuration file."""
        print("\n" + "=" * 80)
        print("Creating Axolotl configuration...")
        print("=" * 80 + "\n")

        config = {
            # Base model configuration
            "base_model": self.base_model,
            "model_type": self.model_type,
            "trust_remote_code": True,
            # Explicitly prevent tokenizer_type from being set to model path
            "tokenizer_type": "AutoTokenizer",
            # Dataset configuration
            "datasets": [
                {
                    "path": dataset_path,
                    "type": "chat_template",
                    "field_messages": "conversations",
                    "message_field_role": "from",
                    "message_field_content": "value",
                }
            ],
            # Output configuration
            "output_dir": self.output_dir,
            # Training hyperparameters
            "num_epochs": self.num_epochs,
            "micro_batch_size": self.batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "learning_rate": self.learning_rate,
            "lr_scheduler": "cosine",
            "warmup_steps": 10,
            "sequence_len": self.max_seq_length,
            # LoRA configuration
            "adapter": "lora",
            "lora_r": self.lora_r,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
            "lora_target_linear": True,
            # Optimization settings
            "optimizer": "adamw_torch",
            "weight_decay": 0.01,
            "max_grad_norm": 1.0,
            # Logging and saving
            "logging_steps": 1,
            "save_strategy": "epoch",
            "save_total_limit": 3,
            # Advanced features
            "flash_attention": self.use_flash_attention,
            "bf16": True,
            "tf32": True,
            "gradient_checkpointing": True,
        }

        # Add DeepSpeed configuration if specified
        if self.deepspeed_config:
            deepspeed_configs = {
                "zero2": {
                    "zero_optimization": {
                        "stage": 2,
                        "offload_optimizer": {"device": "cpu", "pin_memory": True},
                        "allgather_partitions": True,
                        "allgather_bucket_size": 2e8,
                        "reduce_scatter": True,
                        "reduce_bucket_size": 2e8,
                        "overlap_comm": True,
                        "contiguous_gradients": True,
                    }
                },
                "zero3": {
                    "zero_optimization": {
                        "stage": 3,
                        "offload_optimizer": {"device": "cpu", "pin_memory": True},
                        "offload_param": {"device": "cpu", "pin_memory": True},
                        "overlap_comm": True,
                        "contiguous_gradients": True,
                        "sub_group_size": 1e9,
                        "reduce_bucket_size": "auto",
                        "stage3_prefetch_bucket_size": "auto",
                        "stage3_param_persistence_threshold": "auto",
                        "stage3_max_live_parameters": 1e9,
                        "stage3_max_reuse_distance": 1e9,
                        "stage3_gather_16bit_weights_on_model_save": True,
                    }
                },
            }
            if self.deepspeed_config in deepspeed_configs:
                config["deepspeed"] = deepspeed_configs[self.deepspeed_config]

        # Add Weights & Biases logging if configured
        if self.wandb_project:
            config["wandb_project"] = self.wandb_project
            config["wandb_watch"] = "gradients"
            config["wandb_log_model"] = "checkpoint"

        # Save configuration
        self.config_path = os.path.join(self.work_dir, "axolotl_config.yml")
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        print(f"Axolotl config saved to: {self.config_path}")
        print("\nConfiguration summary:")
        print(f"  - Base model: {self.base_model}")
        print(f"  - Model type: {self.model_type}")
        print(f"  - Epochs: {self.num_epochs}")
        print(f"  - Batch size: {self.batch_size}")
        print(f"  - Learning rate: {self.learning_rate}")
        print(f"  - LoRA rank: {self.lora_r}")
        print(f"  - Max sequence length: {self.max_seq_length}")
        if self.deepspeed_config:
            print(f"  - DeepSpeed: {self.deepspeed_config}")

        # Print full config for debugging
        print("\n" + "-" * 80)
        print("Full Axolotl Configuration:")
        print("-" * 80)
        print(yaml.dump(config, default_flow_style=False))
        print("-" * 80 + "\n")

        return self.config_path

    def _run_training(self, config_path: str):
        """Run Axolotl training."""
        print("\n" + "=" * 80)
        print("Starting Axolotl Training...")
        print("=" * 80 + "\n")

        # Detect if running in distributed/multi-node environment
        is_distributed = "MASTER_ADDR" in os.environ

        # Prepare environment
        env = os.environ.copy()

        if is_distributed:
            # Multi-node/multi-GPU setup - use accelerate
            print("🌐 Detected distributed environment - using accelerate launch")
            print(f"  MASTER_ADDR: {env.get('MASTER_ADDR', 'not set')}")
            print(f"  RANK: {env.get('RANK', 'not set')}")
            print(f"  WORLD_SIZE: {env.get('WORLD_SIZE', 'not set')}")
            print(f"  LOCAL_RANK: {env.get('LOCAL_RANK', 'not set')}\n")

            cmd = [
                "accelerate",
                "launch",
                "-m",
                "axolotl.cli.train",
                config_path,
            ]
        else:
            # Single GPU setup - run directly without distributed setup
            print("🖥️  Single GPU mode - running without distributed setup\n")

            # Remove any distributed training environment variables
            # to prevent PyTorch from trying to initialize distributed
            distributed_vars = [
                "MASTER_ADDR",
                "MASTER_PORT",
                "RANK",
                "WORLD_SIZE",
                "LOCAL_RANK",
                "NODE_RANK",
                "GROUP_RANK",
                "TORCHELASTIC_RUN_ID",
            ]

            for var in distributed_vars:
                env.pop(var, None)  # Remove if exists

            print("Setting environment for single GPU:")
            print("  - Removed all distributed environment variables")
            print("  - Running in single-process mode\n")

            cmd = [
                sys.executable,
                "-m",
                "axolotl.cli.train",
                config_path,
            ]

        print(f"Training command: {' '.join(cmd)}\n")
        print("Training output:")
        print("-" * 80)

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=False,
                text=True,
                cwd=self.work_dir,
                env=env,
            )
            print("-" * 80)
            print("\nTraining completed successfully!")
        except subprocess.CalledProcessError as e:
            print("-" * 80)
            print(f"\nTraining failed with error: {e}")
            raise

    def _register_model(self):
        """Register the fine-tuned model with mixtrain."""
        print("\n" + "=" * 80)
        print("Registering model with mixtrain...")
        print("=" * 80 + "\n")

        # The fine-tuned model is in the output directory
        model_dir = self.output_dir

        # Find the checkpoint directory (usually named like 'checkpoint-xxx' or 'final-checkpoint')
        checkpoint_dirs = [
            d
            for d in os.listdir(model_dir)
            if os.path.isdir(os.path.join(model_dir, d))
        ]

        if not checkpoint_dirs:
            raise ValueError(f"No checkpoint directories found in {model_dir}")

        # Use the last checkpoint or final checkpoint
        if "final-checkpoint" in checkpoint_dirs:
            checkpoint_dir = "final-checkpoint"
        else:
            # Sort by name and take the last one (highest checkpoint number)
            checkpoint_dirs.sort()
            checkpoint_dir = checkpoint_dirs[-1]

        final_model_path = os.path.join(model_dir, checkpoint_dir)
        print(f"Using checkpoint: {checkpoint_dir}")
        print(f"Model path: {final_model_path}")

        # Register model with mixtrain
        print(f"\nRegistering model as: {self.output_model_name}")
        model_data = mix.create_model(
            name=self.output_model_name,
            file_paths=[final_model_path],
            description=f"VLM fine-tuned with Axolotl on {self.dataset_name} "
            f"(base: {self.base_model})",
        )

        print("\n" + "=" * 80)
        print("Model registered successfully!")
        print("=" * 80)
        print(f"Model name: {model_data.get('name')}")
        print(f"Model ID: {model_data.get('id')}")
        print(f"Created at: {model_data.get('created_at')}")

        return model_data

    def run(self):
        """Execute the VLM fine-tuning workflow."""
        print("\n" + "=" * 80)
        print("STARTING AXOLOTL VLM FINE-TUNING WORKFLOW")
        print("=" * 80 + "\n")

        try:
            # Step 1: Load and prepare dataset
            dataset_path = self._load_and_prepare_dataset()

            # Step 2: Create Axolotl configuration
            config_path = self._create_axolotl_config(dataset_path)

            # Step 3: Run training
            self._run_training(config_path)

            # Step 4: Register model with mixtrain
            model_data = self._register_model()

            print("\n" + "=" * 80)
            print("WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"\nFine-tuned model '{self.output_model_name}' is ready to use!")
            print(f"Model location: {self.output_dir}")
            print("\nYou can now use this model for inference in mixtrain.")
            print("=" * 80 + "\n")

        except Exception as e:
            print("\n" + "=" * 80)
            print("WORKFLOW FAILED!")
            print("=" * 80)
            print(f"Error: {str(e)}")
            raise

    def cleanup(self):
        """Clean up workflow resources."""
        print("\nCleaning up workflow resources...")
        # Keep the model files in /data for persistence
        # But we can clean up intermediate files if needed
        print("Cleanup completed. Model files preserved in /data")


# Example usage:
# To run this workflow via mixtrain CLI:
#
# 1. Create the workflow:
#    mixtrain workflow create axolotl_vlm_finetune.py --name vlm-finetune
#
# 2. Run with parameters:
#    mixtrain workflow run vlm-finetune \
#      --dataset_name my-vlm-dataset \
#      --output_model_name my-finetuned-llava \
#      --base_model llava-hf/llava-1.5-7b-hf \
#      --num_epochs 3 \
#      --batch_size 2
#
# 3. Or programmatically:
#    workflow = AxolotlVLMFinetune()
#    workflow.setup({
#        "dataset_name": "my-vlm-dataset",
#        "output_model_name": "my-finetuned-llava",
#        "base_model": "llava-hf/llava-1.5-7b-hf",
#        "num_epochs": 3,
#        "batch_size": 2,
#        "learning_rate": 2e-5,
#    })
#    workflow.run()
#    workflow.cleanup()
