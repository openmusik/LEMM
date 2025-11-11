# LEMM Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LEMM MUSIC GENERATION PIPELINE                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: INPUT & ANALYSIS                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ User Prompt  │
    │ (Text Input) │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────┐
    │ Prompt Analyzer     │
    │ - Extract Genre     │
    │ - Extract Style     │
    │ - Extract Tempo     │
    │ - Extract Instruments│
    │ - Extract Mood      │
    └──────┬──────────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
    ┌─────────────┐        ┌──────────────────┐
    │  Metadata   │        │ Auto-Lyrics      │
    │  Storage    │        │ Button Pressed?  │
    └─────────────┘        └────┬─────────────┘
                                │ (Yes)
                                ▼
                         ┌──────────────────┐
                         │  SongComposer    │
                         │  Generate Lyrics │
                         └────┬─────────────┘
                              │
                              ▼
                         ┌──────────────────┐
                         │ Lyrics Text Area │
                         └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: CLIP GENERATION (32-second clips)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────────────┐
    │ For Each Clip (1, 2, 3, ... N)             │
    └────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────┐
    │ ACE-Step Model                  │
    │ Input:                          │
    │  - Prompt Analysis (Genre, etc) │
    │  - Lyrics (if provided)         │
    │  - Previous Clip (if not first) │
    │ Output:                         │
    │  - 32-second audio clip         │
    │    • 2s lead-in                 │
    │    • 28s main content           │
    │    • 2s lead-out                │
    └──────┬──────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────┐
    │ MusicControlNet                 │
    │ - Condition next clip           │
    │ - Use lead-out for continuity   │
    └──────┬──────────────────────────┘
           │
           ▼
    [Clip saved to buffer]

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: STEM SEPARATION                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │ Generated Clip   │
    └────┬─────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │ Demucs / Spleeter        │
    │ Stem Separation          │
    └────┬─────────────────────┘
         │
         ├─────────┬─────────┬─────────┬─────────┐
         ▼         ▼         ▼         ▼         ▼
    ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌───────┐
    │ Vocals │ │ Bass │ │Drums │ │Guitar│ │ Other │
    └────┬───┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬───┘
         │         │        │        │        │
         │         └────────┴────────┴────────┘
         │                  │
         │                  │ (Non-vocal stems)
         │                  │
         ▼                  ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: ENHANCEMENT                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐       ┌────────────────────────┐
    │ Vocal Stem       │       │ Non-Vocal Stems        │
    └────┬─────────────┘       └────┬───────────────────┘
         │                          │
         ▼                          ▼
    ┌──────────────────┐       ┌────────────────────────┐
    │ so-vits-svc      │       │ Pedalboard             │
    │ - Pitch correct  │       │ - EQ                   │
    │ - Tone enhance   │       │ - Compression          │
    │ - Clarity boost  │       │ - Reverb               │
    └────┬─────────────┘       │ - Stereo widening      │
         │                     └────┬───────────────────┘
         │                          │
         └───────────┬──────────────┘
                     │
                     ▼
             ┌───────────────┐
             │ Enhanced Stems│
             └───────┬───────┘
                     │
                     ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: MIXING & CHAINING                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────┐
    │ For Each Clip:                   │
    │ Mix Enhanced Stems               │
    │ (Pydub + Librosa)                │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ Clip Chaining                    │
    │ - Use lead-in/lead-out           │
    │ - Cross-fade (2 seconds)         │
    │ - Beat alignment (Librosa)       │
    │ - Smooth transitions             │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ Final Mix                        │
    │ - Mastering EQ                   │
    │ - Limiter                        │
    │ - Normalization                  │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ Export Final Song                │
    │ - WAV (lossless)                 │
    │ - MP3 (compressed)               │
    └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ OPTIONAL: LORA TRAINING PIPELINE                                            │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────┐
    │ Training Data            │
    │ - Audio samples          │
    │ - Metadata/Tags          │
    └────┬─────────────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │ Data Preprocessing       │
    │ - Normalize              │
    │ - Segment                │
    │ - Augment                │
    └────┬─────────────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │ LoRA Fine-tuning         │
    │ - ACE-Step model         │
    │ - Low-rank adaptation    │
    │ - Custom style training  │
    └────┬─────────────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │ Save LoRA Weights        │
    │ - Merge option           │
    │ - Checkpoint system      │
    └──────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ GRADIO UI LAYOUT                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────────────────────────┐
    │ LEMM - Let Everyone Make Music                        │
    ├────────────────────────────────────────────────────────┤
    │                                                        │
    │ [Text Input: Prompt]                                   │
    │ "Create a upbeat pop song with guitars..."            │
    │                                                        │
    │ [Auto-Lyrics Button] [Generate Song Button]           │
    │                                                        │
    │ [Text Area: Lyrics]                                    │
    │ (Generated or manual lyrics)                           │
    │                                                        │
    │ Settings:                                              │
    │ - Number of Clips: [Slider: 1-10]                     │
    │ - Use LoRA Model: [Checkbox]                          │
    │ - LoRA Path: [File Selector]                          │
    │ - Temperature: [Slider: 0.1-2.0]                      │
    │                                                        │
    │ [Progress Bar]                                         │
    │                                                        │
    │ [Audio Player: Generated Song]                         │
    │                                                        │
    │ [Download WAV] [Download MP3]                          │
    │                                                        │
    │ Advanced:                                              │
    │ - [Tab: Training] [Tab: Settings] [Tab: About]        │
    │                                                        │
    └────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DATA FLOW SUMMARY                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

    Prompt → Analysis → Lyrics (optional) → ACE-Step Generation →
    Stem Separation → Enhancement (Vocal: so-vits-svc, Other: Pedalboard) →
    Mixing → Chaining → Final Output

┌─────────────────────────────────────────────────────────────────────────────┐
│ KEY TECHNICAL COMPONENTS                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    1. Prompt Analysis: NLP/LLM for extracting musical attributes
    2. Lyrics Generation: SongComposer model
    3. Music Generation: ACE-Step (conditioned generation)
    4. Conditioning: MusicControlNet (clip continuity)
    5. Stem Separation: Demucs/Spleeter (source separation)
    6. Vocal Enhancement: so-vits-svc (voice conversion/enhancement)
    7. Audio Enhancement: Pedalboard (audio effects)
    8. Mixing/Chaining: Pydub + Librosa (audio manipulation)
    9. Training: LoRA (efficient fine-tuning)
    10. UI: Gradio (web interface)
```

## Processing Time Estimates

- **Prompt Analysis**: < 1 second
- **Lyrics Generation**: 5-10 seconds
- **Per Clip Generation (ACE-Step)**: 30-60 seconds
- **Stem Separation**: 10-20 seconds per clip
- **Enhancement**: 5-15 seconds per clip
- **Mixing/Chaining**: 5-10 seconds per clip
- **Total for 3-clip song**: ~3-5 minutes

## Resource Requirements

- **GPU**: Recommended NVIDIA GPU with 8GB+ VRAM
- **RAM**: 16GB+ recommended
- **Storage**: 10GB+ for models, additional for output
- **CUDA**: Required for optimal performance
