"""
Configuration loader for LEMM
"""
from pathlib import Path
from typing import Dict, Any
import yaml
from loguru import logger


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration
    
    Returns:
        Default configuration dictionary
    """
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 7860,
            "share": False,
            "debug": False
        },
        "audio": {
            "sample_rate": 44100,
            "clip_duration": 32,
            "lead_in_duration": 2,
            "lead_out_duration": 2,
            "main_duration": 28,
            "crossfade_duration": 2
        },
        "models": {
            "ace_step": {
                "path": "models/ace_step",
                "device": "cuda",
                "dtype": "float16"
            },
            "song_composer": {
                "path": "models/song_composer",
                "device": "cuda"
            },
            "music_control_net": {
                "path": "models/music_control_net",
                "device": "cuda"
            },
            "demucs": {
                "model": "htdemucs",
                "device": "cuda"
            },
            "so_vits_svc": {
                "path": "models/so_vits_svc",
                "device": "cuda"
            }
        },
        "generation": {
            "default_clips": 3,
            "max_clips": 10,
            "temperature": 1.0,
            "top_p": 0.95
        },
        "lora": {
            "enabled": False,
            "path": None,
            "alpha": 1.0
        },
        "output": {
            "directory": "output",
            "format": "wav",
            "export_stems": False
        }
    }
