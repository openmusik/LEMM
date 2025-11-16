"""
Audio Processor for stem separation and enhancement
"""
from typing import Dict, Any, List, Tuple, TYPE_CHECKING
import numpy as np
import torch
from pathlib import Path
try:
    from demucs.pretrained import get_model  # type: ignore
    from demucs.apply import apply_model  # type: ignore
    DEMUCS_AVAILABLE = True
except ImportError:
    DEMUCS_AVAILABLE = False
    get_model = None  # type: ignore
    apply_model = None  # type: ignore
from loguru import logger

# Import pedalboard with proper type checking
try:
    from pedalboard import (  # type: ignore
        Pedalboard, Reverb, Compressor, HighpassFilter, LowpassFilter, 
        Gain, PeakFilter, LowShelfFilter, HighShelfFilter
    )
    PEDALBOARD_AVAILABLE = True
except ImportError:
    PEDALBOARD_AVAILABLE = False
    # Create mock classes for type checking
    class MockPedalboard: 
        def __call__(self, audio: np.ndarray, *args, **kwargs) -> np.ndarray:
            # Return audio unchanged when pedalboard not available
            return audio
    Pedalboard = MockPedalboard  # type: ignore
    Reverb = MockPedalboard  # type: ignore
    Compressor = MockPedalboard  # type: ignore
    HighpassFilter = MockPedalboard  # type: ignore
    LowpassFilter = MockPedalboard  # type: ignore
    Gain = MockPedalboard  # type: ignore
    PeakFilter = MockPedalboard  # type: ignore
    LowShelfFilter = MockPedalboard  # type: ignore
    HighShelfFilter = MockPedalboard  # type: ignore
    logger.warning("Pedalboard not available - install with: pip install pedalboard")


class AudioProcessor:
    """Processes audio clips with stem separation and enhancement"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audio processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.sample_rate = config.get("audio", {}).get("sample_rate", 44100)
        self.demucs_model = None
        self.sovits_model = None
        self.device = config.get("models", {}).get("demucs", {}).get("device", "cuda")
        self.demucs_name = config.get("models", {}).get("demucs", {}).get("model", "htdemucs")
        self.demucs_shifts = config.get("models", {}).get("demucs", {}).get("shifts", 1)
        self.demucs_split = config.get("models", {}).get("demucs", {}).get("split", True)
        
        logger.info(f"Audio Processor initialized - device: {self.device}")
    
    def load_models(self):
        """Load Demucs and so-vits-svc models"""
        try:
            # Check device availability
            import torch
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available - falling back to CPU")
                self.device = "cpu"
            
            # Load Demucs
            logger.info(f"Loading Demucs model: {self.demucs_name}")
            if DEMUCS_AVAILABLE and get_model:
                self.demucs_model = get_model(self.demucs_name)
                self.demucs_model.to(self.device)
                self.demucs_model.eval()
                logger.info(f"Demucs model loaded successfully on {self.device}")
            else:
                self.demucs_model = None
                logger.warning("Demucs not available - stem separation will be skipped")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            logger.warning("Audio processor will skip stem separation")
            # Don't raise - allow app to continue without stem separation
    
    def process_clip(self, clip: np.ndarray, has_vocals: bool = True) -> Dict[str, np.ndarray]:
        """
        Process audio clip: separate stems and enhance
        
        Args:
            clip: Audio clip as numpy array (may contain pre-mixed vocals or be instrumental)
            has_vocals: Whether the clip has vocals embedded in it
            
        Returns:
            Dictionary of enhanced stems
        """
        try:
            logger.info(f"Processing audio clip (has_vocals={has_vocals})")
            
            # Load models if not loaded
            if self.demucs_model is None:
                self.load_models()
            
            # If models available, use stem separation
            if self.demucs_model is not None:
                # Step 1: Stem separation
                stems = self.separate_stems(clip)
                
                # Validate stems aren't all silent
                total_energy = sum(np.abs(stem).max() for stem in stems.values())
                logger.info(f"Total stem energy after separation: {total_energy:.4f}")
                
                # Step 2: Enhance vocals if present
                if has_vocals and 'vocals' in stems:
                    stems['vocals'] = self.enhance_vocals(stems['vocals'])
                
                # Step 3: Enhance non-vocal stems
                for stem_name in stems:
                    if stem_name != 'vocals':
                        stems[stem_name] = self.enhance_non_vocal(stems[stem_name], stem_name)
                
                # Validate enhanced stems
                total_energy_after = sum(np.abs(stem).max() for stem in stems.values())
                logger.info(f"Total stem energy after enhancement: {total_energy_after:.4f}")
                
                return stems
            else:
                # Demucs not available - return the clip as-is without separation
                # Since vocals are pre-mixed into the audio by MusicGen, keep them there
                logger.warning("Demucs model not available - returning mixed audio without stem separation")
                logger.info("Vocals and instruments will remain mixed together in 'other' stem")
                
                # Return all audio in 'other' stem to preserve vocals+instrumental mix
                return {
                    'vocals': np.zeros_like(clip),  # Empty - vocals are in the mixed audio
                    'bass': np.zeros_like(clip),
                    'drums': np.zeros_like(clip),
                    'other': clip  # Keep entire mixed audio (vocals + instrumental)
                }
            
        except Exception as e:
            logger.error(f"Error processing clip: {e}")
            raise
    
    def separate_stems(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Separate audio into stems using Demucs
        
        Args:
            audio: Input audio
            
        Returns:
            Dictionary of separated stems
        """
        try:
            logger.info("Separating stems with Demucs")
            
            # Load model if not loaded
            if self.demucs_model is None:
                self.load_models()
            
            # Prepare audio tensor
            # Demucs expects (batch, channels, samples)
            if audio.ndim == 1:
                # Mono to stereo
                audio_tensor = torch.from_numpy(audio).float()
                audio_tensor = torch.stack([audio_tensor, audio_tensor])  # Create stereo
            else:
                audio_tensor = torch.from_numpy(audio.T).float()
            
            # Add batch dimension
            audio_tensor = audio_tensor.unsqueeze(0).to(self.device)
            
            # Apply Demucs
            logger.info(f"Running Demucs with shifts={self.demucs_shifts}")
            with torch.no_grad():
                sources = apply_model(
                    self.demucs_model,  # type: ignore
                    audio_tensor,
                    shifts=self.demucs_shifts,
                    split=self.demucs_split,
                    overlap=0.25,
                    progress=False
                )[0]  # Remove batch dimension
            
            # Convert sources to numpy
            # sources shape: (stems, channels, samples)
            sources = sources.cpu().numpy()
            
            # Get stem names from model
            stem_names = self.demucs_model.sources  # type: ignore
            
            # Create dictionary of stems (convert to mono by averaging channels)
            stems = {}
            for i, name in enumerate(stem_names):
                stem_audio = sources[i]  # (channels, samples)
                # Convert to mono
                if stem_audio.shape[0] == 2:
                    stem_audio = stem_audio.mean(axis=0)
                else:
                    stem_audio = stem_audio[0]
                stems[name] = stem_audio
            
            logger.info(f"Separated into stems: {list(stems.keys())}")
            
            return stems
            
        except Exception as e:
            logger.error(f"Error separating stems: {e}")
            # Fallback to mock stems
            logger.warning("Falling back to mock stem separation")
            stems = {
                'vocals': audio * 0.3,
                'bass': audio * 0.25,
                'drums': audio * 0.25,
                'other': audio * 0.2
            }
            return stems
    
    def enhance_vocals(self, vocal_stem: np.ndarray) -> np.ndarray:
        """
        Enhance vocal stem using so-vits-svc
        
        Args:
            vocal_stem: Vocal audio stem
            
        Returns:
            Enhanced vocal stem
        """
        try:
            if not PEDALBOARD_AVAILABLE:
                logger.warning("Pedalboard not available, returning unprocessed vocals")
                return vocal_stem
            
            # TODO: Implement actual so-vits-svc enhancement
            # so-vits-svc requires:
            # 1. A trained model checkpoint
            # 2. Configuration file
            # 3. Proper inference setup
            # For now, apply basic enhancement with Pedalboard
            
            logger.info("Enhancing vocals (basic enhancement - so-vits-svc not fully integrated)")
            
            # Apply vocal-specific effects with Pedalboard
            board = Pedalboard([  # type: ignore
                # De-esser (reduce sibilance)
                Compressor(threshold_db=-24, ratio=8, attack_ms=0.1, release_ms=50),  # type: ignore
                # Presence boost
                PeakFilter(cutoff_frequency_hz=3000, gain_db=2, q=0.7),  # type: ignore
                # Gentle compression
                Compressor(threshold_db=-18, ratio=3, attack_ms=5, release_ms=100),  # type: ignore
                # Light reverb
                Reverb(room_size=0.2, damping=0.7, wet_level=0.1),  # type: ignore
                # Gain
                Gain(gain_db=2)  # type: ignore
            ])
            
            if PEDALBOARD_AVAILABLE:
                enhanced = board(vocal_stem, self.sample_rate)
                enhanced = np.clip(enhanced, -1.0, 1.0)
            else:
                logger.warning("Pedalboard not available - returning original vocal stem")
                enhanced = vocal_stem
            
            logger.info("Vocal enhancement complete")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing vocals: {e}")
            # Fallback to slight boost
            return np.clip(vocal_stem * 1.1, -1.0, 1.0)
    
    def enhance_non_vocal(self, stem: np.ndarray, stem_name: str) -> np.ndarray:
        """
        Enhance non-vocal stem using Pedalboard
        
        Args:
            stem: Audio stem
            stem_name: Name of the stem (bass, drums, other)
            
        Returns:
            Enhanced stem
        """
        try:
            # TODO: Implement actual Pedalboard processing
            
            logger.info(f"Enhancing {stem_name} with Pedalboard")
            
            # Placeholder processing based on stem type
            if stem_name == 'bass':
                enhanced = self._apply_bass_enhancement(stem)
            elif stem_name == 'drums':
                enhanced = self._apply_drum_enhancement(stem)
            else:
                enhanced = self._apply_general_enhancement(stem)
            
            logger.warning(f"Using placeholder enhancement for {stem_name}")
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing {stem_name}: {e}")
            raise
    
    def _apply_bass_enhancement(self, audio: np.ndarray) -> np.ndarray:
        """Apply bass-specific enhancement"""
        try:
            if not PEDALBOARD_AVAILABLE:
                logger.warning("Pedalboard not available, applying simple gain")
                return audio * 1.05
            
            # Create bass enhancement chain
            board = Pedalboard([  # type: ignore
                LowShelfFilter(cutoff_frequency_hz=150, gain_db=3),  # type: ignore
                Compressor(threshold_db=-20, ratio=4),  # type: ignore
                Gain(gain_db=2)  # type: ignore
            ])
            
            # Apply effects
            if PEDALBOARD_AVAILABLE:
                enhanced: np.ndarray = board(audio, self.sample_rate)
                logger.info("Bass enhancement complete")
                return enhanced
            else:
                logger.warning("Pedalboard not available - returning original audio")
                return audio
            
        except Exception as e:
            logger.warning(f"Pedalboard bass enhancement failed: {e}, using fallback")
            return audio * 1.05
    
    def _apply_drum_enhancement(self, audio: np.ndarray) -> np.ndarray:
        """Apply drum-specific enhancement"""
        try:
            if not PEDALBOARD_AVAILABLE:
                logger.warning("Pedalboard not available, applying simple gain")
                return audio * 1.03
            
            # Create drum enhancement chain
            board = Pedalboard([  # type: ignore
                HighShelfFilter(cutoff_frequency_hz=5000, gain_db=2),  # type: ignore
                Compressor(threshold_db=-18, ratio=6, attack_ms=1, release_ms=100),  # type: ignore
                Gain(gain_db=1.5)  # type: ignore
            ])
            
            # Apply effects
            if PEDALBOARD_AVAILABLE:
                enhanced: np.ndarray = board(audio, self.sample_rate)
                logger.info("Drum enhancement complete")
                return enhanced
            else:
                logger.warning("Pedalboard not available - returning original audio")
                return audio
            
        except Exception as e:
            logger.warning(f"Pedalboard drum enhancement failed: {e}, using fallback")
            return audio * 1.05
    
    def _apply_general_enhancement(self, audio: np.ndarray) -> np.ndarray:
        """Apply general enhancement"""
        try:
            if not PEDALBOARD_AVAILABLE:
                logger.warning("Pedalboard not available, returning unprocessed audio")
                return audio
            
            # Create general enhancement chain
            board = Pedalboard([  # type: ignore
                Compressor(threshold_db=-16, ratio=3),  # type: ignore
                Reverb(room_size=0.25, damping=0.5, wet_level=0.15),  # type: ignore
                Gain(gain_db=1)  # type: ignore
            ])
            
            # Apply effects
            if PEDALBOARD_AVAILABLE:
                enhanced: np.ndarray = board(audio, self.sample_rate)
                logger.info("General enhancement complete")
                return enhanced
            else:
                logger.warning("Pedalboard not available - returning original audio")
                return audio
            
        except Exception as e:
            logger.warning(f"Pedalboard general enhancement failed: {e}, using fallback")
            logger.exception("Full traceback:")
            return audio * 1.0
    
    def unload_models(self):
        """Unload models to free memory"""
        try:
            if self.demucs_model is not None:
                del self.demucs_model
                self.demucs_model = None
                
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            logger.info("Audio processor models unloaded")
            
        except Exception as e:
            logger.error(f"Error unloading models: {e}")
