"""
HuggingFace Space App for LEMM - Let Everyone Make Music
ZeroGPU Compatible Version
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.__version__ import __version__
from src.ui.gradio_interface import create_interface
from src.utils.config_loader import load_config
from loguru import logger

# ZeroGPU support
try:
    import spaces
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

# Load configuration
config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
config = load_config(config_path)

# Update config for HuggingFace Space environment
# Use HuggingFace model hub instead of local files
config["models"]["ace_step"]["path"] = "ACE-Step/ACE-Step-v1-3.5B"
config["models"]["ace_step"]["use_local"] = False

# Enable sharing for HuggingFace Space
config["server"]["share"] = False  # HF handles this
config["server"]["debug"] = False

logger.info("Configuration updated for HuggingFace Space")
logger.info(f"Model path: {config['models']['ace_step']['path']}")

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
