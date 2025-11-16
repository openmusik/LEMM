# Music & Audio Training Datasets Analysis
## Comprehensive Review for LEMM Project

**Date**: November 12, 2025  
**Purpose**: Evaluate datasets for training MusicGen, ACE-Step, and vocal synthesis models

---

## 📋 Executive Summary

### Recommended Datasets (Open License, Manageable Size)

| Dataset | Size | License | Best For | Priority |
|---------|------|---------|----------|----------|
| **NSynth** | 30GB | CC-BY 4.0 | Instrument timbre, music synthesis | ⭐⭐⭐⭐⭐ |
| **LJ Speech** | 2.6GB | Public Domain | Voice synthesis (single speaker) | ⭐⭐⭐⭐⭐ |
| **LibriTTS** | ~60GB | CC-BY 4.0 | Multi-speaker TTS | ⭐⭐⭐⭐ |
| **FMA (Free Music Archive)** | 879GB full | CC licenses | Music genre, style classification | ⭐⭐⭐⭐ |
| **URMP** | 12.5GB | Research use | Multi-instrument orchestration | ⭐⭐⭐⭐ |
| **MusicNet** | ~6GB | CC-BY 4.0 | Classical music notation | ⭐⭐⭐ |
| **MUSDB18** | ~10GB | CC-BY-NC-SA 4.0 | Stem separation training | ⭐⭐⭐⭐ |

**Total Recommended**: ~130GB (without FMA full)  
**With FMA subset**: ~180GB

---

## 🎵 MUSIC DATASETS (Detailed Analysis)

### 1. ⭐ NSynth (HIGHLY RECOMMENDED)
- **Size**: ~30GB uncompressed (full dataset)
- **License**: ✅ **CC-BY 4.0** (Commercial use allowed)
- **Content**: 305,979 musical notes across 1,006 instruments
- **Format**: 16kHz, 4-second WAV files + TFRecord
- **Annotations**: Instrument family, source (acoustic/electronic/synthetic), pitch, velocity, sonic qualities
- **Best For**:
  - Training instrument synthesizers
  - Timbre transfer
  - Music generation models
  - Sound design AI

**Why This Matters**: Perfect for fine-tuning MusicGen or ACE-Step on specific instrument timbres. High quality, well-annotated, permissive license.

**Download**: https://magenta.tensorflow.org/datasets/nsynth

---

### 2. ⭐ MAESTRO v3.0.0 (RECOMMENDED with caution)
- **Size**: 120GB uncompressed (MIDI-only: 81MB)
- **License**: ⚠️ **CC-BY-NC-SA 4.0** (Non-commercial only!)
- **Content**: 200 hours of virtuosic piano performances
- **Format**: 44.1-48kHz 16-bit PCM stereo + aligned MIDI
- **Annotations**: Composer, title, year, beat/tempo/key
- **Best For**:
  - Piano-specific generation
  - MIDI-to-audio alignment research
  - Performance analysis

**Limitation**: Non-commercial license makes it unsuitable if LEMM will be commercialized.

**Alternative**: Use MIDI-only version (81MB) for research, avoid audio for commercial deployment.

---

### 3. ⚠️ Lakh MIDI Dataset
- **Size**: Variable (MIDI files are small, ~500MB total)
- **License**: ✅ **CC-BY 4.0**
- **Content**: 176,581 unique MIDI files (45,129 matched to Million Song Dataset)
- **Format**: MIDI + optional audio alignment
- **Best For**:
  - Symbolic music generation
  - Music structure analysis
  - Lyrics-to-melody training

**Note**: MIDI-only, no audio. Useful for training melody/harmony models but not audio synthesis.

---

### 4. ⭐ URMP (University of Rochester Multi-Modal Music Performance)
- **Size**: **12.5GB**
- **License**: ✅ Research use (appears to be permissive, check documentation)
- **Content**: 44 multi-instrument classical pieces
- **Format**: Individual instrument tracks + video + MIDI scores + annotations
- **Annotations**: Pitch/note per instrument, beat, form
- **Best For**:
  - Multi-instrument generation
  - Source separation
  - Orchestration AI
  - Performance analysis

**Why Valuable**: Individual instrument stems make this perfect for training MusicGen on multi-instrument coordination.

**Download**: https://labsites.rochester.edu/air/projects/URMP.html

---

### 5. ⭐ FMA (Free Music Archive)
- **Size**:
  - Small: 8GB (8,000 tracks, 30s clips)
  - Medium: 25GB (25,000 tracks, 30s clips)
  - Large: 106GB (106,000 tracks, 30s clips)
  - Full: **879GB** (106,574 full tracks)
- **License**: ✅ **CC licenses** (various, mostly permissive)
- **Content**: 161 genres, comprehensive metadata
- **Format**: MP3, variable quality
- **Annotations**: Genre, tags, user metadata, audio features

**Recommendation**: Start with "Small" (8GB) or "Medium" (25GB) subset.

**Download**: https://github.com/mdeff/fma

---

### 6. MusicNet
- **Size**: ~6GB
- **License**: ✅ **CC-BY 4.0**
- **Content**: 330 classical music recordings with 1M+ note annotations
- **Format**: WAV + MIDI alignments
- **Best For**: Note transcription, classical music generation

---

### 7. MUSDB18
- **Size**: ~10GB
- **License**: ⚠️ **CC-BY-NC-SA 4.0** (Non-commercial)
- **Content**: 150 full-length tracks with stems (drums, bass, vocals, other)
- **Format**: WAV, 44.1kHz stereo
- **Best For**: Stem separation training (Demucs, etc.)

**Note**: Perfect for training your stem separation component, but non-commercial license.

---

### 8. ❌ DISCO-10M (NOT FOUND)
- **Status**: Could not locate this dataset
- The GitHub and HuggingFace links are broken
- May be discontinued or moved

---

## 🎤 SPEECH/VOCAL DATASETS

### 1. ⭐⭐⭐⭐⭐ LJ Speech (ESSENTIAL)
- **Size**: **2.6GB**
- **License**: ✅ **Public Domain**
- **Content**: 13,100 short clips (24 hours total), single female speaker
- **Format**: 22kHz WAV + transcriptions
- **Best For**:
  - TTS training
  - Voice synthesis foundation
  - Vocal quality baseline

**Why Essential**: Free, high-quality, perfect for training your `VocalSynthesizer` module.

**Download**: https://keithito.com/LJ-Speech-Dataset/

---

### 2. ⭐⭐⭐⭐ LibriTTS
- **Size**: ~60GB (LibriTTS-R: improved quality)
- **License**: ✅ **CC-BY 4.0**
- **Content**: 585 hours, 2,456 speakers, read English speech
- **Format**: 24kHz WAV + text
- **Best For**:
  - Multi-speaker TTS
  - Voice cloning
  - Prosody modeling

**Download**: http://www.openslr.org/60

---

### 3. Common Voice (Mozilla)
- **Size**: Varies by language (English ~90GB)
- **License**: ✅ **CC-0** (Public Domain)
- **Content**: 9,283 hours across 60+ languages
- **Format**: MP3 + transcriptions
- **Best For**:
  - Multilingual TTS
  - Accent diversity
  - Speech recognition

---

### 4. VCTK (Voice Cloning Toolkit)
- **Size**: ~11GB
- **License**: ✅ Open Data Commons
- **Content**: 110 English speakers, 400 sentences each
- **Format**: 48kHz WAV
- **Best For**: Voice cloning, speaker diversity

---

## 🔊 SOUND EFFECTS DATASETS

### 1. FSD50K (Freesound Dataset 50K)
- **Size**: ~40GB
- **License**: ✅ **CC licenses** (various)
- **Content**: 51,197 clips, 200 sound event classes
- **Best For**: Sound effect generation, environmental audio

---

### 2. ESC-50 (Environmental Sound Classification)
- **Size**: ~600MB
- **License**: ✅ **CC-BY** (most files)
- **Content**: 2,000 5-second clips, 50 classes
- **Best For**: Quick sound effect training

---

### 3. AudioSet (Google)
- **Size**: Metadata only (~2M YouTube IDs)
- **License**: ⚠️ YouTube ToS
- **Content**: 632 audio event classes
- **Note**: You must download from YouTube yourself

---

## 🚫 DATASETS TO AVOID

### MAESTRO
- **Issue**: NC license (non-commercial)
- **Use Case**: Research only

### Million Song Dataset
- **Issue**: Metadata only, no audio
- **Alternative**: Use Lakh MIDI for symbolic data

### DISCO-10M
- **Issue**: Not found/unavailable

---

## 💾 STORAGE RECOMMENDATIONS

### Minimal Configuration (~50GB)
```
NSynth (full):        30GB  ⭐⭐⭐⭐⭐
LJ Speech:             3GB  ⭐⭐⭐⭐⭐
URMP:                 13GB  ⭐⭐⭐⭐
FMA (small):           8GB  ⭐⭐⭐
----------------------------------------
TOTAL:                54GB
```

### Balanced Configuration (~200GB)
```
NSynth (full):        30GB
LJ Speech:             3GB
LibriTTS:             60GB
URMP:                 13GB
FMA (large):         106GB
MusicNet:              6GB
MUSDB18:              10GB
Lakh MIDI:             1GB
FSD50K:               40GB
----------------------------------------
TOTAL:               269GB
```

### Comprehensive Configuration (~900GB)
```
All of above +
FMA (full):          879GB
LibriSpeech (full):  60GB
Common Voice (en):   90GB
----------------------------------------
TOTAL:             1,298GB
```

---

## 📝 LICENSE SUMMARY

### ✅ Fully Open (Commercial OK)
- **CC-BY 4.0**: NSynth, LibriTTS, Lakh MIDI, MusicNet
- **CC-0/Public Domain**: LJ Speech, Common Voice
- **MIT/Apache**: (Check individual FMA tracks)

### ⚠️ Research Only (Non-Commercial)
- **CC-BY-NC-SA 4.0**: MAESTRO, MUSDB18

### ⚠️ Requires Individual Checking
- **FMA**: Mixed CC licenses per track (mostly permissive)
- **FSD50K**: Mixed CC licenses per sound

---

## 🎯 RECOMMENDED ACTION PLAN

### Phase 1: Foundation (54GB) - START HERE
1. **Download NSynth** (30GB) - Core music synthesis
2. **Download LJ Speech** (3GB) - Vocal synthesis baseline
3. **Download URMP** (13GB) - Multi-instrument coordination
4. **Download FMA Small** (8GB) - Genre diversity

### Phase 2: Enhancement (~150GB additional)
5. **LibriTTS** (60GB) - Multi-speaker vocals
6. **FMA Large** (106GB) - Expand genre coverage
7. **MUSDB18** (10GB) - Stem separation training
   - **Note**: Check if commercial use intended

### Phase 3: Specialization (as needed)
8. **MusicNet** (6GB) - Classical music notation
9. **FSD50K** (40GB) - Sound effects
10. **Lakh MIDI** (1GB) - Symbolic music

---

## 🔍 DATASET PRIORITIES FOR LEMM

### For MusicGen Training:
1. **NSynth** - Instrument diversity ⭐⭐⭐⭐⭐
2. **FMA** - Genre/style variety ⭐⭐⭐⭐⭐
3. **URMP** - Multi-instrument ⭐⭐⭐⭐
4. **MusicNet** - Classical structure ⭐⭐⭐

### For Vocal Synthesis:
1. **LJ Speech** - Foundation ⭐⭐⭐⭐⭐
2. **LibriTTS** - Multi-speaker ⭐⭐⭐⭐
3. **VCTK** - Voice diversity ⭐⭐⭐

### For Stem Separation (Demucs):
1. **MUSDB18** - High quality stems ⭐⭐⭐⭐⭐

---

## ⚖️ FINAL RECOMMENDATION

**Start with Phase 1 (54GB)** to establish a solid foundation without overwhelming your storage. This gives you:
- High-quality instrument synthesis (NSynth)
- Vocal synthesis capability (LJ Speech)
- Multi-instrument coordination (URMP)
- Genre diversity (FMA Small)

All are **commercially usable** with proper attribution.

**Avoid**:
- MAESTRO (unless research-only)
- MUSDB18 (unless non-commercial)
- Any dataset you can't verify the license

**Monitor storage** and expand to Phase 2 once you've validated the training pipeline with Phase 1 datasets.
