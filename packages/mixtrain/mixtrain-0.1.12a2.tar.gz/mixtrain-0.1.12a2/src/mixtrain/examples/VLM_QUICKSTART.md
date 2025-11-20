# VLM Fine-tuning Quick Start Guide

Get started with Vision-Language Model fine-tuning in under 5 minutes!

## Prerequisites

- Mixtrain CLI installed and authenticated (`mixtrain login`)
- Active workspace
- GPU quota available (A100 recommended)

## Step 1: Test with Sample Dataset (Fastest)

Use our provided sample dataset to quickly test the workflow:

```bash
# Navigate to examples directory
cd mixtrain/src/mixtrain/examples

# Upload sample dataset
mixtrain dataset create sample-vlm-data --file sample_vlm_dataset.csv

# Create the workflow
mixtrain workflow create axolotl_vlm_finetune.py \
  --name vlm-finetune \
  --description "Fine-tune VLMs with Axolotl"

# Run a quick test (2 epochs, small batch)
mixtrain workflow run vlm-finetune \
  --dataset_name sample-vlm-data \
  --output_model_name test-llava-model \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 2 \
  --batch_size 1 \
  --learning_rate 0.00002
```

This will take approximately 1-2 hours on an A100 GPU.

## Step 2: Prepare Your Own Dataset

### Option A: CSV Format (Easiest)

Create a CSV file with three columns:

```csv
image_path,prompt,response
/data/images/cat.jpg,"What animal is this?","A cat"
/data/images/dog.jpg,"Describe this image","A dog playing in a park"
```

Upload to mixtrain:

```bash
mixtrain dataset create my-vlm-data --file my_data.csv
```

### Option B: Convert Existing Data

Use the preparation script to convert from various formats:

```bash
# From JSONL (LLaVA format)
python prepare_vlm_dataset.py \
  --format jsonl \
  --input-file llava_data.jsonl \
  --output converted_data.csv

# From HuggingFace dataset
python prepare_vlm_dataset.py \
  --format huggingface \
  --hf-dataset liuhaotian/LLaVA-Instruct-150K \
  --hf-split train \
  --output converted_data.csv

# Upload to mixtrain
mixtrain dataset create my-vlm-data --file converted_data.csv
```

### Option C: Directory Structure

If you have images and text files:

```bash
# Structure:
# images/
#   ├── img001.jpg
#   ├── img002.jpg
# texts/
#   ├── img001.txt  (line 1: prompt, line 2: response)
#   ├── img002.txt

python prepare_vlm_dataset.py \
  --format directory \
  --image-dir images/ \
  --text-dir texts/ \
  --output dataset.csv

mixtrain dataset create my-vlm-data --file dataset.csv
```

## Step 3: Run Fine-tuning

### Basic Fine-tuning

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-vlm-data \
  --output_model_name my-custom-llava \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 3 \
  --batch_size 2
```

### Production Fine-tuning (Recommended)

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-vlm-data \
  --output_model_name my-custom-llava-v1 \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 5 \
  --batch_size 4 \
  --gradient_accumulation_steps 8 \
  --learning_rate 0.00002 \
  --lora_r 128 \
  --lora_alpha 32 \
  --deepspeed_config zero2 \
  --use_flash_attention true
```

## Step 4: Monitor Progress

```bash
# List all workflow runs
mixtrain workflow runs vlm-finetune

# Get detailed workflow info
mixtrain workflow get vlm-finetune

# Check model status (after completion)
mixtrain model get my-custom-llava
```

## Step 5: Use Your Fine-tuned Model

Once training completes, your model is automatically registered:

```bash
# List your models
mixtrain model list

# Get model details
mixtrain model get my-custom-llava

# Run inference (if inference endpoint configured)
mixtrain model run my-custom-llava \
  --inputs '{"image": "/data/test.jpg", "prompt": "What is in this image?"}'
```

## Common Configurations

### Memory-Constrained (24GB GPU)

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-data \
  --output_model_name my-model \
  --batch_size 1 \
  --gradient_accumulation_steps 16 \
  --deepspeed_config zero3 \
  --max_seq_length 1024 \
  --lora_r 32
```

### Fast Training (Small Dataset)

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-data \
  --output_model_name my-model \
  --num_epochs 2 \
  --batch_size 4 \
  --gradient_accumulation_steps 2 \
  --use_flash_attention true
```

### High Quality (Large Dataset)

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-data \
  --output_model_name my-model \
  --num_epochs 10 \
  --batch_size 4 \
  --gradient_accumulation_steps 4 \
  --learning_rate 0.00001 \
  --lora_r 256 \
  --lora_alpha 64 \
  --deepspeed_config zero2 \
  --wandb_project my-experiments
```

## Different Model Architectures

### LLaVA 1.5 7B (Default)

```bash
--base_model llava-hf/llava-1.5-7b-hf --model_type llava
```

### LLaVA 1.5 13B (More Capable)

```bash
--base_model llava-hf/llava-1.5-13b-hf --model_type llava
```

### Qwen2-VL 7B (Latest)

```bash
--base_model Qwen/Qwen2-VL-7B-Instruct --model_type qwen2_vl
```

### Phi-3-Vision (Efficient)

```bash
--base_model microsoft/Phi-3-vision-128k-instruct --model_type phi3_v
```

## Troubleshooting

### "Out of Memory" Error

**Solution 1**: Reduce batch size
```bash
--batch_size 1 --gradient_accumulation_steps 16
```

**Solution 2**: Enable DeepSpeed ZeRO-3
```bash
--deepspeed_config zero3
```

**Solution 3**: Reduce model capacity
```bash
--lora_r 32 --max_seq_length 1024
```

### Training Too Slow

**Solution**: Enable optimizations
```bash
--use_flash_attention true --deepspeed_config zero2
```

### Dataset Loading Error

**Check dataset format**:
```bash
# Validate your dataset
python prepare_vlm_dataset.py \
  --format csv \
  --output your_dataset.csv \
  --validate-only
```

### Workflow Not Starting

**Check GPU availability**:
```bash
# View workspace resources
mixtrain workspace get

# List running workflows
mixtrain workflow runs vlm-finetune
```

## Best Practices

1. **Start Small**: Test with sample dataset first
2. **Validate Data**: Use `prepare_vlm_dataset.py --validate-only`
3. **Monitor Resources**: Check GPU memory usage
4. **Save Checkpoints**: Training saves checkpoints every epoch
5. **Use W&B**: Enable logging with `--wandb_project`
6. **Test Incrementally**: Start with 1-2 epochs, then scale up

## Time & Cost Estimates

| Dataset Size | Epochs | GPU | Time | Cost (est.) |
|--------------|--------|-----|------|-------------|
| 100 samples  | 3      | A100| 30m  | $1-2        |
| 1,000 samples| 3      | A100| 2h   | $8-12       |
| 10,000 samples| 3     | A100| 12h  | $50-70      |
| 50,000 samples| 5     | A100| 48h  | $200-300    |

*Estimates based on LLaVA 1.5 7B with default settings*

## Next Steps

- Read the [full documentation](AXOLOTL_VLM_README.md)
- Explore [Axolotl documentation](https://github.com/OpenAccess-AI-Collective/axolotl)
- Join our community Discord
- Share your fine-tuned models!

## Support

Need help?
- Check logs: `mixtrain workflow runs vlm-finetune`
- Documentation: [AXOLOTL_VLM_README.md](AXOLOTL_VLM_README.md)
- Email: support@mixtrain.ai
- Discord: [Join our community](https://discord.gg/mixtrain)

---

**Happy Fine-tuning! 🚀**
