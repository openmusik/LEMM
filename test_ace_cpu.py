"""
CPU ACE-Step Test - Check if it works without CUDA
"""
import torch
import sys
from pathlib import Path

def test_ace_step_cpu():
    print("=== Testing ACE-Step on CPU ===")
    
    # Import ACE-Step
    try:
        from acestep.pipeline_ace_step import ACEStepPipeline
        print("✅ ACEStepPipeline imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Check model path
    model_path = Path("models/ACE-Step-HF")
    if not model_path.exists():
        print(f"❌ Model path not found: {model_path}")
        return False
    
    print(f"✅ Model path exists: {model_path}")
    
    try:
        # Try to create pipeline with CPU
        print("Creating ACE-Step pipeline on CPU...")
        pipeline = ACEStepPipeline(
            model_path=str(model_path),
            device="cpu",
            torch_dtype=torch.float32,
            bf16=False,
            cpu_offload=False,
            overlapped_decode=False
        )
        print("✅ ACE-Step pipeline created successfully on CPU")
        
        # Try a simple generation test (very short)
        print("Testing music generation...")
        try:
            # Use the correct ACE-Step API call method
            audio = pipeline(
                prompt="A simple melody",
                audio_duration=4,  # Very short for testing
                guidance_scale=7.5,
                infer_step=10  # Very few steps for testing
            )
            print(f"✅ Generation successful! Audio type: {type(audio)}")
            return True
        except PermissionError as e:
            print(f"❌ PERMISSION ERROR during generation: {e}")
            print("This is likely the Error 13 you encountered")
            return False
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Pipeline creation failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ace_step_cpu()
    
    if success:
        print("\n🎉 ACE-Step works on CPU!")
    else:
        print("\n❌ ACE-Step has issues on CPU")
        print("This confirms that CPU generation may not work properly")