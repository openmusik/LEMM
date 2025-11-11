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
python_version: 3.10
suggested_hardware: h200
suggested_storage: small
---

# LEMM - Let Everyone Make Music

An AI-powered music generation system that creates complete songs from text prompts.

**ZeroGPU Compatible** - Optimized for HuggingFace's free H200 GPU allocation!

## Features
- 🎼 AI Music Generation with ACE-Step
- 📝 Auto-Lyrics Generation
- 🎛️ Professional Audio Processing
- 🎸 Stem Separation & Enhancement
- 🎨 LoRA Fine-tuning Support
- ⚡ ZeroGPU Support for Free GPU Access

## Usage
1. Enter a text description of your desired song
2. Optionally add or generate lyrics
3. Choose the number of 32-second clips
4. Click Generate and wait for your AI-created music!

## Technical Details
- **Model**: ACE-Step v1-3.5B
- **Python**: 3.10
- **GPU**: Required for optimal performance

## Note
First run may take 2-3 minutes to load models. Generation time depends on the number of clips requested.
