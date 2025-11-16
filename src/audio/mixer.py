"""
Audio Mixer for chaining clips and final mixing
"""
from typing import Dict, Any, List, Tuple
import numpy as np
from loguru import logger


class AudioMixer:
    """Mixes and chains audio clips"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audio mixer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.sample_rate = config.get("audio", {}).get("sample_rate", 44100)
        self.crossfade_duration = config.get("audio", {}).get("crossfade_duration", 2)
        
        logger.info("Audio Mixer initialized")
    
    def chain_clips(self, clips: List[Dict[str, np.ndarray]]) -> np.ndarray:
        """
        Chain multiple clips with crossfading
        
        Args:
            clips: List of clip dictionaries (each containing stems)
            
        Returns:
            Final mixed audio
        """
        try:
            logger.info(f"Chaining {len(clips)} clips")
            
            # Mix stems within each clip first
            mixed_clips = []
            for i, clip_stems in enumerate(clips):
                mixed = self.mix_stems(clip_stems)
                clip_max = np.abs(mixed).max()
                logger.info(f"Clip {i+1} mixed - peak: {clip_max:.4f}")
                mixed_clips.append(mixed)
            
            # Chain clips with crossfading
            chained = self._chain_with_crossfade(mixed_clips)
            chained_max = np.abs(chained).max()
            chained_rms = np.sqrt(np.mean(chained**2))
            logger.info(f"Chained audio - peak: {chained_max:.4f}, RMS: {chained_rms:.4f}")
            
            # Apply final mastering
            final = self.master(chained)
            
            return final
            
        except Exception as e:
            logger.error(f"Error chaining clips: {e}")
            raise
    
    def mix_stems(self, stems: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Mix all stems into a single audio clip
        
        Args:
            stems: Dictionary of audio stems (vocals, bass, drums, other)
            
        Returns:
            Mixed audio
        """
        try:
            logger.info(f"Mixing stems: {list(stems.keys())}")
            
            # Get reference shape from any stem
            reference_stem = list(stems.values())[0]
            mixed = np.zeros_like(reference_stem, dtype=np.float32)
            
            # Apply stem-specific volume levels for balanced mix
            stem_volumes = {
                'vocals': 1.0,    # Vocals at full volume (most important)
                'drums': 0.85,    # Drums slightly lower
                'bass': 0.80,     # Bass balanced
                'other': 0.75     # Other instruments lower to not compete
            }
            
            for stem_name, stem_audio in stems.items():
                # Get volume for this stem (default to 0.6 if not specified)
                volume = stem_volumes.get(stem_name, 0.6)
                
                # Skip empty stems (all zeros)
                stem_max = np.abs(stem_audio).max()
                if stem_max < 1e-6:
                    logger.debug(f"Skipping empty stem: {stem_name}")
                    continue
                
                logger.info(f"Adding stem '{stem_name}' at {volume*100:.0f}% volume (peak: {stem_max:.4f})")
                mixed += stem_audio * volume
            
            # Log mixed levels before normalization
            mixed_max = np.abs(mixed).max()
            mixed_rms = np.sqrt(np.mean(mixed**2))
            logger.info(f"Mixed audio - peak: {mixed_max:.4f}, RMS: {mixed_rms:.4f}")
            
            # Normalize to prevent clipping while maintaining dynamics
            if mixed_max > 0:
                # Use softer normalization to preserve dynamics
                if mixed_max > 0.95:
                    # Only normalize if we're close to clipping
                    mixed = mixed / mixed_max * 0.95
                    logger.info(f"Normalized mixed audio (peak was {mixed_max:.3f})")
            else:
                logger.warning(f"⚠️ Mixed audio is silent!")
            
            logger.info("✅ Stems mixed successfully")
            return mixed
            
        except Exception as e:
            logger.error(f"Error mixing stems: {e}")
            raise
    
    def _chain_with_crossfade(self, clips: List[np.ndarray]) -> np.ndarray:
        """
        Chain clips with crossfading and smooth ending
        
        Args:
            clips: List of audio clips
            
        Returns:
            Chained audio with smooth fade-out at the end
        """
        if len(clips) == 1:
            # Single clip - add fade-out at the end
            return self._add_final_fadeout(clips[0])
        
        try:
            logger.info("Chaining clips with crossfade")
            
            crossfade_samples = int(self.crossfade_duration * self.sample_rate)
            
            # Calculate total length
            total_samples = sum(len(clip) for clip in clips) - (len(clips) - 1) * crossfade_samples
            result = np.zeros(total_samples, dtype=np.float32)
            
            current_pos = 0
            
            for i, clip in enumerate(clips):
                if i == 0:
                    # First clip: no crossfade at start
                    result[current_pos:current_pos + len(clip)] = clip
                    current_pos += len(clip) - crossfade_samples
                elif i == len(clips) - 1:
                    # Last clip: crossfade with previous, then apply fade-out
                    fade_in = np.linspace(0, 1, crossfade_samples)
                    fade_out = np.linspace(1, 0, crossfade_samples)
                    
                    # Crossfade region
                    overlap_start = current_pos
                    overlap_end = current_pos + crossfade_samples
                    
                    # Apply crossfade
                    result[overlap_start:overlap_end] *= fade_out
                    result[overlap_start:overlap_end] += clip[:crossfade_samples] * fade_in
                    
                    # Add rest of clip with fade-out at the very end
                    remaining_start = current_pos + crossfade_samples
                    remaining_clip = clip[crossfade_samples:]
                    
                    # Apply fade-out to the last 2 seconds of the final clip
                    remaining_clip = self._add_final_fadeout(remaining_clip)
                    
                    result[remaining_start:remaining_start + len(remaining_clip)] = remaining_clip
                    current_pos += len(clip)
                else:
                    # Middle clips: crossfade with previous
                    fade_in = np.linspace(0, 1, crossfade_samples)
                    fade_out = np.linspace(1, 0, crossfade_samples)
                    
                    # Crossfade region
                    overlap_start = current_pos
                    overlap_end = current_pos + crossfade_samples
                    
                    # Apply crossfade
                    result[overlap_start:overlap_end] *= fade_out
                    result[overlap_start:overlap_end] += clip[:crossfade_samples] * fade_in
                    
                    # Add rest of clip
                    remaining_start = current_pos + crossfade_samples
                    result[remaining_start:remaining_start + len(clip) - crossfade_samples] = \
                        clip[crossfade_samples:]
                    
                    current_pos += len(clip) - crossfade_samples
            
            logger.info("Crossfade complete with smooth ending")
            return result
            
        except Exception as e:
            logger.error(f"Error in crossfade: {e}")
            raise
    
    def _add_final_fadeout(self, audio: np.ndarray) -> np.ndarray:
        """
        Add smooth fade-out to the end of audio clip
        
        Args:
            audio: Input audio
            
        Returns:
            Audio with fade-out applied to last 2 seconds
        """
        fadeout_duration = self.crossfade_duration  # Use same duration as crossfade (2 seconds)
        fadeout_samples = int(fadeout_duration * self.sample_rate)
        
        # Only fade if audio is longer than fade duration
        if len(audio) <= fadeout_samples:
            # Fade entire clip
            fade_curve = np.linspace(1, 0, len(audio))
            return audio * fade_curve
        
        # Create a copy to avoid modifying original
        faded_audio = audio.copy()
        
        # Apply exponential fade-out to last portion (smoother than linear)
        fade_start = len(faded_audio) - fadeout_samples
        fade_curve = np.power(np.linspace(1, 0, fadeout_samples), 1.5)  # Exponential curve
        faded_audio[fade_start:] *= fade_curve
        
        return faded_audio
    
    def master(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply final mastering to audio
        
        Args:
            audio: Input audio
            
        Returns:
            Mastered audio
        """
        try:
            logger.info("Applying final mastering")
            
            # Log input levels
            input_max = np.abs(audio).max()
            input_rms = np.sqrt(np.mean(audio**2))
            logger.info(f"   Input peak: {input_max:.4f}, RMS: {input_rms:.4f}")
            
            # TODO: Implement advanced mastering
            # - EQ
            # - Compression
            # - Limiting
            # - Stereo enhancement
            
            mastered = audio.copy()
            
            # Normalize to 0.9 to leave headroom
            max_val = np.abs(mastered).max()
            if max_val > 0:
                mastered = mastered / max_val * 0.9
                logger.info(f"   Normalized: peak {max_val:.4f} -> 0.9")
            else:
                logger.warning("   ⚠️ Mastering received silent audio!")
            
            # Apply gentle limiting only to peaks above 0.9
            peaks = np.abs(mastered) > 0.9
            if np.any(peaks):
                # Soft clip peaks using tanh only on the overage
                mastered[peaks] = np.sign(mastered[peaks]) * (0.9 + 0.1 * np.tanh((np.abs(mastered[peaks]) - 0.9) * 10))
                logger.info("   Applied soft limiting to peaks")
            
            # Final check
            output_max = np.abs(mastered).max()
            output_rms = np.sqrt(np.mean(mastered**2))
            logger.info(f"   Output peak: {output_max:.4f}, RMS: {output_rms:.4f}")
            logger.info("Mastering complete")
            
            return mastered
            
        except Exception as e:
            logger.error(f"Error in mastering: {e}")
            raise
    
    def align_beats(self, clip1: np.ndarray, clip2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Align beats between two clips using Librosa
        
        Args:
            clip1: First clip
            clip2: Second clip
            
        Returns:
            Tuple of aligned clips
        """
        # TODO: Implement beat alignment with Librosa
        # - Detect beats in both clips
        # - Time-stretch to align
        logger.info("Beat alignment (placeholder)")
        return clip1, clip2
