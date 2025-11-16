# Dataset Management Guide for LEMM

## Automatic Dataset Downloading on HuggingFace Spaces

LEMM includes an intelligent dataset management system that automatically downloads training datasets when deployed on HuggingFace Spaces.

## 🚀 Quick Start

### For HuggingFace Space Deployment

The dataset manager will **automatically** download datasets when your Space starts up. Configure it using environment variables:

```yaml
# In your Space's Settings > Variables
LEMM_DATASET_PHASE=minimal  # Options: minimal, balanced, comprehensive
```

### Dataset Phases

| Phase | Datasets | Total Size | Best For |
|-------|----------|------------|----------|
| **Minimal** | NSynth, LJ Speech, URMP, FMA Small | ~54 GB | Quick setup, essential features |
| **Balanced** | Minimal + LibriTTS, MusicNet | ~120 GB | Production-ready training |
| **Comprehensive** | Balanced + FMA Large, Lakh MIDI | ~227 GB | Full research capabilities |

## 📊 Included Datasets

### Phase 1: Minimal (Essential) - 54 GB

1. **NSynth** (30 GB) - CC-BY 4.0
   - 305,979 musical notes across 1,006 instruments
   - Perfect for music synthesis training
   - ⭐⭐⭐⭐⭐ Priority

2. **LJ Speech** (2.6 GB) - Public Domain
   - 13,100 speech clips, high-quality single speaker
   - Essential for vocal synthesis
   - ⭐⭐⭐⭐⭐ Priority

3. **URMP** (12.5 GB) - Research License
   - 44 multi-instrument classical pieces with stems
   - Multi-instrument coordination training
   - ⭐⭐⭐⭐ Priority

4. **FMA Small** (8 GB) - CC-BY
   - 8,000 music tracks, 30-second clips
   - Genre diversity training
   - ⭐⭐⭐⭐ Priority

### Phase 2: Balanced (Additional) - +66 GB

5. **LibriTTS** (60 GB) - CC-BY 4.0
   - 585 hours, 2,456 speakers
   - Multi-speaker TTS training
   - ⭐⭐⭐⭐ Priority

6. **MusicNet** (6 GB) - CC-BY 4.0
   - 330 classical recordings with note annotations
   - Music notation and transcription
   - ⭐⭐⭐ Priority

### Phase 3: Comprehensive (Additional) - +107 GB

7. **FMA Large** (106 GB) - CC-BY
   - 106,000 music tracks, 161 genres
   - Extended genre coverage
   - ⭐⭐ Priority

8. **Lakh MIDI** (0.5 GB) - CC-BY 4.0
   - 176,581 MIDI files
   - Symbolic music generation
   - ⭐⭐⭐ Priority

## 🛠️ Manual Dataset Management

### Command Line Interface

```bash
# List available datasets
python -m src.utils.dataset_manager --list

# Check download status
python -m src.utils.dataset_manager --status

# Download minimal phase
python -m src.utils.dataset_manager --phase minimal

# Download balanced phase
python -m src.utils.dataset_manager --phase balanced

# Download comprehensive phase
python -m src.utils.dataset_manager --phase comprehensive
```

### Python API

```python
from src.utils.dataset_manager import DatasetManager

# Initialize manager
manager = DatasetManager(cache_dir="datasets")

# Download a specific dataset
manager.download_dataset("nsynth")

# Download entire phase
manager.download_phase("minimal")

# Check status
status = manager.get_status_summary()
print(f"Downloaded: {status['downloaded']} datasets")
print(f"Total size: {status['downloaded_size_gb']} GB")

# List available datasets
datasets = manager.list_available_datasets()
for ds in datasets:
    print(f"{ds['name']}: {ds['status']}")
```

## 🔧 Configuration

Edit `config/config.yaml` to customize dataset behavior:

```yaml
datasets:
  auto_download: true  # Auto-download on Space startup
  phase: "minimal"  # Default phase to download
  cache_dir: "datasets"  # Cache location
  use_hf_cache: true  # Use HuggingFace cache system
  max_storage_gb: 150  # Storage limit
  
  priorities:  # Download priority (1-5)
    nsynth: 5
    ljspeech: 5
    urmp: 4
    # ... etc
```

## 📝 License Information

All included datasets are **commercially usable** with proper attribution:

- **CC-BY 4.0**: NSynth, LibriTTS, MusicNet, Lakh MIDI, FMA
- **CC-0 / Public Domain**: LJ Speech
- **Research License**: URMP (verify for commercial use)

**Excluded** datasets (non-commercial licenses):
- ❌ MAESTRO (CC-BY-NC-SA 4.0)
- ❌ MUSDB18 (CC-BY-NC-SA 4.0)

## 🔍 Dataset Details

### NSynth
- **Source**: Google Magenta
- **Download**: HuggingFace Hub (`google/nsynth`)
- **Format**: WAV (16kHz, 4 seconds) + JSON metadata
- **Best for**: Instrument timbre, synthesis training

### LJ Speech
- **Source**: Keith Ito
- **Download**: HuggingFace Hub (`lj_speech`)
- **Format**: WAV (22kHz) + transcriptions
- **Best for**: Single-speaker TTS, voice quality baseline

### URMP
- **Source**: University of Rochester
- **Download**: Direct URL
- **Format**: Individual stems + video + MIDI + annotations
- **Best for**: Multi-instrument generation, source separation

### FMA (Free Music Archive)
- **Source**: EPFL
- **Download**: Direct URL (Small) or HF Hub (community upload)
- **Format**: MP3 (variable quality)
- **Best for**: Genre classification, style diversity

### LibriTTS
- **Source**: LibriVox
- **Download**: HuggingFace Hub (`cdminix/libritts`)
- **Format**: WAV (24kHz) + text
- **Best for**: Multi-speaker TTS, prosody modeling

### MusicNet
- **Source**: University of Washington
- **Download**: Direct URL (Zenodo)
- **Format**: WAV + MIDI alignments
- **Best for**: Note transcription, classical music

### Lakh MIDI
- **Source**: LabROSA (Columbia)
- **Download**: Direct URL
- **Format**: MIDI files only
- **Best for**: Symbolic music generation, structure analysis

## 💡 Tips for HuggingFace Spaces

### Storage Management
- Start with **minimal** phase (54 GB) to test
- Upgrade to **balanced** (120 GB) for production
- Only use **comprehensive** (227 GB) if you have persistent storage

### Caching
- Enable `use_hf_cache: true` to leverage HuggingFace's cache system
- Datasets persist across Space restarts
- Share cache with other HF models

### Performance
- Downloads run **on first startup** only
- Subsequent starts use cached data
- Use Space secrets for download tokens if needed

### Environment Variables
```bash
# Set dataset phase
LEMM_DATASET_PHASE=minimal

# Set custom cache directory
HF_HOME=/data/cache  # For persistent storage Spaces
```

## 🐛 Troubleshooting

### "Failed to download dataset"
- Check internet connectivity
- Verify HuggingFace Hub access
- Check storage space availability

### "Dataset already exists but not detected"
- Run: `python -m src.utils.dataset_manager --status`
- Check `datasets/dataset_status.json`
- Clear cache if corrupted

### "Out of storage space"
- Reduce phase: `comprehensive` → `balanced` → `minimal`
- Set lower `max_storage_gb` in config
- Clear old datasets: `manager.status["downloaded"].clear()`

## 📚 Additional Resources

- [DATASET_ANALYSIS.md](../DATASET_ANALYSIS.md) - Full dataset evaluation
- [HuggingFace Datasets](https://huggingface.co/docs/datasets) - Documentation
- [Magenta Datasets](https://magenta.tensorflow.org/datasets) - Google Magenta datasets

## 🔄 Updating Datasets

To refresh or update datasets:

```python
from src.utils.dataset_manager import DatasetManager

manager = DatasetManager()

# Clear specific dataset
del manager.status["downloaded"]["nsynth"]
manager._save_status()

# Re-download
manager.download_dataset("nsynth")
```

## 📞 Support

For dataset-related issues:
1. Check `logs/lemm_*.log` for detailed error messages
2. Review `datasets/dataset_status.json` for download history
3. Open an issue on GitHub with error logs
