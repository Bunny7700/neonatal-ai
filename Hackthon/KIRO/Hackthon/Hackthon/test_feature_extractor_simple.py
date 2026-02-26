#!/usr/bin/env python
"""
Simple test script for FeatureExtractor class
Tests basic functionality without pytest framework
"""

import sys
import numpy as np

# Import the feature extractor
from feature_extractor import FeatureExtractor


def test_basic_functionality():
    """Test basic feature extraction functionality"""
    print("Testing FeatureExtractor basic functionality...")
    
    # Create extractor
    extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)
    print("✓ FeatureExtractor created successfully")
    
    # Generate test audio (1 second, 300 Hz sine wave - typical cry frequency)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * 300 * t)
    print("✓ Test audio generated (1 second, 300 Hz)")
    
    # Test individual feature extraction
    print("\nTesting individual feature extraction methods:")
    
    # Test pitch
    pitch = extractor.extract_pitch(audio)
    print(f"  Pitch: {pitch:.2f} Hz")
    assert 200 <= pitch <= 400, f"Pitch out of expected range: {pitch}"
    print("  ✓ Pitch extraction works")
    
    # Test intensity
    intensity = extractor.extract_intensity(audio)
    print(f"  Intensity: {intensity:.2f} dB")
    assert -100 <= intensity <= 0, f"Intensity out of range: {intensity}"
    print("  ✓ Intensity extraction works")
    
    # Test MFCCs
    mfccs = extractor.extract_mfccs(audio)
    print(f"  MFCCs shape: {mfccs.shape}")
    assert len(mfccs) == 13, f"Expected 13 MFCCs, got {len(mfccs)}"
    assert np.all(np.isfinite(mfccs)), "MFCCs contain invalid values"
    print("  ✓ MFCC extraction works")
    
    # Test duration
    duration_extracted = extractor.extract_duration(audio)
    print(f"  Duration: {duration_extracted:.3f} seconds")
    assert 0.99 <= duration_extracted <= 1.01, f"Duration incorrect: {duration_extracted}"
    print("  ✓ Duration extraction works")
    
    # Test frequency spectrum
    spectrum = extractor.extract_frequency_spectrum(audio)
    print(f"  Frequency spectrum shape: {spectrum.shape}")
    assert len(spectrum) > 0, "Frequency spectrum is empty"
    assert np.all(np.isfinite(spectrum)), "Spectrum contains invalid values"
    print("  ✓ Frequency spectrum extraction works")
    
    # Test complete feature extraction
    print("\nTesting complete feature extraction:")
    features = extractor.extract_all_features(audio)
    
    required_features = [
        'pitch', 'pitch_std', 'intensity', 'intensity_std',
        'mfccs', 'spectral_centroid', 'spectral_rolloff',
        'zero_crossing_rate', 'duration', 'frequency_spectrum'
    ]
    
    for feature_name in required_features:
        assert feature_name in features, f"Missing feature: {feature_name}"
        print(f"  ✓ {feature_name} present")
    
    # Verify all features are valid
    assert np.isfinite(features['pitch']), "Pitch is not finite"
    assert np.isfinite(features['intensity']), "Intensity is not finite"
    assert len(features['mfccs']) == 13, "MFCCs wrong length"
    assert np.all(np.isfinite(features['mfccs'])), "MFCCs contain invalid values"
    assert np.isfinite(features['duration']), "Duration is not finite"
    
    print("\n✓ All features extracted successfully!")
    print(f"\nFeature summary:")
    print(f"  - Pitch: {features['pitch']:.2f} Hz (std: {features['pitch_std']:.2f})")
    print(f"  - Intensity: {features['intensity']:.2f} dB (std: {features['intensity_std']:.2f})")
    print(f"  - MFCCs: {len(features['mfccs'])} coefficients")
    print(f"  - Spectral centroid: {features['spectral_centroid']:.2f} Hz")
    print(f"  - Spectral rolloff: {features['spectral_rolloff']:.2f} Hz")
    print(f"  - Zero-crossing rate: {features['zero_crossing_rate']:.4f}")
    print(f"  - Duration: {features['duration']:.3f} seconds")
    print(f"  - Frequency spectrum: {len(features['frequency_spectrum'])} bins")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*60)
    print("Testing edge cases...")
    
    extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)
    
    # Test empty audio
    print("\n1. Testing empty audio:")
    audio = np.array([])
    features = extractor.extract_all_features(audio)
    assert features['pitch'] == 0.0, "Empty audio should have 0 pitch"
    assert features['duration'] == 0.0, "Empty audio should have 0 duration"
    print("  ✓ Empty audio handled correctly")
    
    # Test silence
    print("\n2. Testing silence:")
    audio = np.zeros(16000)
    features = extractor.extract_all_features(audio)
    assert np.isfinite(features['pitch']), "Silence pitch should be finite"
    assert features['intensity'] < -50, "Silence should have low intensity"
    assert 0.99 <= features['duration'] <= 1.01, "Silence duration should be correct"
    print("  ✓ Silence handled correctly")
    
    # Test very short audio
    print("\n3. Testing very short audio (50ms):")
    audio = np.random.randn(800)  # 50ms at 16kHz
    features = extractor.extract_all_features(audio)
    assert 0.04 <= features['duration'] <= 0.06, "Short audio duration incorrect"
    assert len(features['mfccs']) == 13, "MFCCs wrong length for short audio"
    print("  ✓ Short audio handled correctly")
    
    # Test audio with NaN/Inf
    print("\n4. Testing audio with invalid values (NaN, Inf):")
    audio = np.array([0.1, 0.2, np.nan, 0.3, np.inf, 0.4, -np.inf] * 2000)
    features = extractor.extract_all_features(audio)
    assert np.isfinite(features['pitch']), "Pitch should be finite despite NaN/Inf"
    assert np.isfinite(features['intensity']), "Intensity should be finite despite NaN/Inf"
    assert np.all(np.isfinite(features['mfccs'])), "MFCCs should be finite despite NaN/Inf"
    print("  ✓ Invalid values handled correctly")
    
    # Test very loud audio
    print("\n5. Testing very loud audio (clipping):")
    audio = np.ones(16000)
    features = extractor.extract_all_features(audio)
    assert features['intensity'] > -10, "Loud audio should have high intensity"
    print("  ✓ Loud audio handled correctly")
    
    print("\n✓ All edge cases passed!")


def test_requirements_validation():
    """Validate that all requirements are met"""
    print("\n" + "="*60)
    print("Validating requirements...")
    
    extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)
    
    # Generate cry-like audio
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.3 * np.sin(2 * np.pi * 300 * t)  # Fundamental
    audio += 0.15 * np.sin(2 * np.pi * 600 * t)  # Harmonic
    
    features = extractor.extract_all_features(audio)
    
    print("\nRequirement 3.1 - Pitch extraction:")
    assert 'pitch' in features
    assert np.isfinite(features['pitch'])
    print(f"  ✓ Pitch computed: {features['pitch']:.2f} Hz")
    
    print("\nRequirement 3.2 - Frequency spectrum analysis:")
    assert 'frequency_spectrum' in features
    assert len(features['frequency_spectrum']) > 0
    print(f"  ✓ Frequency spectrum computed: {len(features['frequency_spectrum'])} bins")
    
    print("\nRequirement 3.3 - Intensity calculation:")
    assert 'intensity' in features
    assert np.isfinite(features['intensity'])
    print(f"  ✓ Intensity computed: {features['intensity']:.2f} dB")
    
    print("\nRequirement 3.4 - MFCC extraction (13 coefficients):")
    assert 'mfccs' in features
    assert len(features['mfccs']) == 13
    assert np.all(np.isfinite(features['mfccs']))
    print(f"  ✓ MFCCs computed: {len(features['mfccs'])} coefficients")
    
    print("\nRequirement 3.5 - Duration calculation:")
    assert 'duration' in features
    assert np.isfinite(features['duration'])
    print(f"  ✓ Duration computed: {features['duration']:.3f} seconds")
    
    print("\nRequirement 3.6 - Complete feature dictionary:")
    required_features = [
        'pitch', 'pitch_std', 'intensity', 'intensity_std',
        'mfccs', 'spectral_centroid', 'spectral_rolloff',
        'zero_crossing_rate', 'duration', 'frequency_spectrum'
    ]
    for feature_name in required_features:
        assert feature_name in features
    print(f"  ✓ All {len(required_features)} features present in dictionary")
    
    print("\n✓ All requirements validated!")


if __name__ == '__main__':
    try:
        print("="*60)
        print("FeatureExtractor Test Suite")
        print("="*60)
        
        test_basic_functionality()
        test_edge_cases()
        test_requirements_validation()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
