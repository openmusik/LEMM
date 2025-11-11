# Changelog

All notable changes to LEMM (Let Everyone Make Music) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-10

### Added
- Initial release of LEMM
- ACE-Step integration for AI music generation
- Text-to-music generation from natural language prompts
- Automatic lyrics generation support
- 32-second clip generation (2s lead-in + 28s main + 2s lead-out)
- Gradio web interface for user interaction
- Demucs stem separation (vocals/bass/drums/other)
- Pedalboard audio enhancement for instruments
- Audio mixing with crossfading and mastering
- Support for LoRA model fine-tuning
- Comprehensive logging system
- Python 3.10 environment support
- CUDA/GPU acceleration support
- Configuration management via YAML
- Version tracking system (v0.1.0)

### Fixed
- Type error in gradio_interface.py (return value consistency)
- ACEStepPipeline import resolution with proper type checking
- Pipeline None checks with runtime guards
- Pedalboard import and usage throughout audio processor
- Added comprehensive error handling and logging
- Graceful fallbacks for missing optional dependencies

### Technical Details
- **Models**: ACE-Step v1-3.5B, So-VITS-SVC
- **Audio Processing**: Demucs 4.0.1, Pedalboard 0.9.19
- **Framework**: PyTorch 2.5.1, Gradio 5.49.1
- **Python Version**: 3.10.11 required (ACE-Step compatibility)

### Known Issues
- ACE-Step model loading takes 1-2 minutes on first run
- Requires CUDA-capable GPU with 8GB+ VRAM for optimal performance
- LoRA training features are implemented but not yet fully tested

### Documentation
- Complete README with installation instructions
- WORKFLOW.md with detailed pipeline documentation
- PYTHON_310_SETUP.md for environment setup
- ERROR_FIXES.md documenting all fixes and improvements
- Installation verification scripts

---

## Version Format

LEMM uses semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Example: Version 1.2.3
- 1 = Major version
- 2 = Minor version (features)
- 3 = Patch version (fixes)
