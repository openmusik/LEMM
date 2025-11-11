# Python 3.10 Installation Guide for LEMM

## Why Python 3.10?

ACE-Step requires Python 3.10 due to specific dependency requirements:
- **spacy 3.8.4** - Required by ACE-Step, not compatible with Python 3.13+
- **ACE-Step package** - Tested and verified on Python 3.10.x

## Step 1: Download Python 3.10

1. Visit the official Python downloads page:
   - **URL**: https://www.python.org/downloads/release/python-31011/
   
2. Scroll down to "Files" section and download:
   - **Windows 64-bit**: `Windows installer (64-bit)` 
   - Direct link: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

## Step 2: Install Python 3.10

1. Run the downloaded installer `python-3.10.11-amd64.exe`

2. **IMPORTANT**: On the first screen:
   - ✅ Check "Add Python 3.10 to PATH"
   - ✅ Check "Install for all users" (optional)
   - Click "Customize installation"

3. Optional Features:
   - ✅ Keep all defaults checked
   - Click "Next"

4. Advanced Options:
   - ✅ Install for all users
   - ✅ Associate files with Python (optional)
   - ✅ Create shortcuts (optional)
   - ✅ Add Python to environment variables
   - ✅ Precompile standard library
   - Set installation path: `C:\Python310` (recommended)
   - Click "Install"

5. Wait for installation to complete
   - Click "Close" when done

## Step 3: Verify Installation

Open a **new** PowerShell window and run:

```powershell
py -0
```

You should see Python 3.10 listed:
```
-V:3.13          Python 3.13 (64-bit)
-V:3.12          Python 3.12 (64-bit)
-V:3.10          Python 3.10 (64-bit)  <- New!
```

## Step 4: Create Python 3.10 Virtual Environment

Navigate to your LEMM project directory:

```powershell
cd D:\2025-vibe-coding\lemm_beta
```

Create a new virtual environment with Python 3.10:

```powershell
py -3.10 -m venv .venv310
```

## Step 5: Activate the Environment

```powershell
.\.venv310\Scripts\Activate.ps1
```

Verify you're using Python 3.10:

```powershell
python --version
# Should output: Python 3.10.11
```

## Step 6: Install PyTorch with CUDA Support

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Step 7: Install ACE-Step

```powershell
pip install git+https://github.com/ACE-Step/ACE-Step.git
```

This will install ACE-Step and all its dependencies including spacy 3.8.4.

## Step 8: Install Other Project Dependencies

```powershell
pip install -r requirements.txt
```

## Step 9: Update VS Code Python Interpreter

1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose: `.\.venv310\Scripts\python.exe`

## Troubleshooting

### Python 3.10 Not Showing in `py -0`

- Restart your computer after installation
- Or log out and log back in
- Close and reopen all terminal windows

### PATH Issues

If Python 3.10 isn't in PATH:
```powershell
# Add manually (temporary for current session):
$env:PATH = "C:\Python310;C:\Python310\Scripts;$env:PATH"
```

### ACE-Step Installation Fails

Make sure you're in the Python 3.10 environment:
```powershell
python --version  # Should show 3.10.x
pip --version     # Should show pip from .venv310
```

## Next Steps

After successful installation:
1. The project will automatically use the Python 3.10 environment
2. ACE-Step models will load properly using `ACEStepPipeline`
3. All dependencies will be compatible
4. You can run: `python main.py` to launch LEMM

---

**Note**: You can keep multiple Python versions installed. The `py` launcher will handle version selection automatically.
