# Deploying LEMM to HuggingFace Spaces

## Complete Step-by-Step Guide

---

## Prerequisites

1. **HuggingFace Account**: Create at https://huggingface.co/join
2. **Git**: Installed and configured
3. **Git LFS**: Required for large files
   ```bash
   git lfs install
   ```

---

## Part 1: Prepare Your Local Repository

### 1. Create Space-Specific Files (Already Done!)

The following files have been created:
- ✅ `app.py` - HuggingFace Space entry point
- ✅ `requirements_space.txt` - Dependencies for the Space
- ✅ `README_SPACE.md` - Space README with metadata

### 2. Update Config for HuggingFace

The `app.py` already handles this automatically by:
- Using `"ACE-Step/ACE-Step-v1-3.5B"` from HuggingFace Hub
- Setting `use_local: false`
- Proper server configuration

---

## Part 2: Create HuggingFace Space

### Method A: Web Interface (Recommended for First Time)

1. **Go to HuggingFace**
   - Visit: https://huggingface.co/new-space

2. **Configure Your Space**
   - **Owner**: Your username
   - **Space name**: `lemm-music-generator` (or your choice)
   - **License**: MIT
   - **Select SDK**: Gradio
   - **SDK Version**: 5.49.1
   - **Python Version**: 3.10
   - **Space hardware**: 
     - Start with **CPU Basic** (free) for testing
     - Upgrade to **T4 small** or **A10G small** for production (paid)
   - **Visibility**: Public or Private

3. **Create Space**
   - Click "Create Space"
   - You'll get a Git repository URL

---

## Part 3: Upload Your Code

### Option 1: Using Git (Recommended)

```bash
# Navigate to your project
cd D:\2025-vibe-coding\lemm_beta

# Initialize git if not already done
git init

# Add HuggingFace Space as remote
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/lemm-music-generator

# Create .gitignore for large files
cat > .gitignore << EOL
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
.venv310/
.venv312/
logs/
output/
models/ACE-Step-HF/
models/ACE-Step-v1-3.5B/
*.log
.DS_Store
EOL

# Prepare Space-specific files
# 1. Copy README for Space
cp README_SPACE.md README.md

# 2. Copy requirements for Space  
cp requirements_space.txt requirements.txt

# 3. Stage all necessary files
git add app.py
git add requirements.txt
git add README.md
git add config/
git add src/
git add .gitignore

# Commit
git commit -m "Initial commit: LEMM v0.1.0 for HuggingFace Space"

# Push to HuggingFace Space
git push space main
```

### Option 2: Using HuggingFace CLI

```bash
# Install HuggingFace CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload files
huggingface-cli upload YOUR_USERNAME/lemm-music-generator . --repo-type=space
```

---

## Part 4: Configure Models (IMPORTANT!)

### ACE-Step Model Access

The ACE-Step model should be automatically downloaded from HuggingFace when your Space starts, but you need to ensure:

1. **Check Model Availability**
   - Visit: https://huggingface.co/ACE-Step/ACE-Step-v1-3.5B
   - If it doesn't exist, you'll need to upload the model

2. **If Model Doesn't Exist on HuggingFace Hub**

   You have two options:

   **Option A: Create Model Repository (Recommended)**
   
   ```bash
   # Create a model repository on HuggingFace
   # Go to: https://huggingface.co/new-model
   # Name it: ace-step-v1-3.5b
   
   # Clone the repo
   git clone https://huggingface.co/YOUR_USERNAME/ace-step-v1-3.5b
   cd ace-step-v1-3.5b
   
   # Copy your local model files
   cp -r D:/2025-vibe-coding/lemm_beta/models/ACE-Step-HF/* .
   
   # Track large files with Git LFS
   git lfs track "*.safetensors"
   git lfs track "*.bin"
   git lfs track "*.pt"
   git lfs track "*.pth"
   
   # Add and commit
   git add .
   git commit -m "Add ACE-Step v1-3.5B model"
   git push
   
   # Then update app.py to use YOUR model:
   # config["models"]["ace_step"]["path"] = "YOUR_USERNAME/ace-step-v1-3.5b"
   ```

   **Option B: Use Spaces Persistent Storage (Easier but Slower)**
   
   - Upgrade your Space to have persistent storage
   - Models will be cached after first download
   - See: https://huggingface.co/docs/hub/spaces-storage

---

## Part 5: Environment Configuration

### Create `.env` file (Optional)

Create a file called `.env` in your Space (through the web interface):

```env
# LEMM Configuration
CONFIG_PATH=config/config.yaml
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
```

---

## Part 6: Launch & Monitor

### 1. Check Build Logs

After pushing, HuggingFace will:
1. Install dependencies (takes 5-10 minutes)
2. Download models (first run only, takes 10-15 minutes)
3. Start the Gradio app

**Monitor at**: `https://huggingface.co/spaces/YOUR_USERNAME/lemm-music-generator`

### 2. Common Build Issues & Solutions

**Issue**: Out of Memory
```
Solution: Upgrade to T4 small or A10G small GPU
```

**Issue**: Dependencies fail to install
```
Solution: Check requirements.txt format, ensure ACE-Step installs correctly
```

**Issue**: Model download timeout
```
Solution: Use persistent storage or upload model to separate repo
```

---

## Part 7: Optimize for HuggingFace Space

### Update `app.py` for better Space experience:

```python
# Add queue for better handling of multiple users
interface.queue(
    max_size=3,  # Max 3 users in queue
    concurrency_count=1  # Process 1 at a time
)

# Add examples
interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    show_error=True,
    enable_queue=True
)
```

---

## Recommended Space Configuration

### For Testing (Free Tier)
- **Hardware**: CPU Basic
- **Note**: Very slow, use for UI testing only

### For Production
- **Hardware**: T4 small ($0.60/hour) or A10G small ($3.15/hour)
- **Persistent Storage**: Upgrade to 20GB+ to cache models
- **Secrets**: Store any API keys in Space settings

---

## Quick Commands Reference

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/lemm-music-generator
cd lemm-music-generator

# Make changes
# ... edit files ...

# Push updates
git add .
git commit -m "Update: description of changes"
git push

# View logs
# Go to web interface -> "Logs" tab
```

---

## Files to Upload

**Required Files** (must upload):
- ✅ `app.py`
- ✅ `requirements.txt` (from requirements_space.txt)
- ✅ `README.md` (from README_SPACE.md)
- ✅ `config/config.yaml`
- ✅ `src/` (entire directory)

**Optional Files**:
- `.env` - Environment variables
- `.gitignore` - Ignore patterns

**DO NOT Upload**:
- `models/` - Too large, download from HuggingFace instead
- `.venv/`, `.venv310/` - Virtual environments
- `logs/`, `output/` - Generated files
- `__pycache__/` - Python cache

---

## Model Download Strategy

Since downloading from HuggingFace is faster than uploading from local:

### Option 1: Use Official ACE-Step (if available)
```python
# In app.py, it's already set to:
config["models"]["ace_step"]["path"] = "ACE-Step/ACE-Step-v1-3.5B"
```

### Option 2: Create Your Own Model Repo
1. Create model repo on HuggingFace
2. Use `huggingface-cli upload` to upload from local
3. Update path in app.py

### Option 3: Use Direct Download in Dockerfile
Create `Dockerfile` in your Space:

```dockerfile
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y git git-lfs ffmpeg

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download models (if needed)
# RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('ACE-Step/ACE-Step-v1-3.5B', local_dir='models/ACE-Step-HF')"

# Expose port
EXPOSE 7860

# Run app
CMD ["python", "app.py"]
```

---

## Testing Your Space

1. **Visit your Space URL**
   - `https://huggingface.co/spaces/YOUR_USERNAME/lemm-music-generator`

2. **Test generation**
   - Enter a simple prompt: "upbeat pop song"
   - Start with 1 clip (32 seconds)
   - Check logs for errors

3. **Monitor performance**
   - Check memory usage
   - Check generation time
   - Upgrade hardware if needed

---

## Estimated Costs

- **Free Tier (CPU)**: $0/month - Very slow, testing only
- **T4 Small (GPU)**: ~$450/month if running 24/7
- **A10G Small (GPU)**: ~$2,300/month if running 24/7

**Recommendation**: Use "Sleep" mode to pause when inactive, or use serverless/on-demand

---

## Next Steps After Deployment

1. ✅ Test the Space with simple prompts
2. ✅ Add example inputs for users
3. ✅ Monitor logs for errors
4. ✅ Optimize for faster loading
5. ✅ Add usage instructions in README
6. ✅ Consider adding authentication for production

---

## Support & Resources

- **HuggingFace Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **Gradio Docs**: https://gradio.app/docs/
- **ACE-Step**: https://github.com/ACE-Step/ACE-Step

---

## Summary: Fastest Deployment Method

```bash
# 1. Create Space on HuggingFace (web interface)
# 2. Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/lemm-music-generator
cd lemm-music-generator

# 3. Copy necessary files
cp /path/to/lemm_beta/app.py .
cp /path/to/lemm_beta/requirements_space.txt requirements.txt
cp /path/to/lemm_beta/README_SPACE.md README.md
cp -r /path/to/lemm_beta/config .
cp -r /path/to/lemm_beta/src .

# 4. Commit and push
git add .
git commit -m "Initial LEMM deployment"
git push

# 5. Wait for build (10-15 minutes)
# 6. Test your Space!
```

**That's it! Your LEMM Space should be live!** 🎉
