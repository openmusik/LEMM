# 🎵 LEMM - Let Everyone Make Music

**An AI-Powered Music Generation System** • Version 0.1.0

LEMM is a sophisticated AI-based music generator that creates complete songs from simple text prompts. Using cutting-edge AI models and advanced audio processing techniques, LEMM enables anyone to create professional-quality music.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/yourusername/lemm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎼 **AI Music Generation**: Generate music using state-of-the-art ACE-Step model
- 📝 **Auto-Lyrics Generation**: Create lyrics automatically with SongComposer
- 🎛️ **Advanced Audio Processing**: Professional-grade stem separation and enhancement
- 🔗 **Seamless Clip Chaining**: Smart clip chaining with MusicControlNet conditioning
- 🎤 **Vocal Enhancement**: Crystal-clear vocals using so-vits-svc
- 🎸 **Instrument Enhancement**: Enhanced audio quality with Pedalboard effects
- 🎚️ **Professional Mixing**: Automated mixing with Pydub and Librosa
- 🎨 **LoRA Training**: Train custom music styles with LoRA fine-tuning
- 🌐 **Web Interface**: User-friendly Gradio interface

## 🏗️ Architecture

LEMM uses a multi-stage pipeline for music generation:

```
Prompt → Analysis → Lyrics → Generation → Stems → Enhancement → Mixing → Output
```

### Key Components

1. **Prompt Analyzer**: Extracts genre, style, tempo, mood, and instruments
2. **Lyrics Generator**: SongComposer-based lyric generation
3. **Music Generator**: ACE-Step for 32-second clips with lead-in/lead-out
4. **MusicControlNet**: Conditions each clip based on the previous one
5. **Stem Separator**: Demucs/Spleeter for source separation
6. **Vocal Enhancer**: so-vits-svc for vocal processing
7. **Audio Enhancer**: Pedalboard for instrument effects
8. **Audio Mixer**: Chains clips with crossfading and final mastering

## 📋 Requirements

### System Requirements

- **OS**: Windows, Linux, or macOS
- **Python**: **3.10-3.12 REQUIRED** (ACE-Step not compatible with 3.13+)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (recommended)
- **RAM**: 16GB+ recommended
- **Storage**: 10GB+ for models
- **CUDA**: 12.1+ (for GPU acceleration)

### Software Requirements

- Python 3.10-3.12 **(REQUIRED for ACE-Step compatibility)**
- CUDA-compatible GPU drivers (for GPU acceleration)
- FFmpeg (for audio conversion)

## 🚀 Installation

### Quick Start (Windows)

1. **Install Python 3.10** (see `PYTHON_310_SETUP.md` for detailed guide)
   - Download: https://www.python.org/downloads/release/python-31011/
   - Make sure to add to PATH during installation

2. **Run the automated setup script**:
   ```powershell
   .\setup.ps1
   ```

3. **Alternative: Manual Installation**:

```bash
# Create Python 3.10 virtual environment
py -3.10 -m venv .venv310

# Activate (Windows)
.\.venv310\Scripts\Activate.ps1

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ACE-Step (this takes 10-15 minutes)
pip install git+https://github.com/ACE-Step/ACE-Step.git

# Install other dependencies
pip install -r requirements.txt
```

### Linux/macOS Installation

```bash
# Create Python 3.10 virtual environment
python3.10 -m venv .venv310

# Activate
source .venv310/bin/activate

# Install PyTorch with CUDA (Linux) or CPU (macOS)
# Linux:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# macOS:
pip install torch torchvision torchaudio

# Install ACE-Step
pip install git+https://github.com/ACE-Step/ACE-Step.git

# Install other dependencies
pip install -r requirements.txt
```
pip install -r requirements.txt
```

### 4. Download Models

Download the required models and place them in the `models/` directory:

- **ACE-Step**: Place in `models/ace_step/`
- **SongComposer**: Place in `models/song_composer/`
- **MusicControlNet**: Place in `models/music_control_net/`
- **so-vits-svc**: Place in `models/so_vits_svc/`

> **Note**: Model download links and instructions will be provided separately due to their size and licensing requirements.

### 5. Configure Settings

Edit `config/config.yaml` to customize:

- Model paths
- Audio settings
- Generation parameters
- Output preferences

## 🎮 Usage

### Basic Usage

1. **Start the application**:

```bash
python main.py
```

2. **Open your browser** to `http://localhost:7860`

3. **Generate music**:
   - Enter a prompt describing your desired song
   - (Optional) Click "Auto-Generate Lyrics" or enter your own
   - Adjust settings (number of clips, temperature, etc.)
   - Click "Generate Song"

### Example Prompts

```
"An upbeat pop song with electric guitars and synths, energetic and fun"

"A calm acoustic ballad with piano and strings, melancholic and emotional"

"Fast-paced electronic dance music with heavy bass, 140 BPM"

"Jazz fusion with saxophone and piano, smooth and sophisticated"
```

### Advanced Features

#### Using LoRA Models

1. Train a custom LoRA model using the Training tab
2. Enable "Use LoRA Model" in settings
3. Select your trained LoRA weights
4. Generate music with your custom style

#### Exporting Stems

Set `export_stems: true` in `config/config.yaml` to save individual instrument stems.

## 🎓 How It Works

### Clip Structure

Each 32-second clip consists of:
- **2 seconds**: Lead-in (for smooth transitions)
- **28 seconds**: Main content
- **2 seconds**: Lead-out (for chaining)

### Generation Process

1. **Prompt Analysis** (< 1s)
   - Extracts musical attributes using NLP

2. **Lyrics Generation** (5-10s)
   - Optional automatic lyric generation

3. **Clip Generation** (30-60s per clip)
   - ACE-Step generates each 32-second clip
   - MusicControlNet conditions on previous clip

4. **Stem Separation** (10-20s per clip)
   - Demucs separates vocals, bass, drums, and other instruments

5. **Enhancement** (5-15s per clip)
   - Vocals: so-vits-svc enhancement
   - Instruments: Pedalboard effects (EQ, compression, reverb)

6. **Mixing & Chaining** (5-10s per clip)
   - Stems mixed back together
   - Clips chained with 2-second crossfades
   - Final mastering applied

**Total time for 3-clip song**: ~3-5 minutes

## 📁 Project Structure

```
lemm_beta/
├── .github/
│   └── copilot-instructions.md
├── config/
│   └── config.yaml
├── docs/
│   └── WORKFLOW.md
├── logs/
├── models/
│   ├── ace_step/
│   ├── song_composer/
│   ├── music_control_net/
│   └── so_vits_svc/
├── output/
├── src/
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   └── mixer.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prompt_analyzer.py
│   │   ├── lyrics_generator.py
│   │   └── music_generator.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── gradio_interface.py
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py
│       └── file_manager.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Configuration

### Audio Settings

```yaml
audio:
  sample_rate: 44100
  clip_duration: 32
  crossfade_duration: 2
```

### Generation Settings

```yaml
generation:
  default_clips: 3  # Number of clips (each 32s)
  max_clips: 10
  temperature: 1.0  # Higher = more creative
  top_p: 0.95
```

### Model Settings

```yaml
models:
  ace_step:
    device: "cuda"  # or "cpu"
    dtype: "float16"  # or "float32"
```

## 🎯 Training Custom Models (LoRA)

1. **Prepare Training Data**:
   - Collect audio files in your desired style
   - Place in a training directory

2. **Configure Training**:
   ```yaml
   training:
     batch_size: 4
     learning_rate: 0.0001
     num_epochs: 10
   ```

3. **Start Training**:
   - Use the Training tab in the UI
   - Upload audio files
   - Set training parameters
   - Click "Start Training"

4. **Use Trained Model**:
   - Load LoRA weights in generation settings
   - Generate music with your custom style

## 🔧 Troubleshooting

### CUDA Out of Memory

- Reduce `batch_size` in config
- Use `dtype: "float16"` instead of `float32`
- Reduce number of clips

### Slow Generation

- Ensure CUDA is properly installed
- Check GPU is being used (`device: "cuda"`)
- Consider using a more powerful GPU

### Poor Audio Quality

- Increase sample rate (if hardware allows)
- Adjust enhancement settings
- Ensure high-quality model weights

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ACE-Step**: Music generation model
- **SongComposer**: Lyrics generation
- **MusicControlNet**: Music conditioning
- **Demucs**: Stem separation by Facebook Research
- **so-vits-svc**: Vocal enhancement
- **Pedalboard**: Audio effects by Spotify
- **Gradio**: Web interface framework

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review the workflow diagram in `docs/WORKFLOW.md`

## 🗺️ Roadmap

- [ ] Real-time generation preview
- [ ] More music styles and genres
- [ ] MIDI export functionality
- [ ] Multi-track editing interface
- [ ] Cloud-based generation option
- [ ] Mobile app support

---

**Made with ❤️ by the LEMM Team**

*Let Everyone Make Music!*
