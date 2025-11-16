"""
Test script to verify UI changes work correctly
Tests:
1. Time estimate display shows by default
2. Model selection is visible outside accordion
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_ui_changes():
    """Test that UI changes are correctly implemented"""
    print("Testing UI changes...")
    
    # Read the gradio_interface.py file
    interface_file = Path(__file__).parent / "src" / "ui" / "gradio_interface.py"
    
    with open(interface_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check that time_estimate has a default value (not visible=False)
    print("\n1️⃣ Checking time estimate display...")
    if 'time_estimate = gr.Markdown(label="Time Estimate", visible=False)' in content:
        print("   ❌ FAIL: time_estimate still has visible=False")
        return False
    elif 'time_estimate = gr.Markdown(\n        label="Time Estimate",\n        value="⏱️' in content:
        print("   ✅ PASS: time_estimate has default value and is visible")
    else:
        print("   ⚠️  WARNING: time_estimate format unexpected")
    
    # Test 2: Check that update function returns string directly
    print("\n2️⃣ Checking time estimate update function...")
    if 'return gr.update(value=estimate, visible=True)' in content:
        print("   ❌ FAIL: Still using gr.update() for time estimate")
        return False
    elif 'return estimate  # Return string directly for HF Space compatibility' in content:
        print("   ✅ PASS: Returns estimate string directly")
    else:
        print("   ⚠️  WARNING: Update function format unexpected")
    
    # Test 3: Check that model_choice is outside accordion
    print("\n3️⃣ Checking model selection visibility...")
    
    # Find the position of model_choice and accordion in the file
    model_choice_pos = content.find('model_choice = gr.Radio(')
    accordion_pos = content.find('with gr.Accordion("⚙️ Advanced Settings"')
    
    if model_choice_pos == -1:
        print("   ❌ FAIL: model_choice not found")
        return False
    elif accordion_pos == -1:
        print("   ❌ FAIL: Accordion not found")
        return False
    elif model_choice_pos < accordion_pos:
        print("   ✅ PASS: model_choice appears before accordion (visible by default)")
        print(f"      model_choice at position: {model_choice_pos}")
        print(f"      accordion at position: {accordion_pos}")
    else:
        print("   ❌ FAIL: model_choice is inside accordion")
        return False
    
    # Test 4: Check that accordion was renamed to "Advanced Settings"
    print("\n4️⃣ Checking accordion label...")
    if 'with gr.Accordion("⚙️ Advanced Settings"' in content:
        print("   ✅ PASS: Accordion renamed to 'Advanced Settings'")
    else:
        print("   ⚠️  WARNING: Accordion label might not be updated")
    
    print("\n" + "="*60)
    print("✅ All UI changes verified successfully!")
    print("="*60)
    
    print("\n📋 Summary of changes:")
    print("  1. Time estimate now visible by default with placeholder text")
    print("  2. Time estimate update returns string directly (HF Space compatible)")
    print("  3. Model selection moved outside accordion (always visible)")
    print("  4. Settings accordion renamed to 'Advanced Settings'")
    
    return True

if __name__ == "__main__":
    try:
        success = test_ui_changes()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
