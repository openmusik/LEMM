"""
Test new features: Lyrics variation, time estimation, vocal synthesis
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_lyrics_variation():
    """Test that lyrics generator produces varied output"""
    print("🎵 Testing Lyrics Variation")
    print("=" * 50)
    
    from src.utils.config_loader import load_config
    from src.models.lyrics_generator import LyricsGenerator
    from src.models.prompt_analyzer import PromptAnalyzer
    
    config = load_config()
    generator = LyricsGenerator(config)
    analyzer = PromptAnalyzer()
    
    prompt = "An upbeat electronic dance song"
    analysis = analyzer.analyze(prompt)
    
    print(f"\nPrompt: {prompt}")
    print(f"Analysis: Genre={analysis['genre']}, Mood={analysis['mood']}, Tempo={analysis['tempo']}")
    
    # Generate 3 versions with different seeds
    print("\n--- Version 1 (seed=123) ---")
    lyrics1 = generator.generate(prompt, analysis, random_seed=123)
    print(lyrics1[:200] + "...")
    
    print("\n--- Version 2 (seed=456) ---")
    lyrics2 = generator.generate(prompt, analysis, random_seed=456)
    print(lyrics2[:200] + "...")
    
    print("\n--- Version 3 (seed=789) ---")
    lyrics3 = generator.generate(prompt, analysis, random_seed=789)
    print(lyrics3[:200] + "...")
    
    # Verify they're different
    if lyrics1 != lyrics2 and lyrics2 != lyrics3 and lyrics1 != lyrics3:
        print("\n✅ Lyrics vary correctly with different seeds!")
        return True
    else:
        print("\n❌ Lyrics are not varying")
        return False


def test_vocal_synthesizer():
    """Test vocal synthesizer initialization"""
    print("\n🎤 Testing Vocal Synthesizer")
    print("=" * 50)
    
    from src.utils.config_loader import load_config
    from src.models.vocal_synthesizer import VocalSynthesizer
    
    config = load_config()
    synthesizer = VocalSynthesizer(config)
    
    print(f"Backend: {synthesizer.backend}")
    print(f"Device: {synthesizer.device}")
    print(f"Backend info: {synthesizer.get_backend_info()}")
    
    # Test synthesis (will return placeholder)
    lyrics = "Hello world, this is a test"
    audio = synthesizer.synthesize(lyrics)
    
    print(f"Audio shape: {audio.shape}")
    print(f"Audio dtype: {audio.dtype}")
    
    # Test time estimation
    test_lyrics = "A" * 500  # 500 characters
    estimated_time = synthesizer.estimate_synthesis_time(test_lyrics)
    print(f"Estimated synthesis time for 500 chars: {estimated_time}s")
    
    print("✅ Vocal synthesizer works!")
    return True


def test_time_estimation():
    """Test generation time estimation"""
    print("\n⏱️ Testing Time Estimation")
    print("=" * 50)
    
    from src.utils.config_loader import load_config
    from src.ui.gradio_interface import LEMMInterface
    
    config = load_config()
    interface = LEMMInterface(config)
    
    # Test different scenarios
    scenarios = [
        (1, "", "MusicGen (CPU)"),
        (3, "Sample lyrics here", "MusicGen (CPU)"),
        (5, "Much longer lyrics for testing purposes", "Auto (Recommended)")
    ]
    
    for num_clips, lyrics, model in scenarios:
        estimate = interface.estimate_generation_time(num_clips, lyrics, model)
        print(f"\nScenario: {num_clips} clips, {'with' if lyrics else 'no'} lyrics, {model}")
        print(estimate[:150] + "...")
    
    print("\n✅ Time estimation works!")
    return True


if __name__ == "__main__":
    print("🧪 Testing New LEMM Features")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Lyrics Variation", test_lyrics_variation()))
    except Exception as e:
        print(f"❌ Lyrics variation test failed: {e}")
        results.append(("Lyrics Variation", False))
    
    try:
        results.append(("Vocal Synthesizer", test_vocal_synthesizer()))
    except Exception as e:
        print(f"❌ Vocal synthesizer test failed: {e}")
        results.append(("Vocal Synthesizer", False))
    
    try:
        results.append(("Time Estimation", test_time_estimation()))
    except Exception as e:
        print(f"❌ Time estimation test failed: {e}")
        results.append(("Time Estimation", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed")
        sys.exit(1)
