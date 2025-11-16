# LEMM Dataset Quick Reference

## 🚀 TL;DR

**HuggingFace Space**: Datasets download automatically on first startup
**Local**: Run `python -m src.utils.dataset_manager --phase minimal`

## 📊 Phases at a Glance

| Phase | Size | Datasets | Use Case |
|-------|------|----------|----------|
| **minimal** | 54 GB | 4 | Free tier, testing |
| **balanced** | 120 GB | 6 | Production (recommended) |
| **comprehensive** | 227 GB | 8 | Research, full features |

## 🎯 Essential Datasets

```
⭐⭐⭐⭐⭐ NSynth (30GB)      - Music synthesis
⭐⭐⭐⭐⭐ LJ Speech (3GB)    - Vocal synthesis
⭐⭐⭐⭐ URMP (13GB)          - Multi-instrument
⭐⭐⭐⭐ FMA Small (8GB)      - Music genres
```

## ⚙️ Environment Variables

```bash
LEMM_DATASET_PHASE=minimal     # Set in Space settings
HF_HOME=/data/cache            # Optional: persistent cache
```

## 💻 CLI Commands

```bash
# List datasets
python -m src.utils.dataset_manager --list

# Check status
python -m src.utils.dataset_manager --status

# Download phase
python -m src.utils.dataset_manager --phase minimal
```

## 🐍 Python API

```python
from src.utils.dataset_manager import DatasetManager

manager = DatasetManager()
manager.download_phase("minimal")
status = manager.get_status_summary()
```

## 📁 Config Location

`config/config.yaml` → `datasets` section

## 📚 Full Docs

- **Dataset Analysis**: `DATASET_ANALYSIS.md`
- **Management Guide**: `docs/DATASET_MANAGEMENT.md`
- **Deployment Guide**: `huggingface_space_deploy/DEPLOYMENT_GUIDE.md`
- **Implementation**: `AUTO_DATASET_IMPLEMENTATION.md`

## ⏱️ Expected Times

- **Minimal phase**: 10-20 min download
- **Balanced phase**: 30-60 min download
- **Comprehensive phase**: 60-120 min download
- **Cached restart**: 2-3 min (no re-download)

## ✅ All Datasets Licensed

- CC-BY 4.0 (commercial OK)
- Public Domain (no restrictions)
- Research (verify for commercial use)

## 🎉 That's It!

Deploy to HuggingFace and let LEMM handle the rest.
