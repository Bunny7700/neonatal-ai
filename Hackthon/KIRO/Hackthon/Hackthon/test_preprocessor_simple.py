#!/usr/bin/env python
"""
Simple test script for AudioPreprocessor without pytest
Tests basic functionality to verify the implementation works.
"""

import numpy as np
from audio_preprocessor import AudioPreprocessor

def test_basic_functionality():
    """Test basic AudioPreprocessor functionality"""
    print("Testing AudioPreprocessor...")
    
    # Initialize preprocessor
    preprocessor = AudioPreprocessor(sample_rate=16000)
    print("✓ Preprocessor initialized")
    
    # Test 1: Empty audio
    print("\nTest 1: Empty audio")
    empty = np.array([])
    result = preprocessor.preprocess(empty)
    assert len(result) == 0, "Empty audio test failed"
    print("✓ Empty audio handled correctly")
    
    # Test 2: Silence
    print("\nTest 2: Silence (all zeros)")
    silence = np.zeros(16000)
    result = preprocessor.preprocess(silence)
    assert len(result) > 0, "Silence test failed"
    assert np.all(np.abs(result) < 1e-5), "Silence should remain near zero"
    print("✓ Silence handled correctly")
    
    # Test 3: Normalization range
    print("\nTest 3: Normalization range")
    audio = np.random.randn(16000) * 5.0  # Large amplitude
    normalized = preprocessor.normalize_audio(audio)
    assert np.all(normalized >= -1.0), "Normalization min bound failed"
    assert np.all(normalized <= 1.0), "Normalization max bound failed"
    peak = np.max(np.abs(normalized))
    assert peak >= 0.95, f"Peak should be >= 0.95, got {peak}"
    print(f"✓ Normalization works correctly (peak: {peak:.3f})")
    
    # Test 4: Noise reduction
    print("\nTest 4: Noise reduction")
    t = np.linspace(0, 1, 16000)
    clean_signal = np.sin(2 * np.pi * 440 * t) * 0.5
    noise = np.random.randn(16000) * 0.1
    noisy_signal = clean_signal + noise
    cleaned = preprocessor.reduce_noise(noisy_signal)
    assert len(cleaned) == len(noisy_signal), "Noise reduction length mismatch"
    assert np.all(np.isfinite(cleaned)), "Noise reduction produced invalid values"
    print("✓ Noise reduction works correctly")
    
    # Test 5: Segmentation
    print("\nTest 5: Segmentation")
    signal1 = np.random.randn(8000) * 0.5
    silence_gap = np.zeros(3200)
    signal2 = np.random.randn(8000) * 0.5
    audio = np.concatenate([signal1, silence_gap, signal2])
    segments = preprocessor.segment_audio(audio, threshold=0.02)
    assert len(segments) >= 1, "Segmentation failed"
    print(f"✓ Segmentation works correctly (found {len(segments)} segments)")
    
    # Test 6: Full preprocessing pipeline
    print("\nTest 6: Full preprocessing pipeline")
    audio = np.random.randn(16000) * 0.5
    result = preprocessor.preprocess(audio)
    assert len(result) > 0, "Preprocessing failed"
    assert np.all(np.isfinite(result)), "Preprocessing produced invalid values"
    assert np.all(result >= -1.0) and np.all(result <= 1.0), "Preprocessing range check failed"
    print("✓ Full preprocessing pipeline works correctly")
    
    # Test 7: Handle NaN/Inf values
    print("\nTest 7: Handle invalid values (NaN/Inf)")
    audio = np.array([0.1, 0.2, np.nan, 0.4, np.inf, -np.inf, 0.5])
    result = preprocessor.reduce_noise(audio)
    assert np.all(np.isfinite(result)), "Failed to handle NaN/Inf values"
    print("✓ Invalid values handled correctly")
    
    # Test 8: Very short audio
    print("\nTest 8: Very short audio")
    short_audio = np.random.randn(800)  # 50ms
    result = preprocessor.preprocess(short_audio)
    assert len(result) > 0, "Short audio test failed"
    print("✓ Short audio handled correctly")
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
