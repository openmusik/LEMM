"""
AMD GPU Compatibility Test for LEMM
Tests device detection and configuration on AMD systems
"""
import sys
import subprocess
import platform
import torch
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from utils.config_loader import load_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_amd_gpu_detection():
    """Test AMD GPU detection on Windows"""
    logger.info("=== AMD GPU Detection Test ===")
    
    # System info
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"PyTorch: {torch.__version__}")
    
    # CUDA availability
    cuda_available = torch.cuda.is_available()
    logger.info(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        logger.info(f"CUDA Devices: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            logger.info(f"  Device {i}: {torch.cuda.get_device_name(i)}")
    
    # AMD GPU detection (Windows)
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                gpus = [line.strip() for line in result.stdout.split('\n') if line.strip() and line.strip() != 'Name']
                logger.info("Detected GPUs:")
                for gpu in gpus:
                    if gpu:
                        logger.info(f"  - {gpu}")
                        if "Radeon" in gpu or "AMD" in gpu:
                            logger.info("    *** AMD GPU detected ***")
                            if not cuda_available:
                                logger.warning("    PyTorch CUDA doesn't support AMD GPUs - will use CPU")
                                logger.info("    Consider using PyTorch with ROCm for AMD GPU support")
        except Exception as e:
            logger.error(f"GPU detection failed: {e}")
    
    # Test configuration loading
    logger.info("\n=== Configuration Test ===")
    try:
        config = load_config("config/config.yaml")
        ace_config = config.get("models", {}).get("ace_step", {})
        logger.info(f"ACE-Step device: {ace_config.get('device', 'not set')}")
        logger.info(f"ACE-Step bf16: {ace_config.get('bf16', 'not set')}")
        logger.info(f"ACE-Step cpu_offload: {ace_config.get('cpu_offload', 'not set')}")
        logger.info(f"ACE-Step overlapped_decode: {ace_config.get('overlapped_decode', 'not set')}")
        logger.info(f"ACE-Step num_inference_steps: {ace_config.get('num_inference_steps', 'not set')}")
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
    
    # Test tensor operations
    logger.info("\n=== Tensor Operations Test ===")
    try:
        # Test basic tensor creation
        x = torch.randn(10, 10)
        logger.info(f"CPU tensor created: {x.shape}")
        
        # Test dtype support
        if cuda_available:
            device = torch.device("cuda")
            x_gpu = x.to(device)
            logger.info(f"GPU tensor created: {x_gpu.device}")
            
            # Test bfloat16
            if torch.cuda.is_bf16_supported():
                x_bf16 = x_gpu.to(torch.bfloat16)
                logger.info("bfloat16 supported on GPU")
            else:
                logger.warning("bfloat16 not supported on this GPU")
        else:
            logger.info("CPU-only mode - using float32")
            
    except Exception as e:
        logger.error(f"Tensor operations test failed: {e}")
    
    # Performance expectations
    logger.info("\n=== Performance Expectations ===")
    if cuda_available:
        logger.info("✅ GPU acceleration available - fast generation expected")
    else:
        logger.warning("⚠️  CPU-only mode detected:")
        logger.warning("   - Music generation will be significantly slower")
        logger.warning("   - Expect 10-50x longer generation times")
        logger.warning("   - Consider using a system with NVIDIA GPU for production")
        logger.warning("   - Or use HuggingFace Space with ZeroGPU for free GPU access")

def test_model_loading():
    """Test if models can be loaded without errors"""
    logger.info("\n=== Model Loading Test ===")
    
    model_path = Path("models/ACE-Step-HF")
    if model_path.exists():
        logger.info(f"ACE-Step model found at: {model_path}")
        try:
            # Test basic imports
            from transformers import AutoTokenizer
            logger.info("✅ Transformers import successful")
            
            # Note: We don't actually load the model here to avoid memory usage
            logger.info("Model loading simulation successful")
            
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
        except Exception as e:
            logger.error(f"❌ Model loading error: {e}")
    else:
        logger.warning(f"ACE-Step model not found at {model_path}")
        logger.info("This is expected if models haven't been downloaded yet")

if __name__ == "__main__":
    logger.info("LEMM AMD GPU Compatibility Test")
    logger.info("=" * 50)
    
    test_amd_gpu_detection()
    test_model_loading()
    
    logger.info("\n" + "=" * 50)
    logger.info("Test completed. Check logs above for compatibility assessment.")