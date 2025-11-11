# LEMM Setup & Model Integration Guide

## ✅ Integration Status

### Fully Working
- ✅ **ACE-Step v1-3.5B**: Music generation
- ✅ **Demucs (htdemucs)**: Stem separation
- ✅ **Pedalboard**: Audio enhancement
- ✅ **Gradio UI**: Web interface
- ✅ **Configuration system**: YAML-based settings

### Partial/Placeholder
- ⚠️ **so-vits-svc**: Files present, using Pedalboard for vocals instead
- ⚠️ **Lyrics Generator**: Placeholder implementation
- ⚠️ **MusicControlNet**: Basic conditioning only

## Quick Start

```powershell
# Launch application
python main.py

# Open browser
http://localhost:7860
```

## Detailed Setup

### Prerequisites

- Python 3.8+
- NVIDIA GPU with 8GB+ VRAM (recommended)
- CUDA 11.7+ installed
- 16GB+ RAM
- 10GB+ free disk space

### Verify Installation

```powershell
# Check Python
python --version

# Check CUDA/GPU
nvidia-smi

# Check virtual environment
.venv\Scripts\python.exe --version
```

### Model Locations

Your models are already in place:

```
models/
├── ACE-Step-v1-3.5B/          ✅ Ready
│   ├── ace_step_transformer/
│   ├── music_dcae_f8c8/
│   ├── music_vocoder/
│   └── umt5-base/
└── sovits/                     ⚠️ Partial
    ├── hubert_base.pt
    └── content_vec.pth
```

## Usage Guide

### Basic Generation

1. **Enter a prompt**:
   ```
   An upbeat pop song with electric guitars and drums
   ```

2. **Optional - Generate lyrics**:
   Click "Auto-Generate Lyrics" button

3. **Settings**:
   - Clips: 1-3 (start with 1 for testing)
   - Temperature: 0.7-1.5 (1.0 = balanced)

4. **Click "Generate Song"**

### Advanced Features

#### Custom Styles with LoRA

1. Go to "Training" tab
2. Upload training audio files
3. Set training parameters
4. Click "Start Training"
5. Use trained weights in generation

#### Multiple Clips

- Each clip = 32 seconds (2s lead-in + 28s main + 2s lead-out)
- Clips are automatically chained with crossfading
- Recommended: Start with 1 clip, increase gradually

## Configuration

Edit `config/config.yaml`:

```yaml
# Performance settings
models:
  ace_step:
    device: "cuda"  # or "cpu"
    num_inference_steps: 27  # 27=fast, 60=quality
    
# Audio settings
audio:
  sample_rate: 44100
  clip_duration: 32
  
# Generation
generation:
  default_clips: 3
  temperature: 1.0
```

## Performance Tips

### For Speed
- Use `num_inference_steps: 27`
- Generate 1 clip at a time
- Keep `shifts: 1` in Demucs

### For Quality
- Use `num_inference_steps: 60`
- Use `shifts: 2` in Demucs
- Higher sample rate (if hardware supports)

### Memory Saving
- Use `device: "cpu"` (much slower)
- Set `dtype: "float16"`
- Enable `split: true` in Demucs
- Generate fewer clips

## Troubleshooting

### CUDA Out of Memory

```yaml
# In config.yaml
models:
  ace_step:
    device: "cpu"  # Slower but works
```

Or:
- Close other applications
- Reduce number of clips
- Use num_inference_steps: 27

### Models Not Loading

Check logs:
```powershell
ls logs/
cat logs/lemm_[latest].log
```

Verify paths in `config/config.yaml`

### Poor Quality

- Increase `num_inference_steps` to 60
- Check prompt quality
- Try different prompts
- Verify models loaded successfully

## Model Details

### ACE-Step v1-3.5B

**Capabilities**:
- Text-to-music generation
- Lyrics support (if provided)
- Duration control
- 15× faster than LLM-based models
- Multi-language support

**Performance**:
- 27 steps: ~20-30s for 32s clip (RTX 3090)
- 60 steps: ~45-60s for 32s clip

**Input Format**:
```python
{
  "prompt": "genre, style, mood, tempo, instruments",
  "lyrics": "optional lyrics text",
  "audio_length_in_s": 32,
  "guidance_scale": 7.5
}
```

### Demucs (htdemucs)

**Capabilities**:
- Separates into 4 stems: vocals, bass, drums, other
- State-of-the-art quality
- Hybrid Transformer architecture

**Performance**:
- ~10-20s for 32s clip
- GPU accelerated

### Pedalboard (Spotify)

**Effects Applied**:
- **Vocals**: De-essing, presence boost, compression, reverb
- **Bass**: Low-shelf filter, compression, gain
- **Drums**: High-shelf filter, compression
- **Other**: Compression, reverb, gain

## Testing Checklist

- [ ] Launch application successfully
- [ ] Generate instrumental clip (1 clip, no lyrics)
- [ ] Generate with lyrics (use auto-generate)
- [ ] Generate multiple clips (2-3 clips)
- [ ] Try different genres
- [ ] Download WAV output
- [ ] Check audio quality

## Expected Timings

For 1 clip (32 seconds):
- Prompt analysis: < 1s
- Music generation (ACE-Step): 20-60s
- Stem separation (Demucs): 10-20s
- Enhancement (Pedalboard): < 5s
- Mixing: < 5s
- **Total**: ~40-90 seconds

For 3 clips:
- **Total**: ~3-5 minutes

## Logs

Application logs are in `logs/`:
```powershell
# View latest
ls logs/

# Monitor in real-time
Get-Content logs/lemm_*.log -Wait -Tail 20
```

## Next Steps

### For Better Lyrics
Integrate SongComposer model when available

### For Better Vocals
Complete so-vits-svc integration with trained checkpoint

### For Better Clip Continuity
Integrate MusicControlNet model when available

## Support

1. Check logs in `logs/`
2. Review `README.md`
3. Check `docs/WORKFLOW.md` for pipeline details
4. Verify configuration in `config/config.yaml`

---

**Status**: ✅ Core pipeline operational with ACE-Step, Demucs, and Pedalboard
