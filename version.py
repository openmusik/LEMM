"""
Display LEMM version and system information
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.__version__ import __version__, __version_info__
import torch

print("=" * 70)
print("LEMM - Let Everyone Make Music")
print("=" * 70)
print(f"\nVersion: {__version__}")
print(f"Version Info: {__version_info__}")
print(f"\nPython: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    try:
        import torch.version
        if hasattr(torch.version, 'cuda'):
            print(f"CUDA Version: {torch.version.cuda}")
        else:
            print("CUDA Version: Not available")
    except (AttributeError, ImportError):
        print("CUDA Version: Not available")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

print("\n" + "=" * 70)
print("Ready to create music!")
print("=" * 70)
