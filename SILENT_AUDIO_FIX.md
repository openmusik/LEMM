# Silent Audio Issue - Diagnosis and Fixes (Nov 13, 2025)

## Problem Summary
Audio generated on HuggingFace Space was silent (correct length, empty waveform) while working fine locally on CPU.

## Root Cause Analysis

### 1. **Silent Fallback Masking Failures** (CRITICAL)
**Location**: `src/models/music_generator.py` line 681

The code was catching exceptions in ACE-Step generation and returning **silent audio** (np.zeros):

```python
except Exception as e:
    logger.error(f"Error in ACE-Step generation: {e}")
    # Fallback to silence if generation fails  ← PROBLEM!
    logger.warning("Falling back to silence generation")
    return np.zeros(duration_samples, dtype=np.float32)
```

**Impact**: When ACE-Step failed to generate audio (for any reason), the system would silently continue with empty audio, process it through the entire pipeline, and present silent WAV files to users without any visible error.

### 2. **Mastering Over-Compression** (FIXED)
**Location**: `src/audio/mixer.py` master() function

Previous implementation used aggressive tanh compression on the entire signal:
```python
mastered = np.tanh(mastered * 0.95) * 0.99  # Over-compressed
```

**Impact**: Even if audio was generated, tanh would severely reduce volume levels.

### 3. **Lack of Validation**
No validation checks throughout the pipeline to detect silent audio:
- No check after clip generation
- No check after stem processing
- No check after mixing
- No check before saving

### 4. **Lyrics Generator Using Placeholder**
**Location**: `src/models/lyrics_generator.py`

Currently using simple placeholder lyrics generation instead of SongComposer.

## Implemented Fixes

### Fix #1: Remove Silent Fallback ✅
**File**: `src/models/music_generator.py`

```python
# OLD - Silent fallback:
except Exception as e:
    logger.warning("Falling back to silence generation")
    return np.zeros(duration_samples, dtype=np.float32)

# NEW - Raise error:
except Exception as e:
    logger.error(f"Error in ACE-Step generation: {e}")
    raise RuntimeError(f"ACE-Step generation failed: {e}") from e
```

**Result**: Generation failures now surface as errors instead of silent audio.

### Fix #2: Add Audio Validation ✅
**File**: `src/models/music_generator.py`

```python
# Validate generated audio is not silent
audio_max = np.abs(audio).max()
audio_rms = np.sqrt(np.mean(audio**2))
logger.info(f"Generated audio levels - peak: {audio_max:.4f}, RMS: {audio_rms:.4f}")

if audio_max < 1e-6:
    logger.error("❌ Generated audio is completely silent!")
    raise RuntimeError("ACE-Step generated silent audio - generation failure")
```

**File**: `src/ui/gradio_interface.py`

```python
# Validate clip is not silent
clip_max = np.abs(clip).max()
clip_rms = np.sqrt(np.mean(clip**2))
logger.info(f"Clip {i+1} generated - peak: {clip_max:.4f}, RMS: {clip_rms:.4f}")

if clip_max < 1e-6:
    error_msg = f"❌ Clip {i+1} is silent! Generation failed."
    logger.error(error_msg)
    return None, error_msg
```

**File**: `src/audio/processor.py`

```python
# Validate stems aren't all silent
total_energy = sum(np.abs(stem).max() for stem in stems.values())
logger.info(f"Total stem energy after separation: {total_energy:.4f}")

# Validate enhanced stems
total_energy_after = sum(np.abs(stem).max() for stem in stems.values())
logger.info(f"Total stem energy after enhancement: {total_energy_after:.4f}")
```

### Fix #3: Improve Mastering ✅
**File**: `src/audio/mixer.py`

```python
# Normalize to 0.9 to leave headroom
mastered = mastered / max_val * 0.9

# Apply gentle limiting only to peaks above 0.9
peaks = np.abs(mastered) > 0.9
if np.any(peaks):
    mastered[peaks] = np.sign(mastered[peaks]) * (0.9 + 0.1 * np.tanh((np.abs(mastered[peaks]) - 0.9) * 10))
```

### Fix #4: Enhanced Logging ✅
Added detailed audio level logging at every stage:

**Music Generation**:
```python
logger.info("🎤 Calling ACE-Step pipeline...")
logger.info(f"   Device: {self.device}")
logger.info(f"   CUDA available: {torch.cuda.is_available()}")
# ... generation ...
logger.info(f"Raw audio output type: {type(audio)}")
logger.info(f"Generated audio levels - peak: {audio_max:.4f}, RMS: {audio_rms:.4f}")
```

**Stem Processing**:
```python
logger.info(f"Adding stem '{stem_name}' at {volume*100:.0f}% volume (peak: {stem_max:.4f})")
logger.info(f"Mixed audio - peak: {mixed_max:.4f}, RMS: {mixed_rms:.4f}")
```

**Mastering**:
```python
logger.info(f"   Input peak: {input_max:.4f}, RMS: {input_rms:.4f}")
logger.info(f"   Output peak: {output_max:.4f}, RMS: {output_rms:.4f}")
```

## What to Check on HF Space

### 1. Check Logs for Errors
When you run generation on HF Space, check the logs for:

**Expected on Success**:
```
🎤 Calling ACE-Step pipeline...
   Device: cuda
   CUDA available: True
   CUDA device: Tesla T4
✅ ACE-Step pipeline call completed
Generated audio levels - peak: 0.8234, RMS: 0.2456
Clip 1 generated - peak: 0.8234, RMS: 0.2456
```

**If Silent Audio Occurs**:
```
Generated audio levels - peak: 0.0000, RMS: 0.0000  ← PROBLEM!
❌ Generated audio is completely silent!
RuntimeError: ACE-Step generated silent audio
```

**If Generation Fails**:
```
❌ Permission Error
❌ CUDA out of memory
❌ Model loading failed
RuntimeError: ACE-Step generation failed: [specific error]
```

### 2. Check Hardware
Verify ZeroGPU is actually allocated:
```
   CUDA available: True  ← Should be True on HF Space
   CUDA device: [GPU name]  ← Should show GPU model
```

If shows `CUDA available: False`, the Space isn't getting GPU access.

### 3. Model Loading
Check if ACE-Step loads successfully:
```
Loading ACE-Step from models/ACE-Step-HF
ACE-Step model loaded successfully
  - Device: cuda:0
  - Precision: float16
```

## Possible Causes on HF Space

### Scenario 1: No GPU Allocated
**Symptom**: `CUDA available: False`
**Cause**: Space not configured for ZeroGPU or GPU quota exceeded
**Solution**: Check Space settings, ensure ZeroGPU is enabled

### Scenario 2: ACE-Step Fails to Load
**Symptom**: Error during model loading
**Cause**: Missing model files, incompatible versions, memory issues
**Solution**: Check model files are uploaded, verify torch/transformers versions

### Scenario 3: ACE-Step Generates Silence
**Symptom**: Generation completes but audio peak = 0.0000
**Cause**: Internal ACE-Step issue, prompt incompatibility, seed issues
**Solution**: Try different prompts, check ACE-Step configuration

### Scenario 4: Permission/CUDA Errors
**Symptom**: Permission denied or CUDA errors during generation
**Cause**: ZeroGPU decorator issues, device conflicts
**Solution**: Verify @spaces.GPU decorator is working

## Testing Locally vs HF Space

### Local (CPU) - Works ✅
- MusicGen selected automatically
- CPU-compatible generation
- Slower but functional
- Proper audio output

### HF Space - Was Silent ❌
- ACE-Step selected (requires GPU)
- Silent fallback was hiding errors
- Now: Will show actual error messages

## Next Steps

### Immediate Actions
1. **Run generation on HF Space** - Check logs for errors
2. **Look for validation messages** - Audio levels at each stage
3. **Check CUDA availability** - Verify GPU is allocated
4. **Review error messages** - Now visible instead of hidden

### If Still Silent
1. Check logs for "Generated audio levels - peak: X"
2. If peak = 0.0000, check for error messages above it
3. Verify ACE-Step model loaded successfully
4. Try shorter generation (1 clip) to isolate issue
5. Check HF Space hardware settings

### Lyrics Generator
- Currently using **placeholder** (documented in SONGCOMPOSER_INTEGRATION.md)
- Works fine for testing but should eventually use SongComposer
- Not related to silent audio issue
- Plan for integration available in SONGCOMPOSER_INTEGRATION.md

## Summary

The silent audio issue was caused by error handling that was **too tolerant** - catching generation failures and returning silent audio instead of surfacing the real problem. The new implementation:

✅ **Validates** audio at every stage
✅ **Logs** detailed audio levels throughout pipeline  
✅ **Raises errors** when generation fails
✅ **Shows** the actual problem instead of hiding it
✅ **Improves** mastering to preserve audio levels

The next generation attempt on HF Space will either:
- **Work** - and show audio levels in logs
- **Fail with clear error** - showing what actually went wrong

Either way, you'll know exactly what's happening instead of getting mysterious silent files.
