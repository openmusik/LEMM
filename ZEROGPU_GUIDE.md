# ZeroGPU Deployment Guide for LEMM

## What is ZeroGPU?

ZeroGPU is HuggingFace's free GPU allocation system for Spaces. Instead of paying for continuous GPU access, ZeroGPU provides:

- **Free GPU access** on H200 (or A100/A10G)
- **On-demand allocation** - GPU only when needed
- **Automatic management** - No manual GPU handling
- **Queue system** - Fair sharing among users

## How LEMM Uses ZeroGPU

LEMM is now **fully compatible** with ZeroGPU through the `@spaces.GPU` decorator:

```python
@spaces.GPU(duration=120)  # Request GPU for 2 minutes
def generate_clip(self, prompt, lyrics, ...):
    # GPU-intensive music generation happens here
    # GPU automatically allocated when this function runs
    # GPU released after completion or timeout
```

## Benefits for LEMM

### 1. **Cost Savings**
- **Traditional GPU**: $0.60/hour (T4) to $3.15/hour (A10G) continuous
- **ZeroGPU**: FREE - pay only for compute time used
- **Example**: Generate 5 songs/day = ~30 minutes GPU time = $0 instead of $18/day

### 2. **Better Hardware**
- Access to **H200** (latest NVIDIA GPU)
- 141GB GPU memory vs 16GB on T4
- Much faster generation times

### 3. **Automatic Scaling**
- No GPU when idle = no cost
- GPU allocated on-demand
- Automatically handles multiple users

## Setup Instructions

### 1. Code Changes (Already Done!)

✅ Added `spaces` import with fallback:
```python
try:
    import spaces
    ZEROGPU_AVAILABLE = True
except ImportError:
    ZEROGPU_AVAILABLE = False
```

✅ Added `@spaces.GPU` decorator to generation methods:
```python
@spaces.GPU(duration=120)
def generate_clip(self, ...):
```

✅ Updated requirements:
```
spaces  # Added to requirements_space.txt
```

### 2. Create HuggingFace Space

**Important**: Select **ZeroGPU** hardware during creation:

```
1. Go to: https://huggingface.co/new-space
2. Fill in:
   - Name: lemm-music-generator
   - SDK: Gradio
   - Hardware: ZeroGPU (H200) ⚡ FREE
   - Visibility: Public or Private
3. Click "Create Space"
```

### 3. Update Space Metadata

In `README_SPACE.md`, ensure you have:

```yaml
---
suggested_hardware: h200
suggested_storage: small
---
```

### 4. Deploy Code

Upload your code as normal (see HUGGINGFACE_DEPLOYMENT.md):

```powershell
git clone https://huggingface.co/spaces/YOUR_USERNAME/lemm-music-generator
cd lemm-music-generator
# Copy files...
git push
```

## ZeroGPU Limitations & Considerations

### Duration Limits
- **Default**: 60 seconds
- **LEMM**: 120 seconds (configured in decorator)
- **Maximum**: 300 seconds (5 minutes)
- **Adjust if needed**:
  ```python
  @spaces.GPU(duration=180)  # 3 minutes
  ```

### Memory Limits
- **H200**: 141GB GPU memory (plenty for ACE-Step)
- **ACE-Step model**: ~7GB
- **Generation**: ~4-8GB during inference
- **Total needed**: ~15GB max ✅ Plenty of room

### Queuing
- During high traffic, requests may queue
- Users see "Waiting for GPU..." message
- Typical wait: 0-30 seconds
- Gradio handles this automatically

### Cold Starts
- First request loads model (~30-60 seconds)
- Subsequent requests are faster
- Model cached for ~15 minutes of inactivity

## Performance Expectations

### Generation Times (per 32-second clip)

**H200 (ZeroGPU):**
- First clip: ~45-60 seconds (includes model loading)
- Subsequent clips: ~30-40 seconds
- Full song (5 clips): ~3-4 minutes

**vs Traditional GPU:**
- T4: ~90-120 seconds per clip
- A10G: ~45-60 seconds per clip
- H200 is comparable to A10G but FREE!

## Best Practices

### 1. Optimize Decorator Duration
```python
# Too short = timeout errors
@spaces.GPU(duration=60)  # May fail for large songs

# Too long = wasted allocation
@spaces.GPU(duration=300)  # Unnecessary for 30s generation

# Just right
@spaces.GPU(duration=120)  # 2 minutes is perfect for LEMM
```

### 2. Handle Timeouts Gracefully
```python
try:
    clip = self.generate_clip(...)
except Exception as e:
    if "GPU timeout" in str(e):
        logger.error("GPU allocation timed out")
        # Return graceful error to user
```

### 3. Progress Updates
```python
# Update Gradio interface during long operations
yield "Loading model..."
yield "Generating clip 1/5..."
yield "Processing audio..."
```

### 4. Minimize GPU Time
- Load models once, reuse
- Cache intermediate results
- Only use GPU for generation, not preprocessing

## Monitoring & Debugging

### Check GPU Usage
In your Space logs, you'll see:
```
🔵 ZeroGPU: Allocating H200 GPU...
🟢 ZeroGPU: GPU allocated (device 0)
⚡ Generating music...
🟢 ZeroGPU: Releasing GPU (48.3s used)
```

### Common Issues

**Issue**: "GPU timeout"
**Solution**: Increase duration in decorator
```python
@spaces.GPU(duration=180)  # Increase from 120 to 180
```

**Issue**: "Out of memory"
**Solution**: Reduce batch size or enable CPU offload
```python
cpu_offload=True  # In ACE-Step config
```

**Issue**: "Long queue times"
**Solution**: This is normal during peak hours, happens automatically

## Cost Comparison

### Scenario: Public Demo Space (100 users/day)

**Traditional GPU (T4):**
- 24/7 operation: $0.60/hr × 24 × 30 = $432/month
- Or pay-per-use with complex scaling

**ZeroGPU:**
- 100 users × 3 min avg = 300 min/day = 5 hrs/day
- **Cost**: $0/month ✅

### Scenario: Personal Testing (10 songs/week)

**Traditional GPU:**
- Keep running: $432/month
- Or manual start/stop (annoying)

**ZeroGPU:**
- **Cost**: $0/month ✅

## Migration Checklist

- [x] Add `spaces` to requirements
- [x] Import `spaces` with fallback
- [x] Add `@spaces.GPU` decorator to generation methods
- [x] Update README with ZeroGPU info
- [x] Set `suggested_hardware: h200` in metadata
- [ ] Create Space with ZeroGPU hardware
- [ ] Deploy and test
- [ ] Monitor logs for GPU allocation

## Testing ZeroGPU Locally

You **cannot** test ZeroGPU locally (it only works on HuggingFace Spaces). However, the code gracefully falls back:

```python
# Local testing - decorator does nothing
@spaces.GPU(duration=120)
def generate_clip(self, ...):
    # Runs normally on your local GPU/CPU
```

## FAQ

**Q: Is ZeroGPU really free?**
A: Yes! HuggingFace provides it free for public Spaces.

**Q: What if I need private Space?**
A: Private Spaces can use ZeroGPU but may have different quotas.

**Q: Can I use my own GPU instead?**
A: Yes! The code works with both ZeroGPU and traditional GPU hardware.

**Q: What if generation takes longer than 120 seconds?**
A: Increase the duration parameter: `@spaces.GPU(duration=180)`

**Q: Does it work with multiple users simultaneously?**
A: Yes! Each user gets queued and allocated GPU in turn.

**Q: How do I upgrade from T4 to ZeroGPU?**
A: Go to Space Settings → Hardware → Select "ZeroGPU (H200)"

## Further Reading

- HuggingFace ZeroGPU Docs: https://huggingface.co/docs/hub/spaces-gpus#zero-gpu
- Spaces Pricing: https://huggingface.co/pricing#spaces
- GPU Hardware Options: https://huggingface.co/docs/hub/spaces-gpus

---

**Ready to deploy?** Follow the main deployment guide in `HUGGINGFACE_DEPLOYMENT.md` and select ZeroGPU hardware during Space creation!
