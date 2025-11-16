# Requirements Consolidation Report

## Changes Made (Nov 11, 2025)

### Problem
- Two conflicting requirements files
- `requirements.txt` had wrong packages and vague versions
- `requirements_space.txt` was correct but not being used

### Solution
✅ **Replaced Space's `requirements.txt` with optimized version**
✅ **Added `pyproject.toml` for Python version enforcement**

### What's Now in requirements.txt

**Essential Only** (removed bloat):
```
spaces                   # ZeroGPU
torch==2.5.1            # Fixed versions
torchaudio==2.5.1
torchvision==0.20.1
demucs==4.0.1
pedalboard==0.9.19
librosa==0.11.0
gradio==5.49.1
numpy, pyyaml, loguru
```

**Removed Unnecessary**:
- transformers, diffusers, accelerate, peft (not used)
- spleeter (using demucs instead)
- scipy (not needed)

### Python Version Protection (4 Layers)

1. `.python-version` → 3.10.11
2. `runtime.txt` → python-3.10.11
3. `pyproject.toml` → requires-python = ">=3.10,<3.13"
4. `README.md` → python_version: "3.10"

### Benefits
- ✅ Faster builds
- ✅ No version conflicts
- ✅ pip enforces Python 3.10+
- ✅ Reproducible environment

**Deployed**: Commit db4195b
