"""
File Manager for handling audio file I/O
"""
from typing import Dict, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime
from loguru import logger
import soundfile as sf


class FileManager:
    """Manages audio file operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize file manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path(config.get("output", {}).get("directory", "output"))
        self.sample_rate = config.get("audio", {}).get("sample_rate", 44100)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"File Manager initialized - output dir: {self.output_dir}")
    
    def save_output(self, audio: np.ndarray, filename: Optional[str] = None) -> str:
        """
        Save final audio output
        
        Args:
            audio: Audio data as numpy array
            filename: Optional filename (will generate if not provided)
            
        Returns:
            Path to saved file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"lemm_song_{timestamp}.wav"
            
            output_path = self.output_dir / filename
            
            # Save as WAV
            sf.write(str(output_path), audio, self.sample_rate)
            
            logger.info(f"Audio saved to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    def save_stems(self, stems: Dict[str, np.ndarray], prefix: str = "stem") -> Dict[str, str]:
        """
        Save individual stems
        
        Args:
            stems: Dictionary of stem audio data
            prefix: Filename prefix
            
        Returns:
            Dictionary mapping stem names to file paths
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_paths = {}
            
            for stem_name, stem_audio in stems.items():
                filename = f"{prefix}_{stem_name}_{timestamp}.wav"
                output_path = self.output_dir / filename
                
                sf.write(str(output_path), stem_audio, self.sample_rate)
                saved_paths[stem_name] = str(output_path)
                
                logger.info(f"Stem '{stem_name}' saved to: {output_path}")
            
            return saved_paths
            
        except Exception as e:
            logger.error(f"Error saving stems: {e}")
            raise
    
    def load_audio(self, filepath: str) -> np.ndarray:
        """
        Load audio file
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Audio data as numpy array
        """
        try:
            audio, sr = sf.read(filepath)
            
            # Resample if necessary
            if sr != self.sample_rate:
                logger.warning(f"Resampling from {sr} to {self.sample_rate}")
                # TODO: Implement resampling
            
            return audio
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def convert_to_mp3(self, wav_path: str) -> str:
        """
        Convert WAV to MP3
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Path to MP3 file
        """
        # TODO: Implement MP3 conversion (requires pydub + ffmpeg)
        logger.warning("MP3 conversion not implemented yet")
        return wav_path
    
    def create_temp_file(self, data: np.ndarray, suffix: str = ".wav") -> str:
        """
        Create temporary file
        
        Args:
            data: Audio data
            suffix: File suffix
            
        Returns:
            Path to temporary file
        """
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_path = temp_dir / f"temp_{timestamp}{suffix}"
        
        sf.write(str(temp_path), data, self.sample_rate)
        
        return str(temp_path)
    
    def cleanup_temp_files(self):
        """Remove temporary files"""
        temp_dir = Path("temp")
        if temp_dir.exists():
            for file in temp_dir.glob("temp_*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete {file}: {e}")
