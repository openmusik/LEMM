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
    import spaces  # type: ignore
    ZEROGPU_AVAILABLE = True
    logger.info("ZeroGPU support enabled")
except ImportError:
    ZEROGPU_AVAILABLE = False
    # Create dummy decorator if not available
    def spaces_decorator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if args and callable(args[0]) else decorator
    
    class MockSpaces:
        GPU = spaces_decorator
    
    spaces = MockSpaces()  # type: ignore

# Import music generation models
if TYPE_CHECKING:
    from acestep.pipeline_ace_step import ACEStepPipeline
    from src.models.musicgen_pipeline import MusicGenPipeline
    from src.models.vocal_synthesizer import VocalSynthesizer

try:
    from acestep.pipeline_ace_step import ACEStepPipeline
    ACESTEP_AVAILABLE = True
except (ImportError, RuntimeError, ModuleNotFoundError) as e:
    ACESTEP_AVAILABLE = False
    ACEStepPipeline = None  # type: ignore
    logger.warning(f"ACE-Step not available: {type(e).__name__}: {str(e)[:100]}")
    logger.info("Install ACE-Step with: pip install git+https://github.com/ACE-Step/ACE-Step.git")

try:
    from src.models.musicgen_pipeline import MusicGenPipeline
    MUSICGEN_AVAILABLE = True
except ImportError:
    MUSICGEN_AVAILABLE = False
    MusicGenPipeline = None  # type: ignore
    logger.warning("MusicGen not available - install with: pip install audiocraft")

try:
    from src.models.vocal_synthesizer import VocalSynthesizer
    VOCAL_SYNTH_AVAILABLE = True
except ImportError:
    VOCAL_SYNTH_AVAILABLE = False
    VocalSynthesizer = None  # type: ignore
    logger.warning("Vocal synthesizer not available")

# Import model selector
from src.models.model_selector import ModelSelector, ModelType


class MusicGenerator:
    """Generates music clips using ACE-Step, MusicGen, and MusicControlNet"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize music generator with automatic model selection
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.pipeline = None
        self.active_model_type = None
        self.vocal_synthesizer = None
        
        # NOTE: Vocal synthesizer is ONLY needed for MusicGen (instrumental-only model)
        # ACE-Step has native vocal generation built-in when lyrics are provided
        # We'll initialize vocal synthesizer later if MusicGen is selected
        
        # Initialize model selector
        self.model_selector = ModelSelector()
        
        # Detect available models and select best one
        available_models = self.model_selector.detect_available_models()
        logger.info(f"Available models detected: {list(available_models.keys())}")
        
        # Store availability for UI
        self.ace_step_available = available_models.get("ace_step", {}).get("available", False)
        self.musicgen_available = available_models.get("musicgen", {}).get("available", False)
        
        # Get user preference from config if available
        user_preference = config.get("models", {}).get("preferred_model", "auto")
        if user_preference not in ["ace_step", "musicgen", "auto"]:
            logger.warning(f"Invalid model preference '{user_preference}', using auto")
            user_preference = "auto"
        
        # Select best model
        selected_model, reason = self.model_selector.select_best_model(user_preference)
        logger.info(f"Selected model: {selected_model} - {reason}")
        
        # Store selected model for UI
        self.selected_model = selected_model
        
        if not selected_model:
            raise RuntimeError("No music generation models available. Install ACE-Step or MusicGen.")
        
        self.active_model_type = selected_model
        self.device = config.get("models", {}).get("ace_step", {}).get("device", "cuda")
        self.sample_rate = config.get("audio", {}).get("sample_rate", 44100)
        self.clip_duration = config.get("audio", {}).get("clip_duration", 32)
        self.model_path = config.get("models", {}).get("ace_step", {}).get("path", "ACE-Step/ACE-Step-v1-3.5B")
        self.use_local = config.get("models", {}).get("ace_step", {}).get("use_local", False)
        self.num_inference_steps = config.get("models", {}).get("ace_step", {}).get("num_inference_steps", 27)
        
        # Initialize selected model
        if self.active_model_type == "ace_step":
            logger.info("🎵 Initializing ACE-Step for music generation")
            self._init_ace_step()
        elif self.active_model_type == "musicgen":
            logger.info("🎶 Initializing MusicGen for music generation")
            self._init_musicgen()
        else:
            raise RuntimeError(f"Unsupported model type: {self.active_model_type}")
        self.guidance_scale = config.get("models", {}).get("ace_step", {}).get("guidance_scale", 7.5)
        
        logger.info(f"Music Generator initialized - device: {self.device}")
        
    def _init_ace_step(self):
        """Initialize ACE-Step model (has native vocal generation)"""
        if not ACESTEP_AVAILABLE:
            logger.warning("ACE-Step selected but not available - falling back to MusicGen")
            logger.info("Install ACE-Step with: pip install git+https://github.com/ACE-Step/ACE-Step.git")
            self.active_model_type = "musicgen"
            self._init_musicgen()
            return
        
        logger.info("🎤 ACE-Step has NATIVE vocal generation - no separate TTS needed")
        # Use existing load_models method for ACE-Step
        self.load_models()
    
    def _init_musicgen(self):
        """Initialize MusicGen model"""
        logger.info("🎵 Initializing MusicGen pipeline")
        
        # Initialize vocal synthesizer for MusicGen (since MusicGen only generates instrumental)
        if VOCAL_SYNTH_AVAILABLE and VocalSynthesizer is not None:
            try:
                logger.info("🎤 Initializing vocal synthesizer for MusicGen...")
                self.vocal_synthesizer = VocalSynthesizer(self.config)
                logger.info("✅ Vocal synthesizer ready (for MusicGen vocal synthesis)")
            except Exception as e:
                logger.warning(f"⚠️ Vocal synthesizer init failed: {e}")
                logger.info("💡 MusicGen will generate instrumental-only")
        else:
            logger.info("💡 Vocal synthesizer not available - MusicGen will be instrumental-only")
        
        if not MUSICGEN_AVAILABLE:
            logger.error("MusicGen dependencies not available")
            raise ImportError("MusicGen is not installed. Install with: pip install audiocraft")
        
        try:
            # Get MusicGen model path from config or use default
            musicgen_config = self.config.get("models", {}).get("musicgen", {})
            model_name = musicgen_config.get("model", "facebook/musicgen-medium")
            
            logger.info(f"Loading MusicGen model: {model_name}")
            logger.info("This may take a while on first run (downloading model weights)")
            
            # Create MusicGen pipeline with compatible interface
            if MusicGenPipeline is None:
                logger.error("MusicGenPipeline class not available")
                raise ImportError("MusicGenPipeline not available")
            
            self.pipeline = MusicGenPipeline(
                model_path=model_name,
                device=self.device,
                dtype="float32",  # MusicGen works best with float32
                torch_compile=False  # Can be enabled later
            )
            
            # Update sample rate to match MusicGen
            self.sample_rate = self.pipeline.sample_rate
            logger.info(f"MusicGen sample rate: {self.sample_rate} Hz")
            
            self.loaded = True
            logger.info("✅ MusicGen model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load MusicGen: {e}")
            raise
        
    def load_models(self):  
        """Load ACE-Step model"""
        logger.info("🚀 Initializing ACE-Step pipeline")
        
        if not ACESTEP_AVAILABLE:
            error_msg = "ACE-Step is not installed. Install with: pip install git+https://github.com/ACE-Step/ACE-Step.git"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        if ACEStepPipeline is None:
            error_msg = "ACEStepPipeline class is not available"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        # Check GPU availability for ACE-Step
        import torch
        if not torch.cuda.is_available():
            logger.warning("⚠️ No CUDA GPU detected - ACE-Step performance may be poor")
            
        try:
            logger.info(f"Loading ACE-Step from {self.model_path}")
            logger.info("This may take several minutes on first run (downloading model weights)")
            
            # Get ACE-Step specific config
            ace_config = self.config.get("models", {}).get("ace_step", {})
            bf16 = ace_config.get("bf16", True)
            torch_compile = ace_config.get("torch_compile", False)
            cpu_offload = ace_config.get("cpu_offload", False)
            overlapped_decode = ace_config.get("overlapped_decode", False)
            device_id = ace_config.get("device_id", 0)
            
            # Adjust settings for CPU
            if self.device == "cpu":
                bf16 = False  # bfloat16 not supported on CPU
                cpu_offload = False  # No point on CPU-only
                overlapped_decode = False  # May cause issues on CPU
                logger.info("CPU mode: disabled bf16, cpu_offload, and overlapped_decode")
            
            # Determine dtype (ACE-Step expects string format)
            if bf16 and torch.cuda.is_available() and torch.cuda.is_bf16_supported():
                dtype = "bfloat16"
                logger.info("Using bfloat16 precision")
            elif self.device == "cuda":
                dtype = "float16"
                logger.info("Using float16 precision")
            else:
                dtype = "float32"
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
            # Show correct device info
            device_info = f"cpu" if self.device == "cpu" else f"cuda:{device_id}"
            logger.info(f"  - Device: {device_info}")
            logger.info(f"  - Precision: {dtype}")
            logger.info(f"  - Torch compile: {torch_compile}")
            logger.info(f"  - CPU offload: {cpu_offload}")
            
            # Warn about CPU performance
            if self.device == "cpu":
                logger.warning("Running on CPU - generation will be significantly slower")
                logger.info("Consider using a system with NVIDIA GPU for faster generation")
            
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
            logger.info(f"Generating clip {clip_index + 1} using {self.active_model_type}")
            
            # Validate model availability
            if self.active_model_type == "ace_step" and not self.ace_step_available:
                error_msg = "ACE-Step selected but not available on this system"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            if self.active_model_type == "musicgen" and not self.musicgen_available:
                error_msg = "MusicGen selected but not installed. Install with: pip install audiocraft"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Load model if not loaded
            if self.pipeline is None:
                logger.info(f"Loading {self.active_model_type} pipeline")
                if self.active_model_type == "ace_step":
                    self.load_models()
                elif self.active_model_type == "musicgen":
                    self._init_musicgen()
                else:
                    raise RuntimeError(f"Unknown model type: {self.active_model_type}")
            
            # Route to appropriate generation method
            if self.active_model_type == "ace_step":
                return self._generate_clip_ace_step(prompt, lyrics, clip_index, analysis, previous_clip, use_lora, lora_path, temperature)
            elif self.active_model_type == "musicgen":
                return self._generate_clip_musicgen(prompt, lyrics, clip_index, analysis, previous_clip, use_lora, lora_path, temperature)
            else:
                raise RuntimeError(f"Unsupported model type: {self.active_model_type}")
                
        except Exception as e:
            logger.error(f"Error in generate_clip (model: {self.active_model_type}): {e}")
            logger.error(f"Available models - ACE-Step: {self.ace_step_available}, MusicGen: {self.musicgen_available}")
            
            # Try to provide helpful error context
            if "Permission denied" in str(e) and self.active_model_type == "ace_step":
                logger.error("ACE-Step Permission Denied - likely AMD GPU incompatibility")
                if self.musicgen_available:
                    logger.info("Consider using MusicGen for CPU-compatible generation")
            
            raise
    
    def _generate_clip_ace_step(
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
        """Generate clip using ACE-Step (has native vocal generation built-in)
        
        ACE-Step natively generates vocals when lyrics are provided.
        No separate vocal synthesis step is needed.
        """
        try:
            logger.info(f"ACE-Step generation - clip {clip_index + 1}")
            
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
            logger.error(f"Error generating ACE-Step clip: {e}")
            raise
    
    def _generate_clip_musicgen(
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
        """Generate clip using MusicGen with optional vocal synthesis"""
        try:
            logger.info(f"MusicGen generation - clip {clip_index + 1}")
            
            # LoRA not supported by MusicGen yet
            if use_lora and lora_path:
                logger.warning("LoRA not supported by MusicGen - ignoring LoRA request")
            
            # Build the full prompt with musical attributes (instrumental description)
            instrumental_prompt = self._build_instrumental_prompt(prompt, analysis)
            
            # Note: MusicGen doesn't support conditioning from previous clips yet
            # This could be added in future versions
            if previous_clip is not None:
                logger.info("Previous clip conditioning not yet supported by MusicGen")
            
            # Generate instrumental track with MusicGen
            logger.info(f"Generating instrumental with MusicGen: '{instrumental_prompt[:50]}...'")
            
            # Use the pipeline (which has ACE-Step compatible interface)
            if self.pipeline is None:
                raise RuntimeError("MusicGen pipeline not initialized")
                
            audio_list = self.pipeline(
                prompt=instrumental_prompt,
                lyrics="",  # MusicGen generates instrumental only
                audio_duration=self.clip_duration,
                infer_step=50,  # Not used by MusicGen but required for interface
                guidance_scale=self.guidance_scale,  # Not used by MusicGen
                manual_seeds=[42 + clip_index]  # Deterministic seeds per clip
            )
            
            # Extract audio from list (MusicGen wrapper returns list like ACE-Step)
            if isinstance(audio_list, list) and len(audio_list) > 0:
                instrumental = audio_list[0]
            else:
                instrumental = audio_list
            
            # Ensure it's a numpy array
            if not isinstance(instrumental, np.ndarray):
                instrumental = np.array(instrumental)
            
            # If lyrics provided, synthesize vocals and mix with instrumental
            if lyrics and lyrics.strip() and self.vocal_synthesizer is not None:
                logger.info("Synthesizing vocal track from lyrics")
                
                try:
                    # Synthesize vocals
                    vocal_audio = self.vocal_synthesizer.synthesize(
                        lyrics=lyrics,
                        style=analysis
                    )
                    
                    # Match lengths (trim or pad to instrumental length)
                    target_length = len(instrumental)
                    if len(vocal_audio) > target_length:
                        vocal_audio = vocal_audio[:target_length]
                    elif len(vocal_audio) < target_length:
                        # Pad with silence
                        padding = np.zeros(target_length - len(vocal_audio), dtype=np.float32)
                        vocal_audio = np.concatenate([vocal_audio, padding])
                    
                    # Mix vocals with instrumental (70% instrumental, 30% vocals for balance)
                    mixed_audio = 0.7 * instrumental + 0.3 * vocal_audio
                    
                    # Normalize to prevent clipping
                    max_val = np.abs(mixed_audio).max()
                    if max_val > 1.0:
                        mixed_audio = mixed_audio / max_val * 0.95
                    
                    logger.info("✅ Vocals synthesized and mixed with instrumental")
                    audio = mixed_audio
                    
                except Exception as e:
                    logger.error(f"Vocal synthesis failed: {e}")
                    logger.warning("Using instrumental-only version")
                    audio = instrumental
            else:
                # No lyrics or no synthesizer - use instrumental only
                if lyrics and lyrics.strip():
                    logger.warning("Lyrics provided but vocal synthesizer not available")
                audio = instrumental
            
            # Ensure correct duration and structure
            clip = self._structure_clip(audio)
            
            logger.info(f"✅ MusicGen clip generated - duration: {len(clip)/self.sample_rate:.2f}s")
            
            return clip
            
        except Exception as e:
            logger.error(f"Error generating MusicGen clip: {e}")
            raise
    
    def _build_instrumental_prompt(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Build instrumental-only prompt for MusicGen"""
        # Extract musical elements
        genre = analysis.get('genre', '')
        style = analysis.get('style', '')
        mood = analysis.get('mood', '')
        tempo = analysis.get('tempo', '')
        instruments = analysis.get('instruments', [])
        
        # Build descriptive instrumental prompt
        parts = []
        if genre:
            parts.append(f"{genre}")
        if style:
            parts.append(f"{style} style")
        if mood:
            parts.append(f"{mood.lower()} mood")
        if instruments:
            parts.append(f"with {', '.join(instruments)}")
        if tempo:
            parts.append(f"{tempo} BPM")
        
        # Add "instrumental" to ensure no vocals from MusicGen
        parts.append("instrumental")
        
        instrumental_prompt = " ".join(parts) if parts else prompt + " instrumental"
        
        return instrumental_prompt
    
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
            
            # Call ACE-Step pipeline with proper error handling for CPU
            # Note: ACE-Step may have CUDA hardcoded dependencies that cause Permission Denied errors on CPU
            try:
                logger.info("🎤 Calling ACE-Step pipeline...")
                logger.info(f"   Device: {self.device}")
                logger.info(f"   CUDA available: {torch.cuda.is_available()}")
                if torch.cuda.is_available():
                    logger.info(f"   CUDA device: {torch.cuda.get_device_name(0)}")
                
                audio = self.pipeline(  # type: ignore
                    prompt=prompt,
                    lyrics=lyrics if lyrics else "",
                    audio_duration=duration,
                    infer_step=self.num_inference_steps,
                    guidance_scale=self.guidance_scale * temperature,
                    manual_seeds=[seed]
                )
                
                logger.info("✅ ACE-Step pipeline call completed")
            except PermissionError as pe:
                logger.error(f"Permission denied (Error 13) during ACE-Step generation: {pe}")
                logger.error("This often indicates CUDA dependencies in ACE-Step that don't work on CPU")
                logger.error("ACE-Step may require NVIDIA GPU despite CPU device setting")
                raise RuntimeError(
                    "ACE-Step generation failed with Permission Denied error. "
                    "This model appears to require NVIDIA GPU hardware. "
                    "Consider using the HuggingFace Space deployment with ZeroGPU instead."
                ) from pe
            except Exception as e:
                logger.error(f"ACE-Step generation failed: {e}")
                raise
            
            logger.info(f"Raw audio output type: {type(audio)}")
            
            # Handle ACE-Step audio output (can be list, tensor, or numpy array)
            if isinstance(audio, list):
                logger.info(f"Audio is list with {len(audio)} items")
                # ACE-Step returns a list - get first item
                if len(audio) > 0:
                    audio = audio[0]
                    logger.info(f"Extracted first item, type: {type(audio)}")
                else:
                    raise ValueError("Empty audio list returned from ACE-Step")
            
            if isinstance(audio, torch.Tensor):
                logger.info(f"Converting torch.Tensor to numpy - shape: {audio.shape}")
                audio = audio.cpu().numpy()
            elif not isinstance(audio, np.ndarray):
                logger.info(f"Converting {type(audio)} to numpy array")
                audio = np.array(audio)
            
            # Ensure correct shape (mono or stereo)
            if hasattr(audio, 'ndim') and audio.ndim == 2:
                # Already stereo or batch dimension
                if audio.shape[0] == 2:
                    audio = audio.T  # Transpose to (samples, channels)
                elif audio.shape[1] == 2:
                    pass  # Already (samples, channels)
                else:
                    # Take first channel
                    audio = audio[0] if audio.shape[0] < audio.shape[1] else audio[:, 0]
            
            # Flatten to mono if needed (we'll handle stereo in mixing)
            if hasattr(audio, 'ndim') and audio.ndim == 2:
                audio = audio.mean(axis=1 if audio.shape[1] <= 2 else 0)
            
            logger.info(f"Generated audio shape: {audio.shape}, duration: {len(audio)/self.sample_rate:.2f}s")
            
            # Validate generated audio is not silent
            audio_max = np.abs(audio).max()
            audio_rms = np.sqrt(np.mean(audio**2))
            logger.info(f"Generated audio levels - peak: {audio_max:.4f}, RMS: {audio_rms:.4f}")
            
            if audio_max < 1e-6:
                logger.error("❌ Generated audio is completely silent!")
                raise RuntimeError("ACE-Step generated silent audio - this indicates a generation failure")
            
            return audio
            
        except Exception as e:
            logger.error(f"Error in ACE-Step generation: {e}")
            logger.exception("Full traceback:")
            # Don't fallback to silence - raise error so user knows generation failed
            raise RuntimeError(f"ACE-Step generation failed: {e}") from e
    
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
            lora_config = self.config.get("lora", {})
            lora_weight = lora_config.get("alpha", 1.0)
            self.pipeline.load_lora(lora_path, lora_weight)
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
