# 🎵 LEMM - Quick Reference

## Launch Command
```powershell
python main.py
```
Access at: **http://localhost:7860**

## Project Structure
```
lemm_beta/
├── src/              # Source code
├── config/           # Configuration
├── models/           # AI models (add here)
├── output/           # Generated songs
├── docs/             # Documentation
└── main.py           # Entry point
```

## Key Files
- `README.md` - Full documentation
- `docs/WORKFLOW.md` - Visual pipeline diagram
- `docs/SETUP.md` - Setup instructions
- `config/config.yaml` - All settings
- `requirements.txt` - Dependencies

## Configuration (config/config.yaml)
```yaml
# Most important settings:
audio:
  sample_rate: 44100
  clip_duration: 32

models:
  ace_step:
    device: "cuda"  # or "cpu"
    
generation:
  default_clips: 3
  temperature: 1.0
```

## Common Commands

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Install PyTorch (CUDA)
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Run Application
```powershell
python main.py
```

### Check GPU
```python
import torch
print(torch.cuda.is_available())
```

## Workflow Summary
```
Prompt → Analysis → Lyrics → Generate Clips → 
Separate Stems → Enhance → Mix → Chain → Export
```

## Clip Structure
- **2 seconds**: Lead-in
- **28 seconds**: Main content  
- **2 seconds**: Lead-out
- **Total**: 32 seconds per clip

## Models Needed
1. **ACE-Step** - Music generation
2. **SongComposer** - Lyrics  
3. **MusicControlNet** - Conditioning
4. **Demucs** - Stem separation (via pip)
5. **so-vits-svc** - Vocal enhancement

## Model Locations
```
models/
├── ace_step/
├── song_composer/
├── music_control_net/
└── so_vits_svc/
```

## Generation Time (estimated)
- 1 clip: ~1-2 minutes
- 3 clips: ~3-5 minutes
- 5 clips: ~5-8 minutes

## UI Features
✅ Prompt input & analysis  
✅ Auto-lyrics button  
✅ Clip settings (1-10 clips)  
✅ Temperature control  
✅ LoRA model support  
✅ Audio playback  
✅ WAV/MP3 download  
✅ Training tab  

## Code Structure

### Models (`src/models/`)
- `prompt_analyzer.py` - Text analysis
- `lyrics_generator.py` - Lyric generation
- `music_generator.py` - Music generation

### Audio (`src/audio/`)
- `processor.py` - Stem separation & enhancement
- `mixer.py` - Mixing & chaining

### UI (`src/ui/`)
- `gradio_interface.py` - Web interface

### Utils (`src/utils/`)
- `config_loader.py` - Configuration
- `file_manager.py` - File I/O

## Troubleshooting

### Import Errors
```powershell
pip install -r requirements.txt
```

### CUDA Not Found
```powershell
# Reinstall PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory
- Reduce `default_clips` in config
- Use `device: "cpu"` instead of `"cuda"`
- Use `dtype: "float16"` instead of `"float32"`

## Environment Info
- **Python**: 3.13.3
- **Virtual Env**: `.venv/`
- **Activation**: Done automatically by VS Code

## Status Indicators
🟢 **Working**: UI, config, file management  
🟡 **Placeholder**: Music gen, lyrics, stem processing  
🔴 **Needs Setup**: Model downloads  

## Quick Test
```powershell
python main.py
# Navigate to http://localhost:7860
# Enter prompt: "upbeat pop song with guitars"
# Click "Generate Song"
# (Will produce mock audio until models are integrated)
```

## Resources
- GitHub: [Add your repo URL]
- Docs: `docs/` folder
- Logs: `logs/` folder
- Output: `output/` folder

## Support
1. Check `docs/SETUP.md`
2. Review `README.md`
3. Check logs in `logs/`
4. Open GitHub issue

---
**LEMM v0.1.0** - Let Everyone Make Music 🎵
