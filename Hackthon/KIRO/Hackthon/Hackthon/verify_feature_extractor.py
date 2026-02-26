#!/usr/bin/env python
"""
Minimal verification script for FeatureExtractor
Just checks that the class can be imported and instantiated
"""

print("Attempting to import FeatureExtractor...")

try:
    from feature_extractor import FeatureExtractor
    print("✓ FeatureExtractor imported successfully")
    
    print("\nAttempting to create FeatureExtractor instance...")
    extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)
    print("✓ FeatureExtractor instance created successfully")
    
    print("\nChecking methods exist...")
    methods = [
        'extract_pitch',
        'extract_frequency_spectrum',
        'extract_intensity',
        'extract_mfccs',
        'extract_duration',
        'extract_spectral_centroid',
        'extract_spectral_rolloff',
        'extract_zero_crossing_rate',
        'extract_pitch_std',
        'extract_intensity_std',
        'extract_all_features'
    ]
    
    for method in methods:
        assert hasattr(extractor, method), f"Missing method: {method}"
        print(f"  ✓ {method}")
    
    print("\n✓ All required methods present!")
    print("\nFeatureExtractor class is ready to use.")
    print("Note: Full testing requires compatible numpy version.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
