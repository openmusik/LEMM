"""
Model Selector for LEMM - Automatic selection between ACE-Step and MusicGen
"""
from typing import Dict, Any, Optional, Tuple, Literal
import torch
import platform
import subprocess
from loguru import logger

ModelType = Literal["ace_step", "musicgen", "auto"]

class ModelSelector:
    """Automatically selects the best available music generation model"""
    
    def __init__(self):
        self.available_models = {}
        self.selected_model = None
        self.selection_reason = ""
        
    def detect_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect which music generation models are available
        
        Returns:
            Dictionary with model availability and capabilities
        """
        models = {}
        
        # Test ACE-Step availability
        models["ace_step"] = self._test_ace_step()
        
        # Test MusicGen availability  
        models["musicgen"] = self._test_musicgen()
        
        self.available_models = models
        logger.info(f"Model detection complete: {len([m for m in models.values() if m['available']])} models available")
        
        return models
    
    def _test_ace_step(self) -> Dict[str, Any]:
        """Test ACE-Step availability and compatibility"""
        result = {
            "available": False,
            "gpu_compatible": False,
            "cpu_compatible": False,
            "reason": "",
            "priority": 1  # High priority when GPU available
        }
        
        try:
            # Use global flag to avoid duplicate imports and check actual availability
            from src.models.music_generator import ACESTEP_AVAILABLE
            if not ACESTEP_AVAILABLE:
                raise ImportError("ACE-Step not available (global flag)")
            
            from acestep.pipeline_ace_step import ACEStepPipeline
            result["available"] = True
            logger.info("✅ ACE-Step import successful")
            
            # Test GPU compatibility
            if torch.cuda.is_available():
                result["gpu_compatible"] = True
                result["reason"] = "CUDA GPU available - ACE-Step optimal"
                logger.info("✅ ACE-Step GPU compatibility confirmed")
            else:
                # Check if AMD GPU (known ACE-Step limitation)
                if self._detect_amd_gpu():
                    result["reason"] = "AMD GPU detected - ACE-Step CPU issues expected (Error 13)"
                    logger.warning("⚠️ AMD GPU detected - ACE-Step may fail on CPU")
                else:
                    result["cpu_compatible"] = True
                    result["reason"] = "No GPU - ACE-Step CPU mode (slow but functional)"
                    logger.info("⚠️ ACE-Step CPU mode available but slow")
                    
        except ImportError as e:
            result["reason"] = f"ACE-Step not installed: {e}"
            logger.warning(f"❌ ACE-Step import failed: {e}")
        except Exception as e:
            result["reason"] = f"ACE-Step error: {e}"
            logger.error(f"❌ ACE-Step detection error: {e}")
        
        return result
    
    def _test_musicgen(self) -> Dict[str, Any]:
        """Test MusicGen availability and compatibility"""
        result = {
            "available": False,
            "gpu_compatible": False,
            "cpu_compatible": False,
            "reason": "",
            "priority": 2  # Lower priority than ACE-Step on GPU, higher on CPU
        }
        
        try:
            # Try importing MusicGen from transformers (no audiocraft needed!)
            from transformers import AutoProcessor, MusicgenForConditionalGeneration
            result["available"] = True
            logger.info("✅ MusicGen (transformers) import successful")
            
            # MusicGen works on both GPU and CPU
            if torch.cuda.is_available():
                result["gpu_compatible"] = True
                result["reason"] = "GPU available - MusicGen fast mode"
                logger.info("✅ MusicGen GPU compatibility confirmed")
            
            result["cpu_compatible"] = True
            result["reason"] = result["reason"] or "CPU mode - MusicGen works reliably"
            logger.info("✅ MusicGen CPU compatibility confirmed")
            
        except ImportError as e:
            result["reason"] = f"MusicGen not installed: {e}"
            logger.warning(f"❌ MusicGen import failed: {e}")
        except Exception as e:
            result["reason"] = f"MusicGen error: {e}"
            logger.error(f"❌ MusicGen detection error: {e}")
        
        return result
    
    def _detect_amd_gpu(self) -> bool:
        """Detect if AMD GPU is present"""
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    gpu_info = result.stdout
                    return "Radeon" in gpu_info or "AMD" in gpu_info
            except Exception:
                pass
        return False
    
    def select_best_model(self, user_preference: Optional[ModelType] = None) -> Tuple[Optional[ModelType], str]:
        """
        Select the best available model based on hardware and user preference
        
        Args:
            user_preference: User's preferred model type or "auto" for automatic selection
            
        Returns:
            Tuple of (selected_model, reason_for_selection)
        """
        if not self.available_models:
            self.detect_available_models()
        
        # Handle user preference
        if user_preference and user_preference != "auto":
            if user_preference in self.available_models:
                model_info = self.available_models[user_preference]
                if model_info["available"]:
                    if torch.cuda.is_available() and model_info["gpu_compatible"]:
                        reason = f"User selected {user_preference} - GPU mode"
                    elif model_info["cpu_compatible"]:
                        reason = f"User selected {user_preference} - CPU mode"
                    else:
                        reason = f"User selected {user_preference} but may have compatibility issues"
                    
                    self.selected_model = user_preference
                    self.selection_reason = reason
                    logger.info(f"🎯 Model selected by user: {user_preference} - {reason}")
                    return user_preference, reason
                else:
                    logger.warning(f"User requested {user_preference} but it's not available")
        
        # Automatic selection logic
        has_gpu = torch.cuda.is_available()
        is_amd = self._detect_amd_gpu()
        
        ace_step = self.available_models.get("ace_step", {})
        musicgen = self.available_models.get("musicgen", {})
        
        # Selection priority logic
        if has_gpu and not is_amd and ace_step.get("gpu_compatible"):
            # NVIDIA GPU available - prefer ACE-Step
            selected = "ace_step"
            reason = "NVIDIA GPU detected - ACE-Step optimal performance"
        elif is_amd and musicgen.get("cpu_compatible"):
            # AMD GPU system - prefer MusicGen (ACE-Step has Error 13 issues)
            selected = "musicgen"
            reason = "AMD GPU detected - MusicGen CPU mode (ACE-Step incompatible)"
        elif not has_gpu and musicgen.get("cpu_compatible"):
            # CPU only - prefer MusicGen for reliability
            selected = "musicgen"
            reason = "CPU only - MusicGen reliable CPU performance"
        elif ace_step.get("available"):
            # Fallback to ACE-Step if available
            selected = "ace_step"
            reason = "Fallback to ACE-Step (may be slow)"
        elif musicgen.get("available"):
            # Fallback to MusicGen
            selected = "musicgen"
            reason = "Fallback to MusicGen"
        else:
            # No models available
            selected = None
            reason = "No music generation models available"
            
        self.selected_model = selected
        self.selection_reason = reason
        
        if selected:
            logger.info(f"🤖 Auto-selected model: {selected} - {reason}")
        else:
            logger.error(f"❌ No models available: {reason}")
            
        return selected, reason
    
    def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        return self.available_models.get(model_type, {})
    
    def get_selection_summary(self) -> Dict[str, Any]:
        """Get summary of model selection process"""
        return {
            "available_models": self.available_models,
            "selected_model": self.selected_model,
            "selection_reason": self.selection_reason,
            "has_gpu": torch.cuda.is_available(),
            "is_amd": self._detect_amd_gpu()
        }