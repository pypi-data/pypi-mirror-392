# Axolotl VLM Fine-tuning Troubleshooting Guide

This guide helps you diagnose and fix common issues when fine-tuning Vision-Language Models with Axolotl.

## Table of Contents

1. [Configuration Errors](#configuration-errors)
2. [Training Failures](#training-failures)
3. [Memory Issues](#memory-issues)
4. [Dataset Problems](#dataset-problems)
5. [Model Loading Issues](#model-loading-issues)
6. [Performance Problems](#performance-problems)
7. [Debugging Steps](#debugging-steps)

---

## Configuration Errors

### Error: `AttributeError: module transformers has no attribute llava-hf/llava-1.5-7b-hf`

**Cause**: The workflow was incorrectly setting `tokenizer_type` to the full model path.

**Fixed in latest version**: The tokenizer_type field is now removed from the config, allowing Axolotl to auto-detect the correct tokenizer.

**Verification**: Check your generated config file (printed during workflow execution) - it should NOT contain a `tokenizer_type` field, or it should be set to `AutoTokenizer`.

---

### Error: `KeyError: 'max_seq_length'`

**Cause**: Axolotl uses `sequence_len` instead of `max_seq_length`.

**Fixed in latest version**: The config now uses `sequence_len`.

**Manual fix** (if using older version):
```yaml
# Change this:
max_seq_length: 2048

# To this:
sequence_len: 2048
```

---

### Error: `Unknown dataset type: chat_template`

**Cause**: Incorrect dataset type for VLM training.

**Fixed in latest version**: Changed to `llava_instruct` type with `conversation: llava`.

**Verification**: Your config should have:
```yaml
datasets:
  - path: train_data.jsonl
    type: llava_instruct
    conversation: llava
```

---

## Training Failures

### Error: `ModuleNotFoundError: No module named 'axolotl'`

**Cause**: Axolotl is not installed in the environment.

**Solutions**:

1. **Verify Docker image**: Make sure you're using `axolotlai/axolotl:main-latest` (check `_mixflow_image` in workflow)

2. **Manual installation** (if not using Axolotl image):
   ```bash
   pip install axolotl[flash-attn,deepspeed]
   ```

3. **Check workflow setup**: The setup method should NOT be installing axolotl since it's in the Docker image

---

### Error: `ImportError: cannot import name 'flash_attn'`

**Cause**: FlashAttention-2 is not installed or incompatible.

**Solutions**:

1. **Disable FlashAttention**:
   ```bash
   --use_flash_attention false
   ```

2. **Check GPU compatibility**: FlashAttention requires Ampere GPUs or newer (A100, A10G, etc.)

3. **Verify installation** (in workflow container):
   ```python
   import torch
   print(torch.cuda.is_available())
   print(torch.cuda.get_device_capability())  # Should be >= (8, 0)
   ```

---

### Error: `RuntimeError: CUDA out of memory`

See [Memory Issues](#memory-issues) section below.

---

### Training hangs or doesn't start

**Diagnostic steps**:

1. **Check logs**: Look for the generated config in workflow output
2. **Verify dataset**: Check that the sample training example looks correct
3. **Test with minimal config**:
   ```bash
   --num_epochs 1 \
   --batch_size 1 \
   --max_seq_length 512
   ```

4. **Check GPU availability**:
   ```python
   import torch
   print(torch.cuda.is_available())
   print(torch.cuda.device_count())
   ```

---

## Memory Issues

### CUDA Out of Memory (OOM)

**Symptoms**:
- `RuntimeError: CUDA out of memory`
- Training crashes during forward/backward pass
- `torch.cuda.OutOfMemoryError`

**Solutions** (try in order):

#### 1. Reduce Batch Size
```bash
--batch_size 1 \
--gradient_accumulation_steps 16
```
This maintains effective batch size while reducing memory.

#### 2. Enable DeepSpeed ZeRO-3
```bash
--deepspeed_config zero3
```
Most aggressive memory optimization, offloads to CPU.

#### 3. Reduce Sequence Length
```bash
--max_seq_length 1024
```
Shorter sequences use less memory.

#### 4. Reduce LoRA Rank
```bash
--lora_r 32 \
--lora_alpha 16
```
Lower rank = less parameters = less memory.

#### 5. Use Smaller Model
```bash
# Instead of 13B:
--base_model llava-hf/llava-1.5-7b-hf

# Or even smaller:
--base_model microsoft/Phi-3-vision-128k-instruct
```

#### 6. Disable Gradient Checkpointing (counterintuitive)
Sometimes disabling can help if causing issues:
```yaml
# In config:
gradient_checkpointing: false
```

#### Memory-Optimized Configuration
```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-data \
  --output_model_name my-model \
  --batch_size 1 \
  --gradient_accumulation_steps 16 \
  --max_seq_length 1024 \
  --lora_r 32 \
  --deepspeed_config zero3 \
  --use_flash_attention true
```

---

### CPU Out of Memory

**Symptoms**:
- System freezes
- `MemoryError` or `killed` messages

**Solutions**:

1. **Reduce dataset size**:
   - Use a smaller subset for testing
   - Implement data streaming instead of loading all at once

2. **Increase system memory allocation**:
   ```python
   _mixflow_memory = 163840  # 160GB instead of 80GB
   ```

3. **Disable DeepSpeed CPU offloading**:
   ```bash
   --deepspeed_config ""  # Empty = no DeepSpeed
   ```

---

## Dataset Problems

### Error: `Missing required columns`

**Cause**: Dataset doesn't have expected column names.

**Solution**: Specify correct column names:
```bash
--image_column your_image_col \
--prompt_column your_prompt_col \
--response_column your_response_col
```

**Verify your dataset**:
```python
import mixtrain
df = mixtrain.MixClient().get_dataset("my-dataset").scan().to_pandas()
print(df.columns.tolist())
print(df.head())
```

---

### Error: `FileNotFoundError` for images

**Cause**: Image paths in dataset are incorrect or inaccessible.

**Solutions**:

1. **Use absolute paths**:
   ```csv
   /data/images/img.jpg  ✓
   images/img.jpg         ✗
   ```

2. **Use URLs** (if images are remote):
   ```csv
   https://example.com/image.jpg  ✓
   ```

3. **Copy images to /data**:
   ```bash
   # Images should be in /data since it's shared storage
   /data/my_images/img001.jpg
   ```

4. **Verify image paths**:
   ```python
   import os
   df = mixtrain.MixClient().get_dataset("my-data").scan().to_pandas()
   for path in df['image_path']:
       if not path.startswith('http'):
           if not os.path.exists(path):
               print(f"Missing: {path}")
   ```

---

### Empty or malformed dataset

**Symptoms**:
- Training starts but no batches
- `len(dataset) = 0` in logs

**Diagnostic**:

Look for the "Sample training example" in workflow output:
```json
{
  "image": "/data/images/cat.jpg",
  "conversations": [
    {"from": "human", "value": "<image>\nWhat is this?"},
    {"from": "gpt", "value": "A cat"}
  ]
}
```

**Verify**:
- `image` field has valid path/URL
- `conversations` has both `human` and `gpt` entries
- Text is not empty or null

---

### Dataset format issues

**Use the validation tool**:
```bash
python prepare_vlm_dataset.py \
  --format csv \
  --output your_dataset.csv \
  --validate-only
```

**Check sample conversions**:
```bash
# Test conversion
python prepare_vlm_dataset.py \
  --format csv \
  --input-file test_sample.csv \
  --output converted.csv

# Upload small test dataset
mixtrain dataset create test-vlm --file converted.csv

# Run with test data
mixtrain workflow run vlm-finetune \
  --dataset_name test-vlm \
  --output_model_name test-model \
  --num_epochs 1
```

---

## Model Loading Issues

### Error: `OSError: Model not found`

**Cause**: HuggingFace model ID is incorrect or model requires authentication.

**Solutions**:

1. **Verify model ID exists**:
   - Check on https://huggingface.co/
   - Example valid IDs:
     - `llava-hf/llava-1.5-7b-hf` ✓
     - `llava-hf/llava-v1.5-7b` ✗ (wrong format)

2. **For gated models** (e.g., Llama-based):
   ```bash
   # Set HuggingFace token as secret
   mixtrain secret create HF_TOKEN your_token_here
   ```

3. **Check model type matches**:
   ```bash
   # For LLaVA:
   --model_type llava

   # For Qwen:
   --model_type qwen2_vl
   ```

---

### Error: `ValueError: Unknown model type`

**Cause**: `model_type` parameter doesn't match Axolotl's supported types.

**Supported types**:
- `llava` - LLaVA models
- `qwen2_vl` - Qwen2-VL models
- `phi3_v` - Phi-3-Vision
- Check Axolotl docs for complete list

**Fix**:
```bash
# Make sure model_type matches your base_model
--base_model llava-hf/llava-1.5-7b-hf \
--model_type llava  # Must match
```

---

## Performance Problems

### Training is very slow

**Diagnostic checklist**:

1. **Check FlashAttention is enabled**:
   ```bash
   --use_flash_attention true
   ```

2. **Verify GPU utilization**:
   - Look for GPU usage in logs
   - Should be 80-100% during training

3. **Check batch size**:
   ```bash
   # Too small = slow
   --batch_size 1  # ✗ slow

   # Better:
   --batch_size 4 \
   --gradient_accumulation_steps 4  # ✓ faster
   ```

4. **Enable DeepSpeed ZeRO-2** (not ZeRO-3):
   ```bash
   --deepspeed_config zero2  # ✓ good speed/memory balance
   --deepspeed_config zero3  # ✗ slower but saves memory
   ```

5. **Check sequence length**:
   ```bash
   # Too long = slow
   --max_seq_length 4096  # ✗ slow

   # Better:
   --max_seq_length 2048  # ✓ faster
   ```

**Optimized for speed**:
```bash
--batch_size 4 \
--gradient_accumulation_steps 2 \
--max_seq_length 2048 \
--use_flash_attention true \
--deepspeed_config zero2
```

---

### High loss / not converging

**Diagnostic steps**:

1. **Check learning rate**:
   ```bash
   # Too high
   --learning_rate 0.0001  # ✗ might diverge

   # Better:
   --learning_rate 0.00002  # ✓ stable
   --learning_rate 0.00001  # ✓ very stable
   ```

2. **Increase training epochs**:
   ```bash
   --num_epochs 5  # instead of 2-3
   ```

3. **Increase LoRA rank**:
   ```bash
   --lora_r 128 \
   --lora_alpha 32
   ```

4. **Check dataset quality**:
   - Are image-text pairs accurate?
   - Is there enough diversity?
   - Any corrupted data?

5. **Monitor with W&B**:
   ```bash
   --wandb_project my-experiments
   ```

---

## Debugging Steps

### Step 1: Enable Verbose Output

The workflow already prints:
- Dataset sample
- Full Axolotl configuration
- Training command

**Review these outputs carefully!**

### Step 2: Test with Minimal Config

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name sample-vlm-data \
  --output_model_name debug-test \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 1 \
  --batch_size 1 \
  --max_seq_length 512 \
  --use_flash_attention false
```

### Step 3: Check Generated Files

Files are in `/data/axolotl_workspace/`:
```bash
# Check these files exist and look correct:
/data/axolotl_workspace/train_data.jsonl
/data/axolotl_workspace/axolotl_config.yml
/data/axolotl_workspace/output/
```

### Step 4: Manual Axolotl Test

```bash
# SSH into the running workflow container
# Then manually test:
cd /data/axolotl_workspace
python -m axolotl.cli.train axolotl_config.yml --debug
```

### Step 5: Check Dependencies

```python
import torch
import transformers
import peft
import axolotl

print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.version.cuda}")
print(f"Transformers: {transformers.__version__}")
print(f"PEFT: {peft.__version__}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

### Step 6: Review Workflow Logs

```bash
# Get detailed logs
mixtrain workflow runs vlm-finetune
mixtrain workflow get vlm-finetune
```

---

## Common Workflow Issues

### Workflow doesn't start

1. **Check GPU quota**:
   ```bash
   mixtrain workspace get
   ```

2. **Verify workflow exists**:
   ```bash
   mixtrain workflow list
   ```

3. **Check for running workflows**:
   ```bash
   mixtrain workflow runs vlm-finetune
   ```

### Workflow times out

**Solutions**:

1. **Increase timeout** in workflow file:
   ```python
   _mixflow_timeout = 28800  # 8 hours instead of 4
   ```

2. **Reduce training time**:
   ```bash
   --num_epochs 3  # instead of 5
   ```

3. **Use faster model**:
   ```bash
   --base_model llava-hf/llava-1.5-7b-hf  # instead of 13B
   ```

---

## Getting Help

### Provide These Details

When asking for help, include:

1. **Exact error message** (full traceback)
2. **Generated Axolotl config** (from workflow output)
3. **Dataset sample** (from workflow output)
4. **Command used**:
   ```bash
   mixtrain workflow run vlm-finetune \
     --dataset_name ... \
     --output_model_name ...
   ```
5. **GPU and memory specs**
6. **Dataset size** (number of samples)

### Check These Resources

- [Axolotl GitHub Issues](https://github.com/OpenAccess-AI-Collective/axolotl/issues)
- [Axolotl Documentation](https://github.com/OpenAccess-AI-Collective/axolotl)
- [LLaVA Documentation](https://github.com/haotian-liu/LLaVA)
- Mixtrain Discord/Support

---

## Success Checklist

Before starting training, verify:

- [ ] Dataset uploaded to mixtrain
- [ ] Dataset has correct columns (image_path, prompt, response)
- [ ] Images are accessible from /data or are URLs
- [ ] Model ID is correct (check HuggingFace)
- [ ] model_type matches base_model
- [ ] GPU resources are available
- [ ] Timeout is sufficient for your dataset size
- [ ] Parameters are appropriate for GPU memory

**Test checklist**:
- [ ] Run with sample dataset first
- [ ] Use minimal config (1 epoch, small batch)
- [ ] Review generated config and dataset sample
- [ ] Monitor for first few minutes to ensure training starts

---

**Last Updated**: 2024
**Workflow Version**: 1.0
