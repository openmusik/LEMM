# LEMM Version 0.2.0 Release Notes

## Version Update Summary
**Date:** November 12, 2025  
**Version:** 0.2.0 (updated from 0.1.0)

## What's New in 0.2.0

### 🐛 Bug Fixes
1. **Vocals Preservation** - Fixed issue where synthesized vocals were lost in final mix
2. **Lyrics Randomization** - Fixed "Randomize Lyrics" button to generate truly different content
3. **Smooth Endings** - Added exponential fade-out to eliminate garbled song endings

### 🌐 HuggingFace Space Improvements
1. **Output Directory Fix** - Resolved Error 21 by implementing proper file permissions handling
2. **Time Estimate Display** - Fixed time estimate not showing on HF Spaces
3. **Model Selection Visibility** - Made ACE-Step/MusicGen switcher always visible for easy testing

### 🔧 Technical Improvements
- Enhanced file manager with HF Space detection
- Added dual save methods (soundfile + scipy fallback)
- Improved stem mixing balance (vocals 100%, instruments 75-85%)
- Better error handling for restricted environments

### 📦 Dependencies
- Cleaned requirements.txt (removed essentia, aubio, duplicates)
- Added scipy>=1.11.0 for audio fallback
- Consolidated duplicate packages

## Files Updated

### Version Files
- ✅ `src/__version__.py` → 0.2.0
- ✅ `huggingface_space_deploy/src/__version__.py` → 0.2.0
- ✅ `README_Local.md` → Updated badges and header

### Feature Files
- `src/ui/gradio_interface.py` - Time estimate & model selection UI
- `src/audio/mixer.py` - Fade-out implementation
- `src/audio/processor.py` - Vocal preservation fix
- `src/utils/file_manager.py` - HF Space compatibility
- `requirements.txt` - Cleaned dependencies

## Upgrade Notes

### For Local Users
Simply pull the latest changes. No configuration changes needed.

### For HuggingFace Space Deployment
1. Push updated files to your HF Space
2. Time estimates will now display correctly
3. Model selection is now visible by default
4. Audio files will save properly to `/tmp/lemm_output`

## Testing Verification
All changes have been tested and verified:
- ✅ Version displays as 0.2.0
- ✅ Local and HF deployment folders synced
- ✅ All bug fixes validated
- ✅ UI improvements working

## Branch Information
**Branch:** LEMM---Working-Test-Version-0.2.0  
**Status:** Ready for commit and publish

---

**Previous Version:** 0.1.0 (Initial Release)  
**Current Version:** 0.2.0 (Bug Fixes & HF Space Improvements)
