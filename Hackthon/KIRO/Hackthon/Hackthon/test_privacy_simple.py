#!/usr/bin/env python3
"""
Simple Privacy Safeguards Test

Quick validation of privacy requirements:
- Requirement 8.1: No raw audio transmitted over network
- Requirement 8.2: Raw audio cleared from memory after processing
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from privacy_logger import verify_no_raw_audio_in_dict, get_privacy_logger


def test_privacy_logger_initialization():
    """Test that privacy logger initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: Privacy Logger Initialization")
    print("="*60)
    
    try:
        logger = get_privacy_logger()
        print("✅ PASS: Privacy logger initialized")
        
        # Test logging methods
        logger.log_audio_capture(16000, 1.0)
        logger.log_audio_disposal("test_stage", success=True)
        logger.log_feature_extraction(13, has_raw_audio=False)
        logger.log_network_check("/api/test", has_audio=False)
        logger.log_feedback_storage(has_raw_audio=False)
        
        print("✅ PASS: All logging methods work")
        
        # Get statistics
        stats = logger.get_statistics()
        print(f"\nStatistics:")
        print(f"  Audio captured: {stats['audio_captured']}")
        print(f"  Audio disposed: {stats['audio_disposed']}")
        print(f"  Features extracted: {stats['features_extracted']}")
        print(f"  Network checks: {stats['network_checks']}")
        print(f"  Privacy violations: {stats['privacy_violations']}")
        
        if stats['privacy_violations'] == 0:
            print("✅ PASS: No violations logged")
        else:
            print(f"❌ FAIL: {stats['privacy_violations']} violations")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_raw_audio_detection():
    """Test that raw audio detection works correctly."""
    print("\n" + "="*60)
    print("TEST 2: Raw Audio Detection")
    print("="*60)
    
    # Test 1: Clean data (should pass)
    print("\nTest 2.1: Clean data without raw audio")
    clean_data = {
        'cryType': 'hunger',
        'confidence': 75.0,
        'features': {
            'pitch': 300.0,
            'intensity': -20.0,
            'mfccs': [1.0, 2.0, 3.0, 4.0, 5.0]  # Small array is OK
        }
    }
    
    if verify_no_raw_audio_in_dict(clean_data):
        print("✅ PASS: Clean data validated correctly")
    else:
        print("❌ FAIL: Clean data incorrectly flagged")
        return False
    
    # Test 2: Data with forbidden key (should fail)
    print("\nTest 2.2: Data with forbidden 'audio' key")
    bad_data_1 = {
        'features': {
            'pitch': 300.0,
            'audio': [1.0] * 100  # Forbidden key
        }
    }
    
    if not verify_no_raw_audio_in_dict(bad_data_1):
        print("✅ PASS: Forbidden key detected correctly")
    else:
        print("❌ FAIL: Failed to detect forbidden key")
        return False
    
    # Test 3: Data with large list (should fail)
    print("\nTest 2.3: Data with large numeric list")
    bad_data_2 = {
        'features': {
            'pitch': 300.0,
            'samples': [0.5] * 1000  # Large list of numbers
        }
    }
    
    if not verify_no_raw_audio_in_dict(bad_data_2):
        print("✅ PASS: Large numeric list detected correctly")
    else:
        print("❌ FAIL: Failed to detect large numeric list")
        return False
    
    return True


def test_privacy_violation_logging():
    """Test that privacy violations are logged correctly."""
    print("\n" + "="*60)
    print("TEST 3: Privacy Violation Logging")
    print("="*60)
    
    logger = get_privacy_logger()
    
    # Get initial violation count
    initial_stats = logger.get_statistics()
    initial_violations = initial_stats['privacy_violations']
    
    # Log a violation
    logger.log_privacy_violation("TEST_VIOLATION", "This is a test violation")
    
    # Check that violation was logged
    new_stats = logger.get_statistics()
    new_violations = new_stats['privacy_violations']
    
    if new_violations == initial_violations + 1:
        print("✅ PASS: Privacy violation logged correctly")
        return True
    else:
        print(f"❌ FAIL: Expected {initial_violations + 1} violations, got {new_violations}")
        return False


def test_disposal_rate_calculation():
    """Test that disposal rate is calculated correctly."""
    print("\n" + "="*60)
    print("TEST 4: Disposal Rate Calculation")
    print("="*60)
    
    logger = get_privacy_logger()
    
    # Log some captures and disposals
    for i in range(5):
        logger.log_audio_capture(16000, 1.0)
        logger.log_audio_disposal(f"stage_{i}", success=True)
    
    stats = logger.get_statistics()
    
    print(f"Audio captured: {stats['audio_captured']}")
    print(f"Audio disposed: {stats['audio_disposed']}")
    print(f"Disposal rate: {stats['disposal_rate']:.1f}%")
    
    if stats['disposal_rate'] == 100.0:
        print("✅ PASS: 100% disposal rate achieved")
        return True
    else:
        print(f"❌ FAIL: Expected 100% disposal rate, got {stats['disposal_rate']:.1f}%")
        return False


def test_privacy_summary():
    """Test that privacy summary prints correctly."""
    print("\n" + "="*60)
    print("TEST 5: Privacy Summary")
    print("="*60)
    
    logger = get_privacy_logger()
    
    try:
        logger.print_summary()
        print("✅ PASS: Privacy summary printed successfully")
        return True
    except Exception as e:
        print(f"❌ FAIL: Error printing summary: {e}")
        return False


def run_all_tests():
    """Run all simple privacy tests."""
    print("\n" + "="*70)
    print("SIMPLE PRIVACY SAFEGUARDS TEST SUITE")
    print("="*70)
    print("Testing Requirements 8.1 and 8.2:")
    print("  8.1: No raw audio transmitted over network")
    print("  8.2: Raw audio cleared from memory after processing")
    print("="*70)
    
    tests = [
        ("Privacy Logger Initialization", test_privacy_logger_initialization),
        ("Raw Audio Detection", test_raw_audio_detection),
        ("Privacy Violation Logging", test_privacy_violation_logging),
        ("Disposal Rate Calculation", test_disposal_rate_calculation),
        ("Privacy Summary", test_privacy_summary),
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
        print("\nAll privacy safeguard tests passed!")
        print("Privacy logging infrastructure validated")
        return True
    else:
        print(f"\n{total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
