#!/usr/bin/env python3
"""
Privacy Safeguards Test Suite

Tests to verify privacy requirements are met:
- Requirement 8.1: No raw audio transmitted over network
- Requirement 8.2: Raw audio cleared from memory after processing

This test suite validates:
1. Raw audio is disposed after processing
2. No raw audio in feature vectors
3. No raw audio in feedback storage
4. No raw audio in API responses
5. Privacy logging is working correctly
"""

import numpy as np
import json
import os
import sys
import time
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cry_detection_yamnet import CryDetector
from privacy_logger import verify_no_raw_audio_in_dict, get_privacy_logger


def test_audio_disposal():
    """
    Test that raw audio is disposed after processing.
    
    Validates: Requirement 8.2
    """
    print("\n" + "="*60)
    print("TEST 1: Audio Disposal After Processing")
    print("="*60)
    
    detector = CryDetector()
    
    # Run detection
    print("Running detection...")
    result = detector.detect()
    
    # Check that result doesn't contain raw audio
    print("Checking result for raw audio...")
    has_no_audio = verify_no_raw_audio_in_dict(result)
    
    if has_no_audio:
        print("✅ PASS: No raw audio found in detection result")
    else:
        print("❌ FAIL: Raw audio detected in detection result")
        return False
    
    # Check privacy statistics
    stats = detector.get_privacy_statistics()
    print(f"\nPrivacy Statistics:")
    print(f"  Audio captured: {stats['audio_captured']}")
    print(f"  Audio disposed: {stats['audio_disposed']}")
    print(f"  Disposal rate: {stats['disposal_rate']:.1f}%")
    
    if stats['disposal_rate'] == 100.0:
        print("✅ PASS: 100% disposal rate achieved")
    else:
        print(f"❌ FAIL: Disposal rate is {stats['disposal_rate']:.1f}%, expected 100%")
        return False
    
    return True


def test_features_no_raw_audio():
    """
    Test that extracted features don't contain raw audio.
    
    Validates: Requirement 8.2
    """
    print("\n" + "="*60)
    print("TEST 2: Features Don't Contain Raw Audio")
    print("="*60)
    
    detector = CryDetector()
    
    # Run detection
    print("Running detection...")
    result = detector.detect()
    
    # Check features specifically
    if 'features' in result:
        features = result['features']
        print(f"Checking {len(features)} features...")
        
        has_no_audio = verify_no_raw_audio_in_dict(features)
        
        if has_no_audio:
            print("✅ PASS: No raw audio in feature vector")
            print(f"  Features present: {', '.join(features.keys())}")
        else:
            print("❌ FAIL: Raw audio detected in feature vector")
            return False
    else:
        print("⚠️  WARNING: No features in result")
    
    return True


def test_feedback_storage_no_raw_audio():
    """
    Test that feedback storage doesn't contain raw audio.
    
    Validates: Requirement 8.3
    """
    print("\n" + "="*60)
    print("TEST 3: Feedback Storage Without Raw Audio")
    print("="*60)
    
    detector = CryDetector()
    
    # Run detection to get features
    print("Running detection...")
    result = detector.detect()
    
    # Submit feedback
    print("Submitting feedback...")
    features = result.get('features', {})
    success = detector.submit_feedback(
        predicted_type='hunger',
        actual_type='pain_distress',
        features=features,
        confidence=75.0
    )
    
    if not success:
        print("❌ FAIL: Feedback submission failed")
        return False
    
    print("✅ Feedback submitted successfully")
    
    # Check feedback files
    feedback_dir = "./feedback_data"
    if os.path.exists(feedback_dir):
        print(f"Checking feedback files in {feedback_dir}...")
        
        feedback_files = [f for f in os.listdir(feedback_dir) if f.endswith('.json')]
        if feedback_files:
            # Check the most recent file
            latest_file = max(
                [os.path.join(feedback_dir, f) for f in feedback_files],
                key=os.path.getctime
            )
            
            print(f"Checking file: {os.path.basename(latest_file)}")
            with open(latest_file, 'r') as f:
                feedback_data = json.load(f)
            
            # Verify no raw audio
            has_no_audio = verify_no_raw_audio_in_dict(feedback_data)
            
            if has_no_audio:
                print("✅ PASS: No raw audio in stored feedback")
                print(f"  Stored fields: {', '.join(feedback_data.keys())}")
            else:
                print("❌ FAIL: Raw audio detected in stored feedback")
                return False
        else:
            print("⚠️  WARNING: No feedback files found")
    else:
        print("⚠️  WARNING: Feedback directory doesn't exist")
    
    return True


def test_network_transmission_safety():
    """
    Test that API responses don't contain raw audio.
    
    Validates: Requirement 8.1
    """
    print("\n" + "="*60)
    print("TEST 4: Network Transmission Safety")
    print("="*60)
    
    detector = CryDetector()
    
    # Simulate API response
    print("Simulating API response...")
    result = detector.detect()
    
    # Convert to JSON (as would happen in API)
    try:
        json_str = json.dumps(result, default=str)
        print(f"JSON response size: {len(json_str)} bytes")
        
        # Parse back
        api_response = json.loads(json_str)
        
        # Check for raw audio
        has_no_audio = verify_no_raw_audio_in_dict(api_response)
        
        if has_no_audio:
            print("✅ PASS: No raw audio in API response")
        else:
            print("❌ FAIL: Raw audio detected in API response")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error serializing result: {e}")
        return False
    
    # Log network check
    privacy_logger = get_privacy_logger()
    privacy_logger.log_network_check("/api/dashboard", has_audio=False)
    
    return True


def test_privacy_logging():
    """
    Test that privacy logging is working correctly.
    
    Validates: Requirement 8.1, 8.2
    """
    print("\n" + "="*60)
    print("TEST 5: Privacy Logging Functionality")
    print("="*60)
    
    detector = CryDetector()
    
    # Run multiple detections
    print("Running 3 detections...")
    for i in range(3):
        result = detector.detect()
        time.sleep(0.1)
    
    # Get statistics
    stats = detector.get_privacy_statistics()
    
    print("\nPrivacy Statistics:")
    print(f"  Audio captured: {stats['audio_captured']}")
    print(f"  Audio disposed: {stats['audio_disposed']}")
    print(f"  Features extracted: {stats['features_extracted']}")
    print(f"  Privacy violations: {stats['privacy_violations']}")
    print(f"  Disposal rate: {stats['disposal_rate']:.1f}%")
    print(f"  Violation rate: {stats['violation_rate']:.1f}%")
    
    # Verify statistics
    if stats['audio_captured'] >= 3:
        print("✅ PASS: Audio capture logged correctly")
    else:
        print(f"❌ FAIL: Expected >= 3 captures, got {stats['audio_captured']}")
        return False
    
    if stats['disposal_rate'] == 100.0:
        print("✅ PASS: 100% disposal rate")
    else:
        print(f"❌ FAIL: Disposal rate is {stats['disposal_rate']:.1f}%")
        return False
    
    if stats['privacy_violations'] == 0:
        print("✅ PASS: No privacy violations detected")
    else:
        print(f"❌ FAIL: {stats['privacy_violations']} privacy violations detected")
        return False
    
    # Print full summary
    print("\nFull Privacy Summary:")
    detector.print_privacy_summary()
    
    return True


def test_privacy_violation_detection():
    """
    Test that privacy violations are detected correctly.
    
    Validates: Requirement 8.1, 8.2
    """
    print("\n" + "="*60)
    print("TEST 6: Privacy Violation Detection")
    print("="*60)
    
    # Test with simulated violation
    print("Testing violation detection with simulated raw audio...")
    
    # Create a dict with raw audio (should be detected)
    test_data = {
        'features': {
            'pitch': 300.0,
            'intensity': -20.0,
            'audio': np.random.randn(16000)  # This should be detected!
        }
    }
    
    has_no_audio = verify_no_raw_audio_in_dict(test_data)
    
    if not has_no_audio:
        print("✅ PASS: Raw audio correctly detected in test data")
    else:
        print("❌ FAIL: Failed to detect raw audio in test data")
        return False
    
    # Test with clean data
    print("\nTesting with clean data...")
    clean_data = {
        'features': {
            'pitch': 300.0,
            'intensity': -20.0,
            'mfccs': [1.0, 2.0, 3.0]  # Small array is OK
        }
    }
    
    has_no_audio = verify_no_raw_audio_in_dict(clean_data)
    
    if has_no_audio:
        print("✅ PASS: Clean data correctly validated")
    else:
        print("❌ FAIL: Clean data incorrectly flagged")
        return False
    
    return True


def run_all_tests():
    """Run all privacy safeguard tests."""
    print("\n" + "="*70)
    print("🔒 PRIVACY SAFEGUARDS TEST SUITE")
    print("="*70)
    print("Testing Requirements 8.1 and 8.2:")
    print("  8.1: No raw audio transmitted over network")
    print("  8.2: Raw audio cleared from memory after processing")
    print("="*70)
    
    tests = [
        ("Audio Disposal", test_audio_disposal),
        ("Features No Raw Audio", test_features_no_raw_audio),
        ("Feedback Storage No Raw Audio", test_feedback_storage_no_raw_audio),
        ("Network Transmission Safety", test_network_transmission_safety),
        ("Privacy Logging", test_privacy_logging),
        ("Privacy Violation Detection", test_privacy_violation_detection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All privacy safeguard tests passed!")
        print("✅ Requirements 8.1 and 8.2 validated")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("❌ Privacy requirements not fully met")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
