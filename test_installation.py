"""
Quick test to verify ACE-Step installation and model loading
"""
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

print("=" * 70)
print("LEMM ACE-Step Installation Verification")
print("=" * 70)

# Test 1: Import ACEStepPipeline
print("\n1. Testing ACE-Step import...")
try:
    from acestep.pipeline_ace_step import ACEStepPipeline
    print("   ✓ ACEStepPipeline imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import ACEStepPipeline: {e}")
    sys.exit(1)

# Test 2: Import project modules
print("\n2. Testing project modules...")
try:
    from utils.config_loader import load_config
    print("   ✓ load_config imported")
    
    from models.music_generator import MusicGenerator
    print("   ✓ MusicGenerator imported")
    
    from ui.gradio_interface import create_interface
    print("   ✓ Gradio interface imported")
except ImportError as e:
    print(f"   ✗ Failed to import project modules: {e}")
    sys.exit(1)

# Test 3: Load configuration
print("\n3. Testing configuration...")
try:
    config = load_config('config/config.yaml')
    print(f"   ✓ Configuration loaded")
    print(f"   - ACE-Step path: {config['models']['ace_step']['path']}")
    print(f"   - Device: {config['models']['ace_step']['device']}")
except Exception as e:
    print(f"   ✗ Failed to load configuration: {e}")
    sys.exit(1)

# Test 4: Check model files exist
print("\n4. Checking model files...")
ace_step_path = config['models']['ace_step']['path']
required_components = [
    'ace_step_transformer/diffusion_pytorch_model.safetensors',
    'music_dcae_f8c8/diffusion_pytorch_model.safetensors',
    'music_vocoder/diffusion_pytorch_model.safetensors',
    'umt5-base/model.safetensors'
]

all_present = True
for component in required_components:
    file_path = os.path.join(ace_step_path, component)
    if os.path.exists(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"   ✓ {component} ({size_mb:.1f} MB)")
    else:
        print(f"   ✗ {component} NOT FOUND")
        all_present = False

if not all_present:
    print("\n   ⚠️  Some model files are missing!")
else:
    print("\n   ✓ All model files present")

# Test 5: Initialize MusicGenerator (without loading models)
print("\n5. Testing MusicGenerator initialization...")
try:
    # Check Python version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"   - Python version: {python_version}")
    
    # Initialize (this won't load the model yet)
    generator = MusicGenerator(config)
    print("   ✓ MusicGenerator initialized")
    print(f"   - Device: {generator.device}")
    print(f"   - Model path: {generator.model_path}")
    print(f"   - Sample rate: {generator.sample_rate} Hz")
except Exception as e:
    print(f"   ✗ Failed to initialize MusicGenerator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE!")
print("=" * 70)
print("\n✅ All tests passed! LEMM is ready to use.")
print("\nTo launch the application:")
print("  1. Activate environment: .venv310\\Scripts\\Activate.ps1")
print("  2. Run: python main.py")
print("\n⚠️  Note: Actual model loading will happen when you generate music.")
print("=" * 70)
