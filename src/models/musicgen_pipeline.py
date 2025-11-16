"""
MusicGen Pipeline Wrapper for LEMM
Provides same interface as ACE-Step for seamless integration
Uses HuggingFace Transformers (no audiocraft dependency required)
"""
from typing import Dict, Any, Optional, Union, List
import torch
import numpy as np
from loguru import logger
import scipy.io.wavfile as wavfile
from pathlib import Path

# MusicGen imports with error handling - using transformers instead of audiocraft
try:
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    MUSICGEN_AVAILABLE = True
    logger.info("✅ MusicGen (transformers) imports successful")
except ImportError as e:
    MUSICGEN_AVAILABLE = False
    AutoProcessor = None  # type: ignore
    MusicgenForConditionalGeneration = None  # type: ignore
    logger.warning(f"❌ MusicGen not available: {e}")


class MusicGenPipeline:
    """
    MusicGen Pipeline wrapper that mimics ACE-Step interface
    
    This wrapper allows MusicGen to be used as a drop-in replacement for ACE-Step
    while maintaining the same method signatures and behavior.
    """
    
    def __init__(
        self,
        model_path: str = "facebook/musicgen-medium",
        device: str = "auto",
        dtype: str = "float32",
        bf16: bool = False,
        cpu_offload: bool = False,
        overlapped_decode: bool = False,
        torch_compile: bool = False
    ):
        """
        Initialize MusicGen pipeline
        
        Args:
            model_path: HuggingFace model name or local path
            device: Device to use ("cuda", "cpu", or "auto")
            dtype: Data type for computations
            bf16: Use bfloat16 (ignored for MusicGen)
            cpu_offload: CPU offloading (ignored for MusicGen)  
            overlapped_decode: Overlapped decoding (ignored for MusicGen)
            torch_compile: Use torch.compile (applied to MusicGen)
        """
        if not MUSICGEN_AVAILABLE:
            raise ImportError("MusicGen not available. Install transformers with: pip install transformers")
        
        self.model_path = model_path
        self.device = self._resolve_device(device)
        self.dtype = dtype
        self.torch_compile = torch_compile
        
        # MusicGen doesn't use these parameters, but we store them for compatibility
        self.bf16 = bf16
        self.cpu_offload = cpu_offload
        self.overlapped_decode = overlapped_decode
        
        # Type hints for model and processor
        self.model: Optional[Any] = None  # MusicgenForConditionalGeneration
        self.processor: Optional[Any] = None  # AutoProcessor
        self.sample_rate = 32000  # MusicGen default sample rate
        
        logger.info(f"MusicGenPipeline initialized with model: {model_path}")
        logger.info(f"Device: {self.device}, dtype: {dtype}")
        
        # Load the model
        self._load_model()
    
    def _resolve_device(self, device: str) -> str:
        """Resolve device string to actual device"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _remove_parametrizations(self):
        """
        Remove parametrizations (e.g., weight_norm) from MusicGen model
        to enable serialization for ZeroGPU compatibility
        """
        try:
            from torch.nn.utils import parametrize
            
            # Recursively check all modules and remove parametrizations
            removed_count = 0
            for name, module in self.model.named_modules():
                if parametrize.is_parametrized(module):
                    # Get all parametrized attributes
                    for param_name in list(module.parametrizations.keys()):
                        parametrize.remove_parametrizations(module, param_name, leave_parametrized=True)
                        removed_count += 1
                        logger.debug(f"Removed parametrization from {name}.{param_name}")
            
            if removed_count > 0:
                logger.info(f"✓ Removed {removed_count} parametrizations for ZeroGPU compatibility")
            else:
                logger.debug("No parametrizations found in model")
                
        except Exception as e:
            logger.warning(f"Could not remove parametrizations: {e}")
            logger.warning("Model may not be serializable for ZeroGPU")
    
    def _load_model(self):
        """Load MusicGen model from HuggingFace transformers"""
        try:
            logger.info(f"Loading MusicGen model: {self.model_path}")
            
            # Load processor and model using transformers
            self.processor = AutoProcessor.from_pretrained(self.model_path)
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32 if self.dtype == "float32" else torch.float16
            )
            
            # CRITICAL: Remove parametrizations to enable serialization (for ZeroGPU)
            # MusicGen uses weight normalization which cannot be pickled
            self._remove_parametrizations()
            
            # Move to device
            self.model = self.model.to(self.device)
            
            # Apply torch.compile if requested
            if self.torch_compile and hasattr(torch, 'compile'):
                logger.info("Applying torch.compile to MusicGen model")
                self.model = torch.compile(self.model)
            
            # Set sample rate from model config
            if hasattr(self.model.config, 'audio_encoder'):
                # MusicGen uses 32kHz by default
                self.sample_rate = 32000
            
            logger.info(f"✅ MusicGen model loaded successfully on {self.device}")
            logger.info(f"   Sample rate: {self.sample_rate} Hz")
            logger.info(f"Model sample rate: {self.sample_rate} Hz")
            
        except Exception as e:
            logger.error(f"Failed to load MusicGen model: {e}")
            raise
    
    def __call__(
        self,
        prompt: str,
        lyrics: str = "",
        audio_duration: int = 30,
        infer_step: int = 50,
        guidance_scale: float = 7.5,
        manual_seeds: Optional[List[int]] = None,
        **kwargs
    ) -> List[np.ndarray]:
        """
        Generate music using MusicGen (ACE-Step compatible interface)
        
        Args:
            prompt: Text description of the music
            lyrics: Lyrics (not used by MusicGen currently)
            audio_duration: Duration in seconds
            infer_step: Number of inference steps (not used by MusicGen)
            guidance_scale: Guidance scale (used for transformers MusicGen)
            manual_seeds: Random seeds for generation
            **kwargs: Additional arguments
            
        Returns:
            List containing generated audio as numpy array
        """
        try:
            logger.info(f"Generating music with MusicGen: '{prompt[:50]}...'")
            logger.info(f"Duration: {audio_duration}s, Device: {self.device}")
            
            # Prepare prompt (combine with lyrics if provided)
            full_prompt = prompt
            if lyrics and lyrics.strip():
                full_prompt = f"{prompt} with lyrics: {lyrics[:100]}..."
                logger.info("Lyrics included in prompt (MusicGen doesn't support separate lyrics)")
            
            # Set seed if provided
            if manual_seeds and len(manual_seeds) > 0:
                seed = manual_seeds[0]
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
                logger.info(f"Random seed set to: {seed}")
            
            # Process prompt text
            inputs = self.processor(
                text=[full_prompt],
                padding=True,
                return_tensors="pt"
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Calculate max_new_tokens from duration
            # MusicGen generates at ~50 tokens per second
            max_new_tokens = int(audio_duration * 50)
            
            # Generate audio
            logger.info(f"Starting MusicGen generation (max_new_tokens={max_new_tokens})...")
            with torch.no_grad():
                audio_values = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    guidance_scale=guidance_scale if guidance_scale > 1.0 else None
                )
            
            # Convert to numpy array
            audio_np = audio_values[0, 0].cpu().numpy()
            
            logger.info(f"✅ MusicGen generation complete - shape: {audio_np.shape}")
            logger.info(f"Generated {len(audio_np)/self.sample_rate:.2f}s of audio")
            
            # Return as list to match ACE-Step interface
            return [audio_np]
            
        except Exception as e:
            logger.error(f"MusicGen generation failed: {e}")
            raise
    
    def load_lora(self, lora_path: str, lora_weight: float = 1.0):
        """
        Load LoRA weights (compatibility method - MusicGen doesn't support LoRA yet)
        
        Args:
            lora_path: Path to LoRA weights
            lora_weight: LoRA weight scale
        """
        logger.warning("MusicGen doesn't support LoRA weights yet - ignoring load_lora call")
        logger.info(f"Requested LoRA: {lora_path} with weight {lora_weight}")
    
    def set_generation_params(self, **params):
        """
        Set generation parameters (compatibility method for transformers MusicGen)
        
        Note: Transformers MusicGen uses different parameter names than audiocraft.
        This method is kept for API compatibility but parameters are set in generate().
        """
        logger.info(f"Generation params noted: {params}")
        # Store params for use in generate()
        if not hasattr(self, '_gen_params'):
            self._gen_params = {}
        self._gen_params.update(params)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": "MusicGen",
            "model_path": self.model_path,
            "device": self.device,
            "sample_rate": self.sample_rate,
            "supports_lyrics": False,  # MusicGen doesn't separate lyrics
            "supports_lora": False,
            "cpu_compatible": True,
            "gpu_compatible": True
        }


class MusicGenModelManager:
    """Manager for different MusicGen model variants"""
    
    AVAILABLE_MODELS = {
        "small": "facebook/musicgen-small",
        "medium": "facebook/musicgen-medium", 
        "large": "facebook/musicgen-large",
        "melody": "facebook/musicgen-melody"  # Can condition on audio
    }
    
    @classmethod
    def get_recommended_model(cls, has_gpu: Optional[bool] = None, memory_gb: Optional[int] = None) -> str:
        """
        Get recommended MusicGen model based on hardware
        
        Args:
            has_gpu: Whether GPU is available
            memory_gb: Available memory in GB
            
        Returns:
            Recommended model name
        """
        if has_gpu is None:
            has_gpu = torch.cuda.is_available()
        
        if not has_gpu:
            # CPU mode - use smaller models
            return cls.AVAILABLE_MODELS["small"]
        
        # GPU mode - choose based on memory if available
        if memory_gb:
            if memory_gb >= 16:
                return cls.AVAILABLE_MODELS["large"]
            elif memory_gb >= 8:
                return cls.AVAILABLE_MODELS["medium"]
            else:
                return cls.AVAILABLE_MODELS["small"]
        
        # Default to medium for GPU
        return cls.AVAILABLE_MODELS["medium"]
    
    @classmethod
    def list_available_models(cls) -> Dict[str, str]:
        """List all available MusicGen models"""
        return cls.AVAILABLE_MODELS.copy()