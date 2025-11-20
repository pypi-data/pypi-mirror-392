# Multi-Node Training Setup Guide

The Axolotl VLM fine-tuning workflow **automatically adapts** to both single-GPU and multi-node distributed training environments.

## How It Works

The workflow detects your environment by checking for distributed training environment variables:

```python
# Automatically detects distributed environment
is_distributed = any(
    env_var in os.environ
    for env_var in ["MASTER_ADDR", "RANK", "WORLD_SIZE", "LOCAL_RANK"]
)
```

### Single-GPU Mode (Default)

**When**: No distributed environment variables are set

**Command Used**:
```bash
python -m axolotl.cli.train config.yml
```

**Output**:
```
🖥️  Single GPU mode - running without distributed setup

Training command: python -m axolotl.cli.train ./axolotl_config.yml
```

**Use Cases**:
- Development and testing
- Small datasets
- Single GPU machines
- Local experimentation

---

### Multi-Node/Multi-GPU Mode

**When**: Distributed environment variables are detected

**Command Used**:
```bash
accelerate launch -m axolotl.cli.train config.yml
```

**Output**:
```
🌐 Detected distributed environment - using accelerate launch
  MASTER_ADDR: 192.168.1.100
  RANK: 0
  WORLD_SIZE: 4
  LOCAL_RANK: 0

Training command: accelerate launch -m axolotl.cli.train ./axolotl_config.yml
```

**Use Cases**:
- Production training
- Large datasets
- Multi-GPU single node
- Multi-node clusters

---

## Setting Up Multi-Node Training

### Prerequisites

1. **Multiple GPU nodes** with same environment setup
2. **Network connectivity** between all nodes
3. **Same Axolotl version** on all nodes
4. **Shared storage** (e.g., NFS) or synchronized datasets

### Configuration Steps

#### 1. Choose Master Node

Pick one node as the master (usually node 0/RANK 0):
```bash
# Master node IP
MASTER_ADDR=192.168.1.100
MASTER_PORT=29500
```

#### 2. Set Environment Variables

**On Master Node (RANK 0)**:
```bash
export MASTER_ADDR=192.168.1.100
export MASTER_PORT=29500
export RANK=0
export WORLD_SIZE=4        # Total number of processes
export LOCAL_RANK=0        # Local rank on this node
```

**On Worker Node 1 (RANK 1)**:
```bash
export MASTER_ADDR=192.168.1.100
export MASTER_PORT=29500
export RANK=1
export WORLD_SIZE=4
export LOCAL_RANK=0
```

**On Worker Node 2 (RANK 2)**:
```bash
export MASTER_ADDR=192.168.1.100
export MASTER_PORT=29500
export RANK=2
export WORLD_SIZE=4
export LOCAL_RANK=0
```

**On Worker Node 3 (RANK 3)**:
```bash
export MASTER_ADDR=192.168.1.100
export MASTER_PORT=29500
export RANK=3
export WORLD_SIZE=4
export LOCAL_RANK=0
```

#### 3. Run the Workflow

On **each node**, run the same workflow command:

```bash
mixtrain workflow run vlm-finetune \
  --dataset_name my-dataset \
  --output_model_name my-model \
  --base_model llava-hf/llava-1.5-7b-hf \
  --num_epochs 3 \
  --batch_size 2
```

The workflow will automatically:
- ✅ Detect distributed environment
- ✅ Use `accelerate launch`
- ✅ Coordinate across nodes
- ✅ Synchronize gradients
- ✅ Save checkpoints on master node

---

## Multi-GPU Single Node

For **multiple GPUs on a single machine**, you can also use distributed training:

### Option 1: Manual Setup
```bash
export MASTER_ADDR=localhost
export MASTER_PORT=29500
export WORLD_SIZE=4  # 4 GPUs on this node

# Run with torchrun or accelerate
mixtrain workflow run vlm-finetune \
  --dataset_name my-dataset \
  --output_model_name my-model
```

### Option 2: Let Accelerate Handle It
```bash
# Set minimal env var to trigger distributed mode
export MASTER_ADDR=localhost

# Run workflow - accelerate will auto-detect GPUs
mixtrain workflow run vlm-finetune \
  --dataset_name my-dataset \
  --output_model_name my-model
```

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `MASTER_ADDR` | IP address of master node | `192.168.1.100` or `localhost` |
| `MASTER_PORT` | Port for communication | `29500` (default) |
| `RANK` | Global rank of this process | `0`, `1`, `2`, `3` (for 4 nodes) |
| `WORLD_SIZE` | Total number of processes | `4` (for 4 GPUs/nodes) |
| `LOCAL_RANK` | Rank on this specific node | Usually `0` for single-GPU nodes |
| `NODE_RANK` | Rank of this node | `0`, `1`, `2` (for multi-node) |

---

## Verification

### Check Detection

The workflow will print which mode it detected:

**Single GPU**:
```
🖥️  Single GPU mode - running without distributed setup
```

**Multi-Node**:
```
🌐 Detected distributed environment - using accelerate launch
  MASTER_ADDR: 192.168.1.100
  RANK: 0
  WORLD_SIZE: 4
  LOCAL_RANK: 0
```

### Verify Distributed Training

Look for these in the training logs:

```
[2025-11-19 00:30:00] [INFO] Distributed training detected
[2025-11-19 00:30:00] [INFO] World size: 4
[2025-11-19 00:30:00] [INFO] Global rank: 0
[2025-11-19 00:30:00] [INFO] Local rank: 0
```

---

## Performance Expectations

### Scaling Efficiency

| Setup | GPUs | Effective Batch Size | Expected Speed |
|-------|------|---------------------|----------------|
| Single GPU | 1 | 8 | 1x (baseline) |
| Single Node | 4 | 32 | ~3.5x |
| Multi-Node | 8 | 64 | ~7x |
| Multi-Node | 16 | 128 | ~14x |

**Note**: Actual speedup depends on:
- Network bandwidth (for multi-node)
- Model size
- Batch size
- Communication overhead

### Recommended Configurations

**2 Nodes (4 GPUs each)**:
```bash
--batch_size 4 \
--gradient_accumulation_steps 2
# Effective batch = 4 × 2 × 8 GPUs = 64
```

**4 Nodes (4 GPUs each)**:
```bash
--batch_size 2 \
--gradient_accumulation_steps 2
# Effective batch = 2 × 2 × 16 GPUs = 64
```

---

## Troubleshooting Multi-Node

### Issue: Nodes Can't Connect

**Symptoms**:
```
RuntimeError: Connection timeout
```

**Solutions**:
1. Check network connectivity: `ping $MASTER_ADDR`
2. Verify firewall allows port `$MASTER_PORT`
3. Ensure all nodes have same Axolotl version
4. Check MASTER_ADDR is reachable from all nodes

### Issue: Rank Mismatch

**Symptoms**:
```
RuntimeError: Rank mismatch
```

**Solutions**:
1. Verify `WORLD_SIZE` is same on all nodes
2. Check `RANK` is unique for each node
3. Ensure all nodes started with same command

### Issue: Out of Sync

**Symptoms**:
```
RuntimeError: Collective operation timeout
```

**Solutions**:
1. Reduce batch size
2. Enable gradient checkpointing
3. Check network bandwidth
4. Verify shared storage is accessible

---

## Best Practices

### 1. Shared Storage
Use shared filesystem (NFS, Lustre) or object storage for:
- ✅ Dataset access
- ✅ Checkpoint saving
- ✅ Model output

### 2. Synchronization
Ensure all nodes:
- ✅ Have same code version
- ✅ Use same Docker image
- ✅ Access same dataset
- ✅ Write checkpoints to shared location

### 3. Monitoring
Monitor on **master node** (RANK 0):
- ✅ Training loss
- ✅ GPU utilization across nodes
- ✅ Network bandwidth
- ✅ Checkpoint saving

### 4. Fault Tolerance
- ✅ Use checkpoint saving (`save_strategy: "epoch"`)
- ✅ Save frequently for long training runs
- ✅ Can resume from checkpoint if node fails

---

## Example: 4-Node Setup

### Node Setup

**Node 0 (Master)**: `gpu-node-0.example.com`
```bash
export MASTER_ADDR=gpu-node-0.example.com
export MASTER_PORT=29500
export RANK=0
export WORLD_SIZE=4
export LOCAL_RANK=0

mixtrain workflow run vlm-finetune \
  --dataset_name production-dataset \
  --output_model_name llava-production-v1 \
  --num_epochs 5 \
  --batch_size 4
```

**Node 1**: `gpu-node-1.example.com`
```bash
export MASTER_ADDR=gpu-node-0.example.com
export MASTER_PORT=29500
export RANK=1
export WORLD_SIZE=4
export LOCAL_RANK=0

# Same command as master
mixtrain workflow run vlm-finetune ...
```

**Node 2 & 3**: Similar setup with `RANK=2` and `RANK=3`

### Expected Output

All nodes will show:
```
🌐 Detected distributed environment - using accelerate launch
  MASTER_ADDR: gpu-node-0.example.com
  RANK: [0-3]
  WORLD_SIZE: 4
  LOCAL_RANK: 0

[2025-11-19 01:00:00] [INFO] Distributed training with 4 processes
[2025-11-19 01:00:00] [INFO] Starting training...
```

Only **master node (RANK 0)** saves checkpoints and final model.

---

## Testing Multi-Node Setup

### Quick Test (1 Epoch)

```bash
# On all nodes simultaneously
mixtrain workflow run vlm-finetune \
  --dataset_name test-small \
  --output_model_name multi-node-test \
  --num_epochs 1 \
  --batch_size 1
```

### Verify Speedup

Compare training time:
```bash
# Single GPU: ~60 minutes
# 4 GPUs (1 node): ~17 minutes  (3.5x speedup)
# 8 GPUs (2 nodes): ~9 minutes  (6.7x speedup)
```

---

## Migration Guide

### From Single GPU to Multi-Node

**No code changes needed!** Just:

1. ✅ Set environment variables on each node
2. ✅ Run same workflow command on all nodes
3. ✅ Workflow auto-detects and adapts

**Before** (single GPU):
```bash
mixtrain workflow run vlm-finetune --dataset_name my-data ...
```

**After** (multi-node):
```bash
# Set env vars
export MASTER_ADDR=node-0
export RANK=0
export WORLD_SIZE=4

# Same command!
mixtrain workflow run vlm-finetune --dataset_name my-data ...
```

---

## Summary

✅ **Automatic Detection**: No code changes needed
✅ **Single Command**: Same workflow for both modes
✅ **Flexible Scaling**: 1 GPU → 100+ GPUs
✅ **Production Ready**: Fault-tolerant with checkpointing

The workflow adapts automatically - just set the environment variables for your desired setup!
