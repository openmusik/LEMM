#!/usr/bin/env python3
"""
Test file path handling in LEMM
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_paths():
    """Test that all file operations return valid file paths, not directories"""
    from pathlib import Path
    from src.utils.config_loader import load_config
    from src.utils.file_manager import FileManager
    import numpy as np
    
    print("🧪 Testing File Path Handling")
    print("=" * 50)
    
    # Load config
    config = load_config()
    file_manager = FileManager(config)
    
    # Create dummy audio
    sample_rate = 44100
    duration = 1  # 1 second
    dummy_audio = np.random.randn(sample_rate * duration).astype(np.float32)
    
    # Test save_output
    print("\n1. Testing save_output...")
    output_path = file_manager.save_output(dummy_audio)
    print(f"   Returned path: {output_path}")
    
    # Validate path
    path_obj = Path(output_path)
    print(f"   Is file: {path_obj.is_file()}")
    print(f"   Is directory: {path_obj.is_dir()}")
    print(f"   Exists: {path_obj.exists()}")
    print(f"   Parent directory: {path_obj.parent}")
    
    if not path_obj.is_file():
        print(f"   ❌ ERROR: Returned path is not a file!")
        return False
    
    if path_obj.is_dir():
        print(f"   ❌ ERROR: Returned path is a directory!")
        return False
        
    print(f"   ✅ File path is valid")
    
    # Test that Gradio can read it
    print("\n2. Testing Gradio compatibility...")
    try:
        with open(output_path, "rb") as f:
            data = f.read(100)  # Read first 100 bytes
        print(f"   ✅ File is readable (read {len(data)} bytes)")
    except PermissionError as e:
        print(f"   ❌ Permission error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False
    
    # Clean up
    try:
        path_obj.unlink()
        print(f"   ✅ Test file cleaned up")
    except Exception as e:
        print(f"   ⚠️ Could not delete test file: {e}")
    
    print("\n✅ All file path tests passed!")
    return True

if __name__ == "__main__":
    success = test_file_paths()
    sys.exit(0 if success else 1)
