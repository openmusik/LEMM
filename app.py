"""
HuggingFace Space App for LEMM - Let Everyone Make Music
ZeroGPU Compatible Version with Automatic Dataset Management
"""
import os
import sys
from pathlib import Path

print("=== LEMM App Starting ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

# Add src to path first
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)
print(f"Added to path: {src_path}")

# CRITICAL: Import spaces BEFORE torch to avoid CUDA initialization issues
print("Importing ZeroGPU spaces package...")
try:
    import spaces
    print("✓ ZeroGPU spaces package loaded")
except ImportError:
    print("✗ ZeroGPU spaces package not available (running locally)")
    spaces = None

# Import torch with detailed error handling
print("Attempting to import torch...")
try:
    import torch
    print(f"✓ PyTorch {torch.__version__} loaded successfully")
    print(f"CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"✗ Failed to import torch: {e}")
    print("Checking installed packages...")
    import subprocess
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True, timeout=10)
        print("Installed packages:")
        for line in result.stdout.split('\n')[:10]:  # Show first 10 packages
            if line.strip():
                print(f"  {line}")
    except Exception as pkg_e:
        print(f"Could not list packages: {pkg_e}")
    raise

from src.__version__ import __version__
from src.ui.gradio_interface import create_interface
from src.utils.config_loader import load_config
from src.utils.dataset_manager import setup_datasets_for_space
from loguru import logger

# ZeroGPU support
try:
    import spaces  # type: ignore
    ZEROGPU_AVAILABLE = True
    logger.info("ZeroGPU (spaces) module detected")
except ImportError:
    ZEROGPU_AVAILABLE = False
    logger.info("Running without ZeroGPU")

# Configure logging for HuggingFace Space
logger.add(
    "logs/lemm_{time}.log",
    rotation="100 MB",
    retention="3 days",
    level="INFO"
)

logger.info(f"Starting LEMM v{__version__} on HuggingFace Space")

# Initialize Dataset Manager and auto-download if needed
logger.info("🗂️  Initializing Dataset Manager...")
dataset_phase = os.getenv("LEMM_DATASET_PHASE", "minimal")  # minimal, balanced, or comprehensive
dataset_manager = setup_datasets_for_space(phase=dataset_phase)

# Log dataset status
status = dataset_manager.get_status_summary()
logger.info(f"📊 Datasets downloaded: {status['downloaded']}/{status['total_available']}")
logger.info(f"💾 Total dataset size: {status['downloaded_size_gb']:.1f} GB")
if status['failed'] > 0:
    logger.warning(f"⚠️  {status['failed']} datasets failed to download")

# Detect GPU availability
if torch.cuda.is_available():
    device = "cuda"
    logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
else:
    device = "cpu"
    logger.warning("CUDA not available - running on CPU (slower)")

# Load configuration
config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
config = load_config(config_path)

# Update config for HuggingFace Space environment
# Use HuggingFace model hub instead of local files
config["models"]["ace_step"]["path"] = "ACE-Step/ACE-Step-v1-3.5B"
config["models"]["ace_step"]["use_local"] = False
config["models"]["ace_step"]["device"] = device

# Update all device settings to match detected device
config["audio"]["device"] = device

# Enable sharing for HuggingFace Space
config["server"]["share"] = False  # HF handles this
config["server"]["debug"] = False

logger.info("Configuration updated for HuggingFace Space")
logger.info(f"Model path: {config['models']['ace_step']['path']}")
logger.info(f"Device: {device}")

# Create and launch interface
interface = create_interface(config)

# Launch with HuggingFace Space settings
if __name__ == "__main__":
    interface.launch(
        server_name=config.get("server", {}).get("host", "0.0.0.0"),
        server_port=config.get("server", {}).get("port", 7860),
        share=False,  # HuggingFace handles sharing
        show_error=True
    )
