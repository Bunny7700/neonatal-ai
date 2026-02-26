#!/usr/bin/env python
"""
Simple test script for CryClassifier module.

Tests basic functionality without pytest to avoid numpy compatibility issues.
"""

import sys
import numpy as np
from cry_classifier import CryClassifier


def test_initialization():
    """Test that classifier initializes correctly."""
    print("Testing initialization...")
    classifier = CryClassifier()
    assert classifier is not None
    assert classifier.yamnet_model is not None
    assert classifier.CONFIDENCE_THRESHOLD == 60.0
    assert len(classifier.CRY_CATEGORIES) == 5
    print("✓ Initialization test passed")


def test_valid_cry_categories():
    """Test that all expected cry categories are defined."""
    print("Testing valid cry categories...")
    classifier = CryClassifier()
    expected_categories = [
        'hunger',
        'sleep_discomfort',
        'pain_distress',
        'diaper_change',
        'normal_unknown'
    ]
    assert set(classifier.CRY_CATEGORIES) == set(expected_categories)
    print("✓ Valid cry categories test passed")


def test_detect_cry_with_audio():
    """Test cry detection with valid audio."""
    print("Testing cry detection with audio...")
    classifier = CryClassifier()
    
    # Generate 1 second of audio at 16kHz with moderate energy
    duration = 1.0
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.1 * np.sin(2 * np.pi * 350 * t)
    
    is_crying, confidence = classifier.detect_cry(audio)
    
    assert isinstance(is_crying, bool)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 100.0
    print(f"✓ Cry detection test passed (is_crying={is_crying}, confidence={confidence:.2f})")


def test_detect_cry_empty_audio():
    """Test cry detection with empty audio."""
    print("Testing cry detection with empty audio...")
    classifier = CryClassifier()
    empty_audio = np.array([])
    is_crying, confidence = classifier.detect_cry(empty_audio)
    
    assert is_crying is False
    assert confidence == 0.0
    print("✓ Empty audio test passed")


def test_detect_cry_silent_audio():
    """Test cry detection with silent audio."""
    print("Testing cry detection with silent audio...")
    classifier = CryClassifier()
    silent_audio = np.zeros(16000)  # 1 second of silence
    is_crying, confidence = classifier.detect_cry(silent_audio)
    
    assert is_crying is False
    assert confidence < 50.0
    print(f"✓ Silent audio test passed (confidence={confidence:.2f})")


def test_classify_cry_type_returns_valid_category():
    """Test that classify_cry_type returns a valid category."""
    print("Testing classify_cry_type returns valid category...")
    classifier = CryClassifier()
    
    sample_features = {
        'pitch': 350.0,
        'pitch_std': 25.0,
        'intensity': -25.0,
        'intensity_std': 5.0,
        'zero_crossing_rate': 0.05,
        'duration': 1.0
    }
    
    cry_type, confidence = classifier.classify_cry_type(sample_features)
    
    assert cry_type in classifier.CRY_CATEGORIES
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 100.0
    print(f"✓ Classify cry type test passed (type={cry_type}, confidence={confidence:.2f})")


def test_classify_cry_type_pain_distress():
    """Test classification of pain/distress cry."""
    print("Testing pain/distress classification...")
    classifier = CryClassifier()
    
    # Features indicating pain: high pitch, high intensity, high variation
    pain_features = {
        'pitch': 450.0,
        'pitch_std': 60.0,
        'intensity': -15.0,
        'intensity_std': 10.0,
        'zero_crossing_rate': 0.05,
        'duration': 0.8
    }
    
    cry_type, confidence = classifier.classify_cry_type(pain_features)
    
    # Should classify as pain_distress with reasonable confidence
    assert cry_type == 'pain_distress'
    assert confidence >= 60.0
    print(f"✓ Pain/distress classification test passed (confidence={confidence:.2f})")


def test_classify_cry_type_hunger():
    """Test classification of hunger cry."""
    print("Testing hunger classification...")
    classifier = CryClassifier()
    
    # Features indicating hunger: moderate pitch, moderate intensity, rhythmic
    hunger_features = {
        'pitch': 350.0,
        'pitch_std': 20.0,
        'intensity': -25.0,
        'intensity_std': 5.0,
        'zero_crossing_rate': 0.05,
        'duration': 1.5
    }
    
    cry_type, confidence = classifier.classify_cry_type(hunger_features)
    
    # Should classify as hunger with reasonable confidence
    assert cry_type == 'hunger'
    assert confidence >= 60.0
    print(f"✓ Hunger classification test passed (confidence={confidence:.2f})")


def test_predict_no_crying():
    """Test predict method when no crying is detected."""
    print("Testing predict with no crying...")
    classifier = CryClassifier()
    
    silent_audio = np.zeros(16000)
    features = {'pitch': 0.0, 'intensity': -100.0, 'duration': 1.0}
    
    result = classifier.predict(silent_audio, features)
    
    assert result['is_crying'] is False
    assert result['cry_type'] == 'normal_unknown'
    assert result['confidence'] == 0.0
    assert 'detection_confidence' in result
    print("✓ Predict no crying test passed")


def test_predict_with_crying():
    """Test predict method when crying is detected."""
    print("Testing predict with crying...")
    classifier = CryClassifier()
    
    # Generate audio
    audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
    
    features = {
        'pitch': 350.0,
        'pitch_std': 25.0,
        'intensity': -25.0,
        'intensity_std': 5.0,
        'zero_crossing_rate': 0.05,
        'duration': 1.0
    }
    
    result = classifier.predict(audio, features)
    
    assert isinstance(result['is_crying'], bool)
    assert result['cry_type'] in classifier.CRY_CATEGORIES
    assert 0.0 <= result['confidence'] <= 100.0
    assert 'detection_confidence' in result
    print(f"✓ Predict with crying test passed (type={result['cry_type']}, confidence={result['confidence']:.2f})")


def test_confidence_threshold_boundaries():
    """Test confidence threshold at boundaries."""
    print("Testing confidence threshold boundaries...")
    classifier = CryClassifier()
    
    audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
    
    # Test 59.9% (below threshold)
    original_method = classifier.classify_cry_type
    classifier.classify_cry_type = lambda features: ('hunger', 59.9)
    result = classifier.predict(audio, {})
    assert result['cry_type'] == 'normal_unknown', "59.9% should be normal_unknown"
    print("  ✓ 59.9% threshold test passed")
    
    # Test 60.0% (at threshold)
    classifier.classify_cry_type = lambda features: ('hunger', 60.0)
    result = classifier.predict(audio, {})
    assert result['cry_type'] == 'hunger', "60.0% should be hunger"
    print("  ✓ 60.0% threshold test passed")
    
    # Test 60.1% (above threshold)
    classifier.classify_cry_type = lambda features: ('hunger', 60.1)
    result = classifier.predict(audio, {})
    assert result['cry_type'] == 'hunger', "60.1% should be hunger"
    print("  ✓ 60.1% threshold test passed")
    
    # Restore original method
    classifier.classify_cry_type = original_method
    print("✓ All confidence threshold boundary tests passed")


def test_validate_cry_type():
    """Test validate_cry_type method."""
    print("Testing validate_cry_type...")
    classifier = CryClassifier()
    
    # Test valid categories
    for category in classifier.CRY_CATEGORIES:
        assert classifier.validate_cry_type(category) is True
    
    # Test invalid categories
    invalid_categories = ['invalid', 'unknown', 'test', '']
    for category in invalid_categories:
        assert classifier.validate_cry_type(category) is False
    
    print("✓ Validate cry type test passed")


def test_predict_result_structure():
    """Test that predict returns all required fields."""
    print("Testing predict result structure...")
    classifier = CryClassifier()
    
    audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
    features = {'pitch': 350.0, 'intensity': -25.0, 'duration': 1.0}
    
    result = classifier.predict(audio, features)
    
    required_fields = ['is_crying', 'cry_type', 'confidence', 'detection_confidence']
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    print("✓ Predict result structure test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running CryClassifier Tests")
    print("=" * 60)
    
    tests = [
        test_initialization,
        test_valid_cry_categories,
        test_detect_cry_with_audio,
        test_detect_cry_empty_audio,
        test_detect_cry_silent_audio,
        test_classify_cry_type_returns_valid_category,
        test_classify_cry_type_pain_distress,
        test_classify_cry_type_hunger,
        test_predict_no_crying,
        test_predict_with_crying,
        test_confidence_threshold_boundaries,
        test_validate_cry_type,
        test_predict_result_structure,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
