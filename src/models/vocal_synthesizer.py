"""
Vocal Synthesizer for Singing Voice Generation
Supports CPU-compatible text-to-singing synthesis
"""
from typing import Dict, Any, Optional, Union
import numpy as np
from pathlib import Path
from loguru import logger
import torch

try:
    import piper_tts
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False

try:
    from bark import SAMPLE_RATE, generate_audio, preload_models
    BARK_AVAILABLE = True
except ImportError:
    BARK_AVAILABLE = False


class VocalSynthesizer:
    """
    Synthesizes singing vocals from lyrics
    
    Supports multiple backends:
    - Piper TTS (CPU-friendly, fast, good quality)
    - Bark (CPU-compatible, expressive, slower)
    - Placeholder (fallback when no TTS available)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vocal synthesizer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.vocal_config = config.get('models', {}).get('vocal_synthesis', {})
        self.device = self._get_device()
        self.backend = None
        self.model = None
        
        # Initialize based on available backends
        self._initialize_backend()
        
        logger.info(f"Vocal Synthesizer initialized with backend: {self.backend}")
    
    def _get_device(self) -> str:
        """Determine computation device"""
        device_setting = self.vocal_config.get('device', 'auto')
        
        if device_setting == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return device_setting
    
    def _initialize_backend(self):
        """Initialize the best available TTS backend"""
        preferred_backend = self.vocal_config.get('backend', 'auto')
        
        if preferred_backend == 'auto':
            # Auto-detect best available backend
            if PIPER_AVAILABLE:
                self._init_piper()
            elif BARK_AVAILABLE:
                self._init_bark()
            else:
                self._init_placeholder()
        elif preferred_backend == 'piper' and PIPER_AVAILABLE:
            self._init_piper()
        elif preferred_backend == 'bark' and BARK_AVAILABLE:
            self._init_bark()
        else:
            logger.warning(f"Requested backend '{preferred_backend}' not available, using placeholder")
            self._init_placeholder()
    
    def _init_piper(self):
        """Initialize Piper TTS backend"""
        try:
            # Piper is lightweight and CPU-friendly
            self.backend = 'piper'
            # Model will be loaded on first synthesis
            logger.info("✅ Piper TTS backend initialized (CPU-friendly)")
        except Exception as e:
            logger.error(f"Failed to initialize Piper: {e}")
            self._init_placeholder()
    
    def _init_bark(self):
        """Initialize Bark TTS backend"""
        try:
            self.backend = 'bark'
            # Preload models for faster generation
            if self.vocal_config.get('preload_models', False):
                preload_models()
                logger.info("✅ Bark models preloaded")
            logger.info("✅ Bark TTS backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Bark: {e}")
            self._init_placeholder()
    
    def _init_placeholder(self):
        """Initialize placeholder backend (no actual synthesis)"""
        self.backend = 'placeholder'
        logger.warning("⚠️ No TTS backend available - using placeholder mode")
        logger.info("💡 Install piper-tts for CPU-compatible vocal synthesis:")
        logger.info("   pip install piper-tts")
    
    def synthesize(
        self,
        lyrics: str,
        style: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> np.ndarray:
        """
        Synthesize singing voice from lyrics
        
        Args:
            lyrics: Text lyrics to synthesize
            style: Style parameters (tempo, mood, gender, etc.)
            output_path: Optional path to save audio
            
        Returns:
            Audio array (numpy array)
        """
        if not lyrics or lyrics.strip() == "":
            logger.warning("Empty lyrics provided, returning silence")
            return self._generate_silence(duration=1.0)
        
        logger.info(f"Synthesizing vocals with {self.backend} backend")
        
        # Route to appropriate backend
        if self.backend == 'piper':
            audio = self._synthesize_piper(lyrics, style)
        elif self.backend == 'bark':
            audio = self._synthesize_bark(lyrics, style)
        else:
            audio = self._synthesize_placeholder(lyrics, style)
        
        # Save if output path provided
        if output_path:
            self._save_audio(audio, output_path)
        
        return audio
    
    def _synthesize_piper(self, lyrics: str, style: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Synthesize with Piper TTS"""
        try:
            # Piper implementation would go here
            # For now, return placeholder
            logger.warning("Piper synthesis not yet fully implemented")
            return self._synthesize_placeholder(lyrics, style)
        except Exception as e:
            logger.error(f"Piper synthesis failed: {e}")
            return self._synthesize_placeholder(lyrics, style)
    
    def _synthesize_bark(self, lyrics: str, style: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Synthesize with Bark TTS"""
        try:
            # Clean lyrics for better synthesis
            text = self._prepare_lyrics_for_tts(lyrics)
            
            # Bark supports voice presets for different styles
            # Default to a pleasant singing voice
            audio_array = generate_audio(
                text,
                history_prompt=style.get('voice_preset', 'v2/en_speaker_6') if style else 'v2/en_speaker_6'
            )
            
            logger.info(f"✅ Bark synthesis complete: {len(audio_array)} samples")
            return audio_array
            
        except Exception as e:
            logger.error(f"Bark synthesis failed: {e}")
            return self._synthesize_placeholder(lyrics, style)
    
    def _synthesize_placeholder(self, lyrics: str, style: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Generate placeholder audio (silence with analysis logging)"""
        logger.info(f"Placeholder synthesis for lyrics ({len(lyrics)} chars)")
        
        # Estimate duration based on lyrics length (rough estimate: 4 chars/second)
        duration = max(1.0, len(lyrics) / 4.0)
        
        return self._generate_silence(duration)
    
    def _prepare_lyrics_for_tts(self, lyrics: str) -> str:
        """
        Prepare lyrics for TTS synthesis
        
        Args:
            lyrics: Raw lyrics text
            
        Returns:
            Cleaned lyrics suitable for TTS
        """
        # Remove section markers like [Verse 1], [Chorus], etc.
        import re
        text = re.sub(r'\[.*?\]', '', lyrics)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length to prevent extremely long synthesis
        max_chars = self.vocal_config.get('max_chars', 2000)
        if len(text) > max_chars:
            logger.warning(f"Lyrics truncated from {len(text)} to {max_chars} chars")
            text = text[:max_chars]
        
        return text
    
    def _generate_silence(self, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """Generate silence array"""
        num_samples = int(duration * sample_rate)
        return np.zeros(num_samples, dtype=np.float32)
    
    def _save_audio(self, audio: np.ndarray, output_path: Union[str, Path]):
        """Save audio to file"""
        try:
            import soundfile as sf
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            sample_rate = self.vocal_config.get('sample_rate', 44100)
            sf.write(str(output_path), audio, sample_rate)
            
            logger.info(f"✅ Audio saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about current backend"""
        return {
            'backend': self.backend,
            'device': self.device,
            'available_backends': {
                'piper': PIPER_AVAILABLE,
                'bark': BARK_AVAILABLE
            },
            'cpu_compatible': True  # All backends support CPU
        }
    
    def estimate_synthesis_time(self, lyrics: str) -> float:
        """
        Estimate synthesis time in seconds
        
        Args:
            lyrics: Lyrics to synthesize
            
        Returns:
            Estimated time in seconds
        """
        char_count = len(lyrics)
        
        # Rough estimates based on backend and hardware
        if self.backend == 'piper':
            # Piper is fast: ~0.01s per character on CPU
            return char_count * 0.01
        elif self.backend == 'bark':
            # Bark is slower: ~0.1s per character on CPU, ~0.02s on GPU
            multiplier = 0.02 if self.device == 'cuda' else 0.1
            return char_count * multiplier
        else:
            # Placeholder is instant
            return 0.1
