"""
Test ACE-Step pipeline loading with actual model files
"""
import sys
sys.path.insert(0, 'src')

from utils.config_loader import load_config
from models.music_generator import MusicGenerator
from loguru import logger

print("=" * 70)
print("Testing ACE-Step Model Loading")
print("=" * 70)

# Load config
config = load_config('config/config.yaml')

# Initialize generator
print("\n1. Initializing MusicGenerator...")
generator = MusicGenerator(config)
print("   ✓ Initialized")

# Load models (this is where the error would occur)
print("\n2. Loading ACE-Step models...")
print("   (This will take 1-2 minutes on first run)")
try:
    generator.load_models()
    print("   ✓ Models loaded successfully!")
    print(f"   ✓ Pipeline ready: {generator.pipeline is not None}")
except Exception as e:
    print(f"   ✗ Error loading models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ACE-Step pipeline loaded successfully!")
print("=" * 70)
print("\nYou can now use LEMM to generate music.")
print("Run: python main.py")
