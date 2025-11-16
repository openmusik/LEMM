---
title: LEMM - Let Everyone Make Music
emoji: 🎵
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: mit
models:
  - ACE-Step/ACE-Step-v1-3.5B
python_version: "3.10"
suggested_hardware: t4-medium
suggested_storage: medium
---

# LEMM - Let Everyone Make Music

An AI-powered music generation system that creates complete songs from text prompts with **automatic training dataset management**.

**ZeroGPU Compatible** - Optimized for HuggingFace's free H200 GPU allocation!

## ✨ Features
- 🎼 AI Music Generation with ACE-Step & MusicGen
- 📝 Auto-Lyrics Generation with Variation
- � Vocal Synthesis (CPU-Compatible)
- �🎛️ Professional Audio Processing
- 🎸 Stem Separation & Enhancement
- 📊 **Auto-Download Training Datasets**
- 🎨 LoRA Fine-tuning Support
- ⚡ ZeroGPU Support for Free GPU Access
- ⏱️ Time Estimation for Generation

## 🗂️ Dataset Management

LEMM **automatically downloads** training datasets when deployed on HuggingFace Spaces!

### Available Dataset Phases

Configure via environment variable: `LEMM_DATASET_PHASE`

| Phase | Datasets | Size | Description |
|-------|----------|------|-------------|
| **minimal** | NSynth, LJ Speech, URMP, FMA Small | 54 GB | Essential training (default) |
| **balanced** | Minimal + LibriTTS, MusicNet | 120 GB | Production-ready |
| **comprehensive** | Balanced + FMA Large, Lakh MIDI | 227 GB | Full capabilities |

### Included Datasets (All Commercially Licensed)

- ✅ **NSynth** (30GB) - 305K instrument notes, CC-BY 4.0
- ✅ **LJ Speech** (3GB) - Voice synthesis, Public Domain
- ✅ **URMP** (13GB) - Multi-instrument stems
- ✅ **FMA** (8-106GB) - Music genres, CC-BY
- ✅ **LibriTTS** (60GB) - Multi-speaker TTS, CC-BY 4.0
- ✅ **MusicNet** (6GB) - Classical notation, CC-BY 4.0
- ✅ **Lakh MIDI** (0.5GB) - Symbolic music, CC-BY 4.0

See [DATASET_ANALYSIS.md](DATASET_ANALYSIS.md) for full details.

## 🚀 Usage
## 🚀 Usage
1. Enter a text description of your desired song
2. Click 🎲 to randomize lyrics or write custom lyrics
3. Choose the number of 32-second clips
4. View estimated generation time
5. Click Generate and wait for your AI-created music!

## ⚙️ Configuration

Set environment variables in Space Settings:

```bash
LEMM_DATASET_PHASE=minimal  # minimal, balanced, or comprehensive
CONFIG_PATH=config/config.yaml
```

## 🛠️ Technical Details
- **Models**: ACE-Step v1-3.5B, MusicGen
- **Python**: 3.10
- **GPU**: Optional (CPU fallback available)
- **Datasets**: Auto-managed via HuggingFace Hub
- **Storage**: 50-250 GB depending on dataset phase

## 📝 Note
- First run downloads datasets (5-60 minutes depending on phase)
- Models cached after first load (~2-3 minutes)
- Generation time: 3-15 minutes depending on clips and hardware
- Dataset downloads persist across restarts
