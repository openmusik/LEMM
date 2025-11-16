#!/usr/bin/env python3
"""
Minimal LEMM test without audiocraft dependencies - test our dual-model architecture
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_minimal_lemm():
    """Test LEMM without audiocraft dependencies"""
    try:
        print("🎵 Testing LEMM Dual-Model Architecture")
        print("=" * 50)
        
        # Test configuration loading
        print("1. Testing configuration...")
        from src.utils.config_loader import load_config
        config = load_config()
        print(f"✅ Config loaded: {list(config.keys())}")
        
        # Test ModelSelector (should work even without audiocraft)
        print("\n2. Testing ModelSelector...")
        from src.models.model_selector import ModelSelector
        selector = ModelSelector() 
        available = selector.detect_available_models()
        print(f"✅ Model detection: {available}")
        
        # Test model selection logic
        selected, reason = selector.select_best_model("auto")
        print(f"✅ Auto-selection: {selected} - {reason}")
        
        # Test UI components (without launching)
        print("\n3. Testing UI components...")
        from src.ui.gradio_interface import LEMMInterface
        lemm = LEMMInterface(config)
        system_status = lemm.get_system_status()
        print(f"✅ System Status:\n{system_status}")
        
        # Test prompt analyzer
        print("\n4. Testing prompt analysis...")
        test_prompt = "An upbeat electronic dance song with synthesizers"
        analysis_result = lemm.analyze_prompt(test_prompt)
        print(f"✅ Analysis result: {analysis_result[:100]}...")
        
        print("\n✅ All core components working!")
        print("\nNext steps:")
        print("- Install audiocraft on a system with proper FFmpeg support")
        print("- Or deploy to HuggingFace Spaces with GPU support")
        print("- The dual-model architecture is ready for MusicGen integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_lemm()
    sys.exit(0 if success else 1)