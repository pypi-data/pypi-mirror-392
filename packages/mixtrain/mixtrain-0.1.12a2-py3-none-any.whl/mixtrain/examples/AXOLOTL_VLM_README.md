# Axolotl VLM Fine-tuning Workflow

This workflow enables fine-tuning of Vision-Language Models (VLMs) using the Axolotl framework on the mixtrain platform.

## Overview

The `AxolotlVLMFinetune` workflow supports fine-tuning popular VLM architectures including:
- **LLaVA** (Large Language and Vision Assistant)
- **Qwen-VL** (Qwen Vision Language)
- **Phi-3-Vision**
- Other Axolotl-supported VLM architectures

## Features

- ✅ **Dataset Integration**: Seamlessly uses mixtrain datasets
- ✅ **LoRA Fine-tuning**: Efficient parameter-efficient fine-tuning with LoRA
- ✅ **GPU Acceleration**: Optimized for A100 GPUs with FlashAttention-2
- ✅ **DeepSpeed Support**: Optional DeepSpeed ZeRO optimization (stages 2 and 3)
- ✅ **Model Registration**: Automatically registers fine-tuned models in mixtrain
- ✅ **Persistent Storage**: Uses `/data` for shared workspace storage
- ✅ **W&B Integration**: Optional Weights & Biases logging

## Dataset Format

Your mixtrain dataset should be in tabular format (CSV, Parquet, or Iceberg table) with the following columns:

### Required Columns

| Column Name | Description | Example |
|-------------|-------------|---------|
| `image_path` | Path or URL to the image | `/data/images/img001.jpg` or `https://...` |
| `prompt` | Instruction or question | "What is in this image?" |
| `response` | Expected model response | "A cat sitting on a windowsill" |

### Example Dataset Structure

```csv
image_path,prompt,response
/data/images/cat.jpg,"Describe this image","A fluffy orange cat sitting on a windowsill looking outside"
/data/images/dog.jpg,"What animal is this?","This is a golden retriever dog playing in a park"
/data/images/car.jpg,"What color is the vehicle?","The vehicle is red"
```

### Advanced: Custom Column Names

You can customize column names using workflow parameters:
- `image_column`: Name of your image path column (default: `image_path`)
- `prompt_column`: Name of your prompt column (default: `prompt`)
- `response_column`: Name of your response column (default: `response`)

## Quick Start

### 1. Prepare Your Dataset

First, upload your dataset to mixtrain:

```bash
# Upload a CSV file as a dataset
mixtrain dataset create my-vlm-data --file training_data.csv

# Or use an existing dataset
mixtrain dataset list
```

### 2. Create the Workflow

```bash
cd mixtrain/src/mixtrain/examples
mixtrain workflow create axolotl_vlm_finetune.py \
  --name vlm-finetune \
  --description "Fine-tune VLMs with Axolotl"
```

### 3. Run Fine-tuning

#### Basic Example (LLaVA 1.5 7B)

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-vlm-data \
  --output_model_name my-finetuned-llava \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 3 \
  --batch_size 2
```

#### Advanced Example (with DeepSpeed and W&B)

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-vlm-data \
  --output_model_name my-finetuned-llava \
  --base_model llava-hf/llava-1.5-7b-hf \
  --model_type llava \
  --num_epochs 5 \
  --batch_size 4 \
  --learning_rate 0.00002 \
  --gradient_accumulation_steps 8 \
  --lora_r 128 \
  --lora_alpha 32 \
  --deepspeed_config zero2 \
  --wandb_project my-vlm-experiments \
  --use_flash_attention true
```

## Parameters

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_name` | str | **required** | Name of mixtrain dataset |
| `output_model_name` | str | **required** | Name for fine-tuned model |
| `base_model` | str | `llava-hf/llava-1.5-7b-hf` | HuggingFace model ID |
| `model_type` | str | `llava` | Architecture: `llava`, `qwen2_vl`, `phi3_v` |

### Training Hyperparameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_epochs` | int | `3` | Number of training epochs |
| `batch_size` | int | `2` | Batch size per GPU |
| `learning_rate` | float | `2e-5` | Learning rate |
| `gradient_accumulation_steps` | int | `4` | Gradient accumulation |
| `max_seq_length` | int | `2048` | Maximum sequence length |

### LoRA Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lora_r` | int | `64` | LoRA rank (higher = more capacity) |
| `lora_alpha` | int | `16` | LoRA scaling factor |
| `lora_dropout` | float | `0.05` | LoRA dropout rate |

### Advanced Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_flash_attention` | bool | `true` | Use FlashAttention-2 |
| `deepspeed_config` | str | `""` | DeepSpeed stage: `zero2`, `zero3`, or empty |
| `wandb_project` | str | `""` | W&B project name (optional) |

### Dataset Column Mapping

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_column` | str | `image_path` | Column with image paths |
| `prompt_column` | str | `prompt` | Column with prompts |
| `response_column` | str | `response` | Column with responses |

## Supported Models

### LLaVA Models

```bash
# LLaVA 1.5 7B
--base_model llava-hf/llava-1.5-7b-hf --model_type llava

# LLaVA 1.5 13B
--base_model llava-hf/llava-1.5-13b-hf --model_type llava

# LLaVA 1.6 (Next)
--base_model llava-hf/llava-v1.6-mistral-7b-hf --model_type llava
```

### Qwen-VL Models

```bash
# Qwen2-VL 2B
--base_model Qwen/Qwen2-VL-2B-Instruct --model_type qwen2_vl

# Qwen2-VL 7B
--base_model Qwen/Qwen2-VL-7B-Instruct --model_type qwen2_vl
```

### Phi-3-Vision

```bash
# Phi-3-Vision 128K
--base_model microsoft/Phi-3-vision-128k-instruct --model_type phi3_v
```

## Resource Requirements

| GPU | Memory | Batch Size | Model Size | Notes |
|-----|--------|------------|------------|-------|
| A100 40GB | 40GB | 2-4 | 7B | Recommended for most use cases |
| A100 80GB | 80GB | 4-8 | 7B-13B | For larger batches or models |
| A10G | 24GB | 1-2 | 7B | Budget option (slower) |

The workflow is configured for A100 80GB by default:
```python
_mixflow_gpu = "a100"
_mixflow_memory = 81920  # 80GB
```

## Single-GPU vs Multi-Node Training

The workflow **automatically detects** your environment and adapts:

### Single-GPU Mode (Default)
When running on a single GPU (no distributed environment variables set):
```
🖥️  Single GPU mode - running without distributed setup
```
- No distributed coordination needed
- Runs directly via `python -m axolotl.cli.train`
- Perfect for development and smaller models

### Multi-Node/Multi-GPU Mode
When distributed environment variables are set:
```
🌐 Detected distributed environment - using accelerate launch
  MASTER_ADDR: 192.168.1.100
  RANK: 0
  WORLD_SIZE: 4
  LOCAL_RANK: 0
```
- Uses `accelerate launch` for distributed training
- Automatically coordinates across nodes
- Scales to multiple GPUs/nodes

**Environment Variables for Multi-Node**:
- `MASTER_ADDR` - Address of the master node
- `MASTER_PORT` - Port for communication (default: 29500)
- `RANK` - Global rank of this process
- `WORLD_SIZE` - Total number of processes
- `LOCAL_RANK` - Local rank on this node

## Output

### Model Files

The fine-tuned model is saved to `/data/axolotl_workspace/output/` and includes:
- **Adapter weights** (LoRA): `adapter_model.bin`, `adapter_config.json`
- **Tokenizer**: `tokenizer.json`, `tokenizer_config.json`
- **Training logs**: `trainer_state.json`
- **Model config**: `config.json`

### Model Registration

The workflow automatically registers the model in mixtrain, making it available for:
- Inference via mixtrain API
- Model versioning and tracking
- Sharing within your workspace

## Monitoring

### Workflow Logs

Monitor training progress:

```bash
# View workflow runs
mixtrain workflow runs vlm-finetune

# Get specific run details
mixtrain workflow get vlm-finetune
```

### Weights & Biases Integration

Enable W&B logging:

```bash
# Set W&B API key as secret
mixtrain secret create WANDB_API_KEY your_wandb_key

# Run with W&B logging
mixtrain workflow run vlm-finetune \
  --dataset_name my-data \
  --output_model_name my-model \
  --wandb_project my-experiments
```

## Troubleshooting

### Out of Memory (OOM) Errors

1. **Reduce batch size**: `--batch_size 1`
2. **Enable DeepSpeed ZeRO-3**: `--deepspeed_config zero3`
3. **Reduce sequence length**: `--max_seq_length 1024`
4. **Reduce LoRA rank**: `--lora_r 32`

### Slow Training

1. **Enable FlashAttention**: `--use_flash_attention true` (default)
2. **Increase batch size with gradient accumulation**:
   ```bash
   --batch_size 1 --gradient_accumulation_steps 16
   ```
3. **Use DeepSpeed ZeRO-2**: `--deepspeed_config zero2`

### Dataset Format Issues

Ensure your dataset has the correct columns:

```python
# Check your dataset structure
import mixtrain
df = mixtrain.MixClient().get_dataset("my-data").scan().to_pandas()
print(df.columns)
print(df.head())
```

### Image Loading Errors

- Verify image paths are accessible from `/data`
- Use absolute paths: `/data/images/img.jpg`
- Or use URLs: `https://example.com/image.jpg`

## Example: Complete Workflow

```bash
# 1. Create dataset from CSV
cat > training_data.csv << EOF
image_path,prompt,response
/data/vlm/cat1.jpg,"What animal is this?","This is a domestic cat"
/data/vlm/dog1.jpg,"Describe the scene","A dog playing fetch in a park"
EOF

mixtrain dataset create vlm-training-data --file training_data.csv

# 2. Create workflow
mixtrain workflow create axolotl_vlm_finetune.py --name vlm-finetune

# 3. Run fine-tuning
mixtrain workflow run vlm-finetune \
  --dataset_name vlm-training-data \
  --output_model_name my-custom-llava \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 3 \
  --batch_size 2 \
  --learning_rate 2e-5

# 4. Monitor progress
mixtrain workflow runs vlm-finetune

# 5. Use the fine-tuned model
mixtrain model get my-custom-llava
mixtrain model run my-custom-llava \
  --inputs '{"image": "/data/test.jpg", "prompt": "What is in this image?"}'
```

## Best Practices

1. **Start Small**: Test with a small dataset subset first
2. **Monitor Training**: Use W&B or check logs regularly
3. **Hyperparameter Tuning**: Start with defaults, then experiment
4. **Data Quality**: Ensure high-quality image-text pairs
5. **Resource Planning**: Allocate sufficient time (4+ hours for full training)

## Additional Resources

- [Axolotl Documentation](https://github.com/OpenAccess-AI-Collective/axolotl)
- [LLaVA Paper](https://arxiv.org/abs/2304.08485)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Mixtrain Documentation](https://docs.mixtrain.ai)

## Support

For issues or questions:
- Check workflow logs: `mixtrain workflow runs vlm-finetune`
- Review model status: `mixtrain model get <model-name>`
- Contact support: support@mixtrain.ai
