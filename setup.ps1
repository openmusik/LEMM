# LEMM Setup Script for Windows PowerShell
# This script sets up the Python 3.10 environment and installs all dependencies

Write-Host "="*70 -ForegroundColor Cyan
Write-Host "LEMM (Let Everyone Make Music) - Setup Script" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""

# Check Python 3.10 is available
Write-Host "Checking for Python 3.10..." -ForegroundColor Yellow
$python310 = py -3.10 --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python 3.10 not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10.11 from:" -ForegroundColor Red
    Write-Host "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Found: $python310" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "Creating Python 3.10 virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv310") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    py -3.10 -m venv .venv310
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv310\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
.\.venv310\Scripts\python.exe -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install PyTorch with CUDA
Write-Host "Installing PyTorch with CUDA 12.1..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes...)" -ForegroundColor Gray
.\.venv310\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install PyTorch" -ForegroundColor Red
    exit 1
}
Write-Host "✓ PyTorch installed" -ForegroundColor Green
Write-Host ""

# Install other requirements
Write-Host "Installing other dependencies from requirements.txt..." -ForegroundColor Yellow
Write-Host "(This may take 5-10 minutes...)" -ForegroundColor Gray
.\.venv310\Scripts\python.exe -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some dependencies may have failed to install" -ForegroundColor Yellow
    Write-Host "Please check the output above for errors" -ForegroundColor Yellow
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Install ACE-Step
Write-Host "Installing ACE-Step (this is the slow part)..." -ForegroundColor Yellow
Write-Host "(This may take 10-15 minutes on first install...)" -ForegroundColor Gray
Write-Host "Downloading from GitHub..." -ForegroundColor Gray
.\.venv310\Scripts\python.exe -m pip install git+https://github.com/ACE-Step/ACE-Step.git
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install ACE-Step" -ForegroundColor Red
    Write-Host "You can try installing it manually later with:" -ForegroundColor Yellow
    Write-Host "  .\.venv310\Scripts\python.exe -m pip install git+https://github.com/ACE-Step/ACE-Step.git" -ForegroundColor Cyan
} else {
    Write-Host "✓ ACE-Step installed successfully!" -ForegroundColor Green
}
Write-Host ""

# Verify installation
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "Verifying installation..." -ForegroundColor Yellow
Write-Host ""

$python_version = .\.venv310\Scripts\python.exe --version
Write-Host "Python: $python_version" -ForegroundColor Green

$torch_check = .\.venv310\Scripts\python.exe -c "import torch; print(f'PyTorch {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $torch_check -ForegroundColor Green
} else {
    Write-Host "WARNING: PyTorch verification failed" -ForegroundColor Yellow
}

$acestep_check = .\.venv310\Scripts\python.exe -c "from acestep.pipeline_ace_step import ACEStepPipeline; print('ACE-Step: Installed')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $acestep_check -ForegroundColor Green
} else {
    Write-Host "WARNING: ACE-Step not installed or verification failed" -ForegroundColor Yellow
    Write-Host "Install it manually with:" -ForegroundColor Yellow
    Write-Host "  .\.venv310\Scripts\python.exe -m pip install git+https://github.com/ACE-Step/ACE-Step.git" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the environment in the future, run:" -ForegroundColor Cyan
Write-Host "  .\.venv310\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start LEMM, run:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor Yellow
Write-Host ""
