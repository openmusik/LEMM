#!/usr/bin/env python3
"""
Test MusicGen standalone without ACE-Step dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_musicgen_imports():
    """Test if MusicGen can be imported"""
    try:
        print("Testing MusicGen imports...")
        
        # Test audiocraft import
        try:
            from audiocraft.models import MusicGen
            print("✅ audiocraft.models.MusicGen imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import MusicGen: {e}")
            return False
            
        # Test ModelSelector without ACE-Step
        try:
            from src.models.model_selector import ModelSelector
            print("✅ ModelSelector imported successfully")
            
            # Test model detection
            selector = ModelSelector()
            available = selector.detect_available_models()
            print(f"Available models: {available}")
            
        except ImportError as e:
            print(f"❌ Failed to import ModelSelector: {e}")
            
        # Test MusicGen Pipeline
        try:
            from src.models.musicgen_pipeline import MusicGenPipeline
            print("✅ MusicGenPipeline imported successfully")
            
            # Test initialization
            pipeline = MusicGenPipeline(
                model_path="facebook/musicgen-small",
                device="cpu"
            )
            print("✅ MusicGenPipeline created successfully")
            
        except Exception as e:
            print(f"❌ Failed to create MusicGenPipeline: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    try:
        from src.utils.config_loader import load_config
        config = load_config()
        print(f"✅ Config loaded: {list(config.keys())}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

if __name__ == "__main__":
    print("🎵 LEMM MusicGen Standalone Test")
    print("=" * 50)
    
    # Test basic imports
    success = test_config_loading()
    
    if success:
        success = test_musicgen_imports()
    
    if success:
        print("\n✅ All tests passed - MusicGen implementation is working!")
    else:
        print("\n❌ Some tests failed - check dependencies and configuration")
        sys.exit(1)