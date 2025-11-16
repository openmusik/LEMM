"""
File Manager for handling audio file I/O
"""
from typing import Dict, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime
from loguru import logger
import soundfile as sf
import os
import tempfile


class FileManager:
    """Manages audio file operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize file manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        output_dir_str = config.get("output", {}).get("directory", "output")
        
        # Check if running on HuggingFace Space (restricted permissions)
        is_hf_space = os.getenv("SPACE_ID") is not None
        
        if is_hf_space:
            # Use /tmp for temporary files on HF Spaces (always writable)
            self.output_dir = Path("/tmp") / "lemm_output"
            logger.info("🌐 Running on HuggingFace Space - using /tmp for output")
        else:
            # Local development - use configured directory
            self.output_dir = Path(output_dir_str)
        
        # Create output directory with robust error handling
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Output directory created: {self.output_dir}")
            
            # Test write permissions with more detailed error info
            test_file = self.output_dir / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                logger.info(f"✅ Output directory is writable")
            except PermissionError as perm_err:
                logger.error(f"❌ Permission denied for {self.output_dir}: {perm_err}")
                raise
            except Exception as test_err:
                logger.error(f"❌ Write test failed: {test_err}")
                raise
            
        except Exception as e:
            logger.error(f"❌ Cannot create/write to output directory {self.output_dir}: {e}")
            # Fallback to temp directory
            fallback_dir = Path(tempfile.gettempdir()) / "lemm_output"
            logger.warning(f"⚠️ Attempting fallback directory: {fallback_dir}")
            
            try:
                fallback_dir.mkdir(parents=True, exist_ok=True)
                self.output_dir = fallback_dir
                logger.info(f"✅ Using fallback directory: {self.output_dir}")
            except Exception as fallback_err:
                logger.error(f"❌ Fallback directory also failed: {fallback_err}")
                # Last resort: use system temp with timestamp to avoid conflicts
                self.output_dir = Path(tempfile.mkdtemp(prefix="lemm_"))
                logger.warning(f"⚠️ Using temporary directory (will be cleaned): {self.output_dir}")
        
        self.sample_rate = config.get("audio", {}).get("sample_rate", 44100)
        
        logger.info(f"File Manager initialized - output dir: {self.output_dir}")
    
    def save_output(self, audio: np.ndarray, filename: Optional[str] = None) -> str:
        """
        Save final audio output
        
        Args:
            audio: Audio data as numpy array
            filename: Optional filename (will generate if not provided)
            
        Returns:
            Absolute path to saved file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"lemm_song_{timestamp}.wav"
            
            # Ensure filename has .wav extension
            if not filename.endswith('.wav'):
                filename += '.wav'
            
            # CRITICAL: Ensure we're not using a directory as the filename
            if Path(filename).is_absolute() or '/' in filename or '\\' in filename:
                logger.error(f"❌ Invalid filename contains path separators: {filename}")
                # Extract just the filename
                filename = Path(filename).name
                if not filename or filename == '.wav':
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"lemm_song_{timestamp}.wav"
                logger.warning(f"⚠️ Using sanitized filename: {filename}")
            
            output_path = self.output_dir / filename
            
            # Verify output_path is a file, not a directory
            if output_path.exists() and output_path.is_dir():
                logger.error(f"❌ Output path is a directory: {output_path}")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"lemm_song_{timestamp}.wav"
                output_path = self.output_dir / filename
                logger.warning(f"⚠️ Using new filename: {filename}")
            
            logger.info(f"💾 Saving audio to: {output_path}")
            logger.info(f"   Output directory: {output_path.parent}")
            logger.info(f"   Filename: {output_path.name}")
            logger.info(f"   Audio shape: {audio.shape}, dtype: {audio.dtype}")
            logger.info(f"   Sample rate: {self.sample_rate} Hz")
            
            # Ensure audio is in correct format
            if audio.ndim == 1:
                # Mono audio
                audio_to_save = audio
            elif audio.ndim == 2:
                # Stereo - ensure shape is (samples, channels)
                if audio.shape[0] < audio.shape[1]:
                    audio_to_save = audio.T
                else:
                    audio_to_save = audio
            else:
                raise ValueError(f"Unexpected audio shape: {audio.shape}")
            
            # Ensure float32 for compatibility
            if audio_to_save.dtype != np.float32:
                audio_to_save = audio_to_save.astype(np.float32)
            
            # Normalize audio to prevent clipping and ensure audible signal
            max_val = np.abs(audio_to_save).max()
            if max_val > 0:
                # Normalize to -1.0 to 1.0 range with 0.95 headroom
                audio_to_save = audio_to_save / max_val * 0.95
                logger.info(f"   Normalized audio (max was: {max_val:.4f})")
            else:
                logger.warning("   ⚠️ Audio contains only silence!")
            
            # Save as WAV with enhanced error handling
            try:
                # Verify directory still exists and is writable
                if not output_path.parent.exists():
                    logger.error(f"❌ Output directory disappeared: {output_path.parent}")
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    logger.info(f"✅ Recreated output directory")
                
                sf.write(str(output_path), audio_to_save, self.sample_rate)
                logger.info(f"✅ Audio saved with soundfile")
                
            except PermissionError as perm_err:
                logger.error(f"❌ Permission Error (Error 21): {perm_err}")
                logger.error(f"   Path: {output_path}")
                logger.error(f"   Directory writable: {os.access(output_path.parent, os.W_OK)}")
                
                # Try with a different filename in case of file lock
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                alt_filename = f"lemm_song_{timestamp}.wav"
                alt_path = output_path.parent / alt_filename
                logger.warning(f"⚠️ Trying alternative filename: {alt_filename}")
                
                try:
                    sf.write(str(alt_path), audio_to_save, self.sample_rate)
                    output_path = alt_path
                    logger.info(f"✅ Saved with alternative filename")
                except Exception as alt_err:
                    logger.error(f"❌ Alternative save also failed: {alt_err}")
                    raise
                    
            except Exception as write_error:
                logger.error(f"❌ soundfile.write failed: {write_error}")
                logger.warning("⚠️ Trying scipy.io.wavfile fallback...")
                
                # Try alternative write method
                import scipy.io.wavfile as wavfile
                # Convert to int16 for scipy
                audio_int16 = (audio_to_save * 32767).astype(np.int16)
                try:
                    wavfile.write(str(output_path), self.sample_rate, audio_int16)
                    logger.info("✅ Used scipy.io.wavfile as fallback")
                except Exception as scipy_err:
                    logger.error(f"❌ scipy.io.wavfile also failed: {scipy_err}")
                    raise
            
            # Verify file was created
            if not output_path.exists():
                raise FileNotFoundError(f"File was not created: {output_path}")
            
            # CRITICAL: Ensure we're returning a file, not a directory
            if output_path.is_dir():
                logger.error(f"❌ output_path is a directory, not a file: {output_path}")
                raise ValueError(f"Output path is a directory: {output_path}")
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Audio saved successfully: {file_size_mb:.2f} MB")
            
            # Return absolute path as string (required for Gradio)
            result_path = str(output_path.absolute())
            logger.info(f"🔙 Returning path to Gradio: {result_path}")
            
            # Final validation before return
            if not Path(result_path).is_file():
                logger.error(f"❌ Result path is not a file: {result_path}")
                raise ValueError(f"Result path is not a valid file: {result_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"❌ Error saving audio: {e}")
            logger.exception("Full traceback:")
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
