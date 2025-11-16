"""
CPU Permission Error Test for LEMM
Tests the specific permission denied error during music generation
"""
import sys
import os
import traceback
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_cpu_generation():
    """Test CPU generation to identify permission errors"""
    print("=== CPU Generation Permission Test ===")
    
    try:
        # Test basic imports first
        print("Testing imports...")
        import torch
        print(f"✅ PyTorch {torch.__version__} imported")
        
        # Test ACE-Step import
        try:
            from acestep.pipeline_ace_step import ACEStepPipeline
            print("✅ ACE-Step pipeline imported")
        except ImportError as e:
            print(f"❌ ACE-Step import failed: {e}")
            # Try alternative import
            try:
                import acestep
                print("✅ ACE-Step module imported (checking contents...)")
                print(f"ACE-Step contents: {dir(acestep)}")
            except ImportError as e2:
                print(f"❌ ACE-Step module import also failed: {e2}")
                return False
        
        # Test model path access
        model_path = Path("models/ACE-Step-HF")
        print(f"\nTesting model path access: {model_path}")
        
        if model_path.exists():
            print("✅ Model directory exists")
            
            # Check permissions
            if os.access(model_path, os.R_OK):
                print("✅ Model directory readable")
            else:
                print("❌ Model directory not readable - PERMISSION ISSUE")
                
            if os.access(model_path, os.W_OK):
                print("✅ Model directory writable")
            else:
                print("⚠️ Model directory not writable")
                
            # Check individual files
            config_file = model_path / "config.json"
            if config_file.exists():
                if os.access(config_file, os.R_OK):
                    print("✅ config.json readable")
                else:
                    print("❌ config.json not readable - PERMISSION ISSUE")
            else:
                print("❌ config.json not found")
        else:
            print("❌ Model directory does not exist")
            
        # Test output directory
        output_path = Path("output")
        print(f"\nTesting output directory: {output_path}")
        
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                print("✅ Output directory created")
            except PermissionError as e:
                print(f"❌ Cannot create output directory: {e}")
                return False
        
        if os.access(output_path, os.W_OK):
            print("✅ Output directory writable")
        else:
            print("❌ Output directory not writable - PERMISSION ISSUE")
            
        # Test creating a test file
        test_file = output_path / "test_permissions.txt"
        try:
            with open(test_file, 'w') as f:
                f.write("permission test")
            print("✅ Can create files in output directory")
            test_file.unlink()  # Clean up
        except PermissionError as e:
            print(f"❌ Cannot create files in output directory: {e}")
            return False
            
        print("\n=== Attempting minimal ACE-Step initialization ===")
        
        try:
            # Try to initialize ACE-Step without GPU
            import acestep
            print(f"ACE-Step version: {getattr(acestep, '__version__', 'unknown')}")
            
            # Check if we can create a pipeline
            if hasattr(acestep, 'ACEStepPipeline'):
                print("ACEStepPipeline class found")
                
                # Try minimal initialization
                from acestep.pipeline_ace_step import ACEStepPipeline
                pipeline = ACEStepPipeline(
                    model_path=str(model_path),
                    device="cpu",
                    torch_dtype=torch.float32
                )
                print("✅ ACE-Step pipeline created successfully on CPU")
                return True
                
            else:
                print("❌ ACEStepPipeline class not found in acestep module")
                print(f"Available classes: {[attr for attr in dir(acestep) if not attr.startswith('_')]}")
                
        except PermissionError as e:
            print(f"❌ PERMISSION ERROR during ACE-Step initialization: {e}")
            print("This suggests the model files or directories have restricted access")
            return False
        except Exception as e:
            print(f"❌ OTHER ERROR during ACE-Step initialization: {e}")
            print(f"Error type: {type(e).__name__}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cpu_generation()
    
    if success:
        print("\n🎉 CPU generation should work - no permission issues found")
    else:
        print("\n⚠️ Permission or compatibility issues detected")
        print("\nPossible solutions:")
        print("1. Run as administrator")
        print("2. Check file/folder permissions")
        print("3. Use a different model path")
        print("4. Install CPU-compatible version of ACE-Step")