"""
Dataset Manager for LEMM
Handles automatic downloading and caching of training datasets
Optimized for HuggingFace Spaces deployment
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from loguru import logger
from huggingface_hub import hf_hub_download, snapshot_download
from datasets import load_dataset
import requests
from tqdm import tqdm


class DatasetManager:
    """Manages dataset downloading and caching for LEMM training"""
    
    # Dataset configurations with HuggingFace Hub IDs where available
    DATASETS_CONFIG = {
        "nsynth": {
            "name": "NSynth",
            "size_gb": 30,
            "license": "CC-BY-4.0",
            "priority": 5,
            "hf_id": "google/nsynth",  # If available on HF Hub
            "download_url": "http://download.magenta.tensorflow.org/datasets/nsynth/nsynth-train.jsonwav.tar.gz",
            "type": "music_synthesis",
            "description": "305,979 musical notes across 1,006 instruments"
        },
        "ljspeech": {
            "name": "LJ Speech",
            "size_gb": 2.6,
            "license": "Public Domain",
            "priority": 5,
            "hf_id": "lj_speech",  # Available on HF Hub
            "type": "vocal_synthesis",
            "description": "13,100 speech clips, single speaker, high quality"
        },
        "urmp": {
            "name": "URMP",
            "size_gb": 12.5,
            "license": "Research",
            "priority": 4,
            "download_url": "https://labsites.rochester.edu/air/resource/URMP_4.zip",
            "type": "multi_instrument",
            "description": "44 multi-instrument classical pieces with stems"
        },
        "fma_small": {
            "name": "FMA Small",
            "size_gb": 8,
            "license": "CC-BY",
            "priority": 4,
            "hf_id": "rudraml/fma",  # Community upload
            "download_url": "https://os.unil.cloud.switch.ch/fma/fma_small.zip",
            "type": "music_genre",
            "description": "8,000 tracks, 30s clips, 8 genres"
        },
        "libritts": {
            "name": "LibriTTS",
            "size_gb": 60,
            "license": "CC-BY-4.0",
            "priority": 3,
            "hf_id": "cdminix/libritts",  # Available on HF Hub
            "type": "vocal_synthesis",
            "description": "585 hours, 2,456 speakers, multi-speaker TTS"
        },
        "musicnet": {
            "name": "MusicNet",
            "size_gb": 6,
            "license": "CC-BY-4.0",
            "priority": 3,
            "download_url": "https://zenodo.org/record/5120004/files/musicnet.tar.gz",
            "type": "music_notation",
            "description": "330 classical recordings with note annotations"
        },
        "fma_large": {
            "name": "FMA Large",
            "size_gb": 106,
            "license": "CC-BY",
            "priority": 2,
            "download_url": "https://os.unil.cloud.switch.ch/fma/fma_large.zip",
            "type": "music_genre",
            "description": "106,000 tracks, 30s clips, 161 genres"
        },
        "lakh_midi": {
            "name": "Lakh MIDI",
            "size_gb": 0.5,
            "license": "CC-BY-4.0",
            "priority": 3,
            "download_url": "http://hog.ee.columbia.edu/craffel/lmd/lmd_full.tar.gz",
            "type": "symbolic_music",
            "description": "176,581 MIDI files (symbolic music only)"
        }
    }
    
    # Phase configurations
    PHASES = {
        "minimal": {
            "datasets": ["nsynth", "ljspeech", "urmp", "fma_small"],
            "total_gb": 54,
            "description": "Essential datasets for foundation training"
        },
        "balanced": {
            "datasets": ["nsynth", "ljspeech", "urmp", "fma_small", "libritts", "musicnet"],
            "total_gb": 120,
            "description": "Balanced music and vocal training"
        },
        "comprehensive": {
            "datasets": ["nsynth", "ljspeech", "urmp", "fma_small", "libritts", "musicnet", "fma_large", "lakh_midi"],
            "total_gb": 227,
            "description": "Full dataset collection"
        }
    }
    
    def __init__(self, cache_dir: str = "datasets", use_hf_cache: bool = True):
        """
        Initialize Dataset Manager
        
        Args:
            cache_dir: Directory to cache downloaded datasets
            use_hf_cache: Use HuggingFace's cache system (recommended for Spaces)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.use_hf_cache = use_hf_cache
        self.hf_cache_dir = Path.home() / ".cache" / "huggingface" if use_hf_cache else None
        
        # Status tracking
        self.status_file = self.cache_dir / "dataset_status.json"
        self.status = self._load_status()
        
        logger.info(f"Dataset Manager initialized with cache: {self.cache_dir}")
    
    def _load_status(self) -> Dict:
        """Load download status from JSON file"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return {"downloaded": {}, "failed": {}, "last_updated": None}
    
    def _save_status(self):
        """Save download status to JSON file"""
        import datetime
        self.status["last_updated"] = datetime.datetime.now().isoformat()
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def download_from_hf(self, dataset_id: str, dataset_name: str) -> bool:
        """
        Download dataset from HuggingFace Hub
        
        Args:
            dataset_id: HuggingFace dataset ID
            dataset_name: Local dataset name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading {dataset_name} from HuggingFace Hub: {dataset_id}")
            
            # Use datasets library for HF datasets
            dataset = load_dataset(
                dataset_id,
                cache_dir=str(self.hf_cache_dir) if self.use_hf_cache else str(self.cache_dir / dataset_name)
            )
            
            self.status["downloaded"][dataset_name] = {
                "source": "huggingface",
                "id": dataset_id,
                "status": "complete"
            }
            self._save_status()
            
            logger.success(f"✅ Successfully downloaded {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {dataset_name}: {e}")
            self.status["failed"][dataset_name] = str(e)
            self._save_status()
            return False
    
    def download_from_url(self, url: str, dataset_name: str, dataset_size_gb: float) -> bool:
        """
        Download dataset from direct URL
        
        Args:
            url: Download URL
            dataset_name: Local dataset name
            dataset_size_gb: Expected size in GB
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = self.cache_dir / f"{dataset_name}.tar.gz"
            
            # Check if already downloaded
            if output_path.exists():
                logger.info(f"⏭️  {dataset_name} already exists, skipping download")
                return True
            
            logger.info(f"Downloading {dataset_name} from {url}")
            logger.info(f"Expected size: ~{dataset_size_gb} GB")
            
            # Stream download with progress bar
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=dataset_name
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
            
            self.status["downloaded"][dataset_name] = {
                "source": "url",
                "url": url,
                "path": str(output_path),
                "status": "complete"
            }
            self._save_status()
            
            logger.success(f"✅ Successfully downloaded {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {dataset_name}: {e}")
            self.status["failed"][dataset_name] = str(e)
            self._save_status()
            return False
    
    def download_dataset(self, dataset_key: str) -> bool:
        """
        Download a single dataset
        
        Args:
            dataset_key: Key from DATASETS_CONFIG
            
        Returns:
            True if successful, False otherwise
        """
        if dataset_key not in self.DATASETS_CONFIG:
            logger.error(f"Unknown dataset: {dataset_key}")
            return False
        
        config = self.DATASETS_CONFIG[dataset_key]
        
        # Check if already downloaded
        if dataset_key in self.status["downloaded"]:
            logger.info(f"⏭️  {config['name']} already downloaded")
            return True
        
        # Try HuggingFace Hub first if available
        if "hf_id" in config:
            success = self.download_from_hf(config["hf_id"], dataset_key)
            if success:
                return True
        
        # Fall back to direct URL
        if "download_url" in config:
            return self.download_from_url(
                config["download_url"],
                dataset_key,
                config["size_gb"]
            )
        
        logger.warning(f"⚠️  No download method available for {config['name']}")
        return False
    
    def download_phase(self, phase: str = "minimal", skip_existing: bool = True) -> Tuple[int, int]:
        """
        Download all datasets for a specific phase
        
        Args:
            phase: Phase name ("minimal", "balanced", "comprehensive")
            skip_existing: Skip datasets that are already downloaded
            
        Returns:
            Tuple of (successful_downloads, failed_downloads)
        """
        if phase not in self.PHASES:
            logger.error(f"Unknown phase: {phase}. Available: {list(self.PHASES.keys())}")
            return 0, 0
        
        phase_config = self.PHASES[phase]
        datasets = phase_config["datasets"]
        
        logger.info(f"🚀 Starting {phase} phase download")
        logger.info(f"📦 Datasets: {len(datasets)}")
        logger.info(f"💾 Total size: ~{phase_config['total_gb']} GB")
        logger.info(f"📝 Description: {phase_config['description']}")
        
        successful = 0
        failed = 0
        
        for dataset_key in datasets:
            config = self.DATASETS_CONFIG[dataset_key]
            logger.info(f"\n--- Downloading {config['name']} ({config['size_gb']} GB) ---")
            
            if skip_existing and dataset_key in self.status["downloaded"]:
                logger.info(f"⏭️  Skipping (already downloaded)")
                successful += 1
                continue
            
            if self.download_dataset(dataset_key):
                successful += 1
            else:
                failed += 1
        
        logger.info(f"\n✅ Phase {phase} complete: {successful} successful, {failed} failed")
        return successful, failed
    
    def get_status_summary(self) -> Dict:
        """Get summary of dataset download status"""
        total_downloaded = len(self.status["downloaded"])
        total_failed = len(self.status["failed"])
        
        downloaded_size = sum(
            self.DATASETS_CONFIG[k]["size_gb"]
            for k in self.status["downloaded"]
            if k in self.DATASETS_CONFIG
        )
        
        return {
            "total_available": len(self.DATASETS_CONFIG),
            "downloaded": total_downloaded,
            "failed": total_failed,
            "downloaded_size_gb": downloaded_size,
            "datasets": self.status["downloaded"],
            "failures": self.status["failed"]
        }
    
    def list_available_datasets(self) -> List[Dict]:
        """List all available datasets with metadata"""
        datasets = []
        for key, config in self.DATASETS_CONFIG.items():
            status = "downloaded" if key in self.status["downloaded"] else \
                    "failed" if key in self.status["failed"] else "not_downloaded"
            
            datasets.append({
                "key": key,
                "name": config["name"],
                "size_gb": config["size_gb"],
                "license": config["license"],
                "priority": config["priority"],
                "type": config["type"],
                "description": config["description"],
                "status": status
            })
        
        # Sort by priority (descending)
        datasets.sort(key=lambda x: x["priority"], reverse=True)
        return datasets
    
    def auto_download_on_space(self, max_size_gb: int = 150) -> bool:
        """
        Automatically download datasets when deployed on HuggingFace Space
        Respects storage limits
        
        Args:
            max_size_gb: Maximum storage to use in GB
            
        Returns:
            True if any datasets were downloaded
        """
        logger.info(f"🤖 Auto-download mode (max {max_size_gb} GB)")
        
        # Determine which phase to use based on storage
        if max_size_gb >= 200:
            phase = "comprehensive"
        elif max_size_gb >= 100:
            phase = "balanced"
        else:
            phase = "minimal"
        
        logger.info(f"📊 Selected phase: {phase}")
        
        successful, failed = self.download_phase(phase, skip_existing=True)
        
        return successful > 0


# Convenience function for HuggingFace Spaces
def setup_datasets_for_space(phase: str = "minimal", cache_dir: str = "datasets") -> DatasetManager:
    """
    Setup datasets for HuggingFace Space deployment
    
    Args:
        phase: Which dataset phase to download
        cache_dir: Cache directory (will use HF cache by default)
        
    Returns:
        DatasetManager instance
    """
    manager = DatasetManager(cache_dir=cache_dir, use_hf_cache=True)
    
    # Check if running on HuggingFace Space
    is_space = os.getenv("SPACE_ID") is not None
    
    if is_space:
        logger.info("🚀 Detected HuggingFace Space environment")
        space_id = os.getenv("SPACE_ID", "unknown")
        logger.info(f"📍 Space ID: {space_id}")
        
        # Auto-download based on phase
        manager.download_phase(phase, skip_existing=True)
    else:
        logger.info("💻 Local environment detected - skipping auto-download")
        logger.info(f"💡 To download datasets, run: manager.download_phase('{phase}')")
    
    return manager


if __name__ == "__main__":
    """CLI interface for dataset management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LEMM Dataset Manager")
    parser.add_argument(
        "--phase",
        choices=["minimal", "balanced", "comprehensive"],
        default="minimal",
        help="Dataset phase to download"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available datasets"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show download status"
    )
    parser.add_argument(
        "--cache-dir",
        default="datasets",
        help="Cache directory"
    )
    
    args = parser.parse_args()
    
    manager = DatasetManager(cache_dir=args.cache_dir)
    
    if args.list:
        print("\n📚 Available Datasets:\n")
        for ds in manager.list_available_datasets():
            print(f"  [{ds['status'].upper()}] {ds['name']}")
            print(f"    Size: {ds['size_gb']} GB | License: {ds['license']}")
            print(f"    Type: {ds['type']} | Priority: {'⭐' * ds['priority']}")
            print(f"    {ds['description']}\n")
    
    elif args.status:
        summary = manager.get_status_summary()
        print("\n📊 Download Status:\n")
        print(f"  Downloaded: {summary['downloaded']}/{summary['total_available']}")
        print(f"  Total Size: {summary['downloaded_size_gb']:.1f} GB")
        print(f"  Failed: {summary['failed']}")
    
    else:
        # Download phase
        manager.download_phase(args.phase)
