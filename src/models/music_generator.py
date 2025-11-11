"""
Music Generator using ACE-Step and MusicControlNet
ZeroGPU Compatible Version
"""
from typing import Dict, Any, Optional, TYPE_CHECKING
import numpy as np
import torch
from pathlib import Path
from loguru import logger
import soundfile as sf

# ZeroGPU support
try:
    import spaces
    ZEROGPU_AVAILABLE = True
    logger.info("ZeroGPU support enabled")
except ImportError:
    ZEROGPU_AVAILABLE = False
    # Create dummy decorator if not available
    def spaces_decorator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if args and callable(args[0]) else decorator
    spaces = type('spaces', (), {'GPU': spaces_decorator})()  # type: ignore

# Import ACE-Step pipeline
if TYPE_CHECKING:
    from acestep.pipeline_ace_step import ACEStepPipeline

try:
    from acestep.pipeline_ace_step import ACEStepPipeline
    ACESTEP_AVAILABLE = True
except ImportError:
    ACESTEP_AVAILABLE = False
    ACEStepPipeline = None  # type: ignore
    logger.warning("ACE-Step not available - install with: pip install git+https://github.com/ACE-Step/ACE-Step.git")


class MusicGenerator:
    """Generates music clips using ACE-Step and MusicControlNet"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize music generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.pipeline = None
        self.device = config.get("models", {}).get("ace_step", {}).get("device", "cuda")
        self.sample_rate = config.get("audio", {}).get("sample_rate", 44100)
        self.clip_duration = config.get("audio", {}).get("clip_duration", 32)
        self.model_path = config.get("models", {}).get("ace_step", {}).get("path", "ACE-Step/ACE-Step-v1-3.5B")
        self.use_local = config.get("models", {}).get("ace_step", {}).get("use_local", False)
        self.num_inference_steps = config.get("models", {}).get("ace_step", {}).get("num_inference_steps", 27)
        self.guidance_scale = config.get("models", {}).get("ace_step", {}).get("guidance_scale", 7.5)
        
        logger.info(f"Music Generator initialized - device: {self.device}")
        
    def load_models(self):
        """Load ACE-Step model"""
        if not ACESTEP_AVAILABLE:
            error_msg = "ACE-Step is not installed. Install with: pip install git+https://github.com/ACE-Step/ACE-Step.git"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        if ACEStepPipeline is None:
            error_msg = "ACEStepPipeline class is not available"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        try:
            logger.info(f"Loading ACE-Step from {self.model_path}")
            
            # Get ACE-Step specific config
            ace_config = self.config.get("models", {}).get("ace_step", {})
            bf16 = ace_config.get("bf16", True)
            torch_compile = ace_config.get("torch_compile", False)
            cpu_offload = ace_config.get("cpu_offload", False)
            overlapped_decode = ace_config.get("overlapped_decode", False)
            device_id = ace_config.get("device_id", 0)
            
            # Determine dtype
            if bf16 and torch.cuda.is_available() and torch.cuda.is_bf16_supported():
                dtype = torch.bfloat16
                logger.info("Using bfloat16 precision")
            elif self.device == "cuda":
                dtype = torch.float16
                logger.info("Using float16 precision")
            else:
                dtype = torch.float32
                logger.info("Using float32 precision")
            
            # Load ACE-Step pipeline with proper parameters
            logger.info("Loading ACE-Step pipeline (this may take 1-2 minutes)...")
            
            self.pipeline = ACEStepPipeline(  # type: ignore
                checkpoint_dir=self.model_path,
                dtype=dtype,
                torch_compile=torch_compile,
                cpu_offload=cpu_offload,
                overlapped_decode=overlapped_decode,
                device_id=device_id
            )
            
            logger.info("ACE-Step model loaded successfully")
            logger.info(f"  - Device: cuda:{device_id}")
            logger.info(f"  - Precision: {dtype}")
            logger.info(f"  - Torch compile: {torch_compile}")
            logger.info(f"  - CPU offload: {cpu_offload}")
            
        except Exception as e:
            logger.error(f"Error loading ACE-Step model: {e}")
            logger.error(f"Make sure the model files are in: {self.model_path}")
            logger.error("Expected structure:")
            logger.error("  models/ACE-Step-HF/")
            logger.error("    ├── ace_step_transformer/")
            logger.error("    ├── music_dcae_f8c8/")
            logger.error("    ├── music_vocoder/")
            logger.error("    └── umt5-base/")
            raise
    
    @spaces.GPU(duration=120)  # Request GPU for 2 minutes for generation
    def generate_clip(
        self,
        prompt: str,
        lyrics: str,
        clip_index: int,
        analysis: Dict[str, Any],
        previous_clip: Optional[np.ndarray] = None,
        use_lora: bool = False,
        lora_path: Optional[str] = None,
        temperature: float = 1.0
    ) -> np.ndarray:
        """
        Generate a single 32-second music clip
        
        Args:
            prompt: User's text prompt
            lyrics: Lyrics for this clip (empty for instrumental)
            clip_index: Index of clip being generated
            analysis: Musical analysis from prompt
            previous_clip: Previous clip for conditioning (if any)
            use_lora: Whether to use LoRA weights
            lora_path: Path to LoRA weights
            temperature: Generation temperature
            
        Returns:
            Generated audio as numpy array
        """
        try:
            logger.info(f"Generating clip {clip_index + 1}")
            
            # Load model if not loaded
            if self.pipeline is None:
                self.load_models()
            
            # Apply LoRA if requested
            if use_lora and lora_path:
                self._apply_lora(lora_path)
            
            # Build the full prompt with musical attributes
            full_prompt = self._build_prompt(prompt, lyrics, analysis)
            
            # Generate conditioning from previous clip if available
            conditioning = None
            if previous_clip is not None:
                conditioning = self._generate_conditioning(previous_clip)
            
            # Generate clip with ACE-Step
            clip = self._generate_with_ace_step(
                prompt=full_prompt,
                lyrics=lyrics,
                analysis=analysis,
                conditioning=conditioning,
                temperature=temperature
            )
            
            # Ensure correct duration and structure
            clip = self._structure_clip(clip)
            
            return clip
            
        except Exception as e:
            logger.error(f"Error generating clip: {e}")
            raise
    
    def _build_prompt(self, prompt: str, lyrics: str, analysis: Dict[str, Any]) -> str:
        """
        Build comprehensive prompt from user input and analysis
        
        Args:
            prompt: Original user prompt
            lyrics: Lyrics (if any)
            analysis: Musical analysis
            
        Returns:
            Enhanced prompt string
        """
        # Extract key attributes
        genre = analysis.get('genre', 'pop')
        style = analysis.get('style', 'modern')
        mood = analysis.get('mood', 'neutral')
        tempo = analysis.get('tempo', 120)
        instruments = analysis.get('instruments', [])
        
        # Build detailed prompt
        parts = []
        
        # Add genre and style
        parts.append(f"{genre} music")
        if style and style.lower() != f"modern {genre.lower()}":
            parts.append(f"{style} style")
        
        # Add mood
        if mood and mood.lower() != 'neutral':
            parts.append(f"{mood} mood")
        
        # Add tempo
        if tempo:
            if tempo < 90:
                parts.append("slow tempo")
            elif tempo > 140:
                parts.append("fast tempo")
            else:
                parts.append("medium tempo")
        
        # Add instruments
        if instruments:
            inst_str = ", ".join(instruments)
            parts.append(f"with {inst_str}")
        
        # Add vocal info
        if lyrics:
            parts.append("with vocals")
        else:
            parts.append("instrumental")
        
        # Combine with original prompt
        full_prompt = ", ".join(parts)
        if prompt:
            full_prompt = f"{prompt}. {full_prompt}"
        
        logger.info(f"Built prompt: {full_prompt}")
        return full_prompt
    
    def _generate_with_ace_step(
        self,
        prompt: str,
        lyrics: str,
        analysis: Dict[str, Any],
        conditioning: Optional[np.ndarray],
        temperature: float
    ) -> np.ndarray:
        """
        Generate audio with ACE-Step model
        
        Returns:
            Generated audio array
        """
        try:
            if self.pipeline is None:
                error_msg = "Pipeline not loaded. Call load_models() first."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            logger.info("Generating audio with ACE-Step")
            
            # ACE-Step parameters
            duration = self.clip_duration  # 32 seconds
            
            # Generate seed for reproducibility
            import random
            seed = random.randint(0, 2**32 - 1)
            
            # Build ACE-Step generation call
            # ACE-Step API: pipeline(prompt, lyrics, audio_duration, infer_step, guidance_scale, ...)
            logger.info(f"ACE-Step generating {duration}s audio")
            logger.info(f"  - Prompt: {prompt[:100]}...")
            logger.info(f"  - Lyrics: {'Yes' if lyrics else 'No'}")
            logger.info(f"  - Steps: {self.num_inference_steps}")
            logger.info(f"  - Guidance: {self.guidance_scale}")
            logger.info(f"  - Seed: {seed}")
            
            # Call ACE-Step pipeline
            audio = self.pipeline(  # type: ignore
                prompt=prompt,
                lyrics=lyrics if lyrics else "",
                audio_duration=duration,
                infer_step=self.num_inference_steps,
                guidance_scale=self.guidance_scale * temperature,
                manual_seeds=[seed],
                scheduler_type="FLOW",  # ACE-Step's scheduler type
                cfg_type="TRIANGULAR"   # CFG type for ACE-Step
            )
            
            logger.info("Audio generation complete")
            
            # ACE-Step returns audio as numpy array
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            
            # Ensure correct shape (mono or stereo)
            if audio.ndim == 2:
                # Already stereo or batch dimension
                if audio.shape[0] == 2:
                    audio = audio.T  # Transpose to (samples, channels)
                elif audio.shape[1] == 2:
                    pass  # Already (samples, channels)
                else:
                    # Take first channel
                    audio = audio[0] if audio.shape[0] < audio.shape[1] else audio[:, 0]
            
            # Flatten to mono if needed (we'll handle stereo in mixing)
            if audio.ndim == 2:
                audio = audio.mean(axis=1 if audio.shape[1] <= 2 else 0)
            
            logger.info(f"Generated audio shape: {audio.shape}, duration: {len(audio)/self.sample_rate:.2f}s")
            
            return audio
            
        except Exception as e:
            logger.error(f"Error in ACE-Step generation: {e}")
            logger.exception("Full traceback:")
            # Fallback to silence if generation fails
            logger.warning("Falling back to silence generation")
            duration_samples = int(self.clip_duration * self.sample_rate)
            return np.zeros(duration_samples, dtype=np.float32)
    
    def _generate_conditioning(self, previous_clip: np.ndarray) -> np.ndarray:
        """
        Generate conditioning signal from previous clip using MusicControlNet
        
        Args:
            previous_clip: Previous audio clip
            
        Returns:
            Conditioning signal
        """
        # TODO: Implement MusicControlNet conditioning
        
        # Extract lead-out section (last 2 seconds) from previous clip
        lead_out_samples = int(2 * self.sample_rate)
        lead_out = previous_clip[-lead_out_samples:]
        
        # Placeholder: return lead-out as conditioning
        return lead_out
    
    def _structure_clip(self, clip: np.ndarray) -> np.ndarray:
        """
        Structure clip with lead-in, main, and lead-out sections
        
        Args:
            clip: Raw generated clip
            
        Returns:
            Structured clip
        """
        # Ensure correct total duration
        expected_samples = int(self.clip_duration * self.sample_rate)
        
        if len(clip) < expected_samples:
            # Pad if too short
            padding = expected_samples - len(clip)
            clip = np.pad(clip, (0, padding), mode='constant')
        elif len(clip) > expected_samples:
            # Truncate if too long
            clip = clip[:expected_samples]
        
        # Mark sections (conceptually - actual structuring would be in generation)
        # 2s lead-in, 28s main, 2s lead-out
        
        return clip
    
    def _apply_lora(self, lora_path: str):
        """
        Apply LoRA weights to model
        
        Args:
            lora_path: Path to LoRA weights
        """
        try:
            logger.info(f"Applying LoRA weights from {lora_path}")
            
            if self.pipeline is None:
                logger.error("Pipeline not loaded, cannot apply LoRA")
                return
            
            # Load LoRA weights
            self.pipeline.load_lora_weights(lora_path)
            logger.info("LoRA weights applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying LoRA: {e}")
    
    def unload_models(self):
        """Unload models to free memory"""
        try:
            if self.pipeline is not None:
                del self.pipeline
                self.pipeline = None
                
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info("Models unloaded successfully")
                
        except Exception as e:
            logger.error(f"Error unloading models: {e}")
