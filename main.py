"""
Main entry point for LEMM - Let Everyone Make Music
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.__version__ import __version__
from src.ui.gradio_interface import create_interface
from src.utils.config_loader import load_config
from loguru import logger


def main():
    """
    Main function to launch LEMM application
    """
    # Configure logging
    logger.add(
        "logs/lemm_{time}.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO"
    )
    
    logger.info(f"Starting LEMM v{__version__} - Let Everyone Make Music")
    
    # Load configuration
    config = load_config()
    
    # Create and launch Gradio interface
    interface = create_interface(config)
    
    interface.launch(
        server_name=config.get("server", {}).get("host", "0.0.0.0"),
        server_port=config.get("server", {}).get("port", 7860),
        share=config.get("server", {}).get("share", False),
        debug=config.get("server", {}).get("debug", False)
    )


if __name__ == "__main__":
    main()
