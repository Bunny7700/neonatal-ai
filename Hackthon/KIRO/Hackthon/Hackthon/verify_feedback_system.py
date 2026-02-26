#!/usr/bin/env python3
"""
Verification script for FeedbackSystem - tests without numpy.
"""

import os
import json
import shutil
import tempfile
import sys

# Import FeedbackSystem
try:
    from feedback_system import FeedbackSystem
    print("✓ FeedbackSystem imported successfully")
except Exception as e:
    print(f"✗ Failed to import FeedbackSystem: {e}")
    sys.exit(1)


def verify_basic_functionality():
    """Verify basic feedback system functionality."""
    print("\n" + "=" * 60)
    print("Verifying FeedbackSystem Basic Functionality")
    print("=" * 60)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"\nUsing temporary directory: {temp_dir}")
    
    try:
        # Test 1: Initialize
        print("\n[Test 1] Initializing FeedbackSystem...")
        fs = FeedbackSystem(storage_path=temp_dir)
        print("  ✓ FeedbackSystem initialized")
        
        # Test 2: Record feedback
        print("\n[Test 2] Recording feedback...")
        features = {
            'pitch': 350.5,
            'pitch_std': 25.3,
            'intensity': -22.5,
            'intensity_std': 5.2,
            'spectral_centroid': 450.0,
            'spectral_rolloff': 800.0,
            'zero_crossing_rate': 0.15,
            'duration': 1.5
        }
        
        success = fs.record_feedback(
            features=features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5,
            timestamp=1234567890.0
        )
        
        if success:
            print("  ✓ Feedback recorded successfully")
        else:
            print("  ✗ Failed to record feedback")
            return False
        
        # Test 3: Check file creation
        print("\n[Test 3] Checking file creation...")
        files = os.listdir(temp_dir)
        print(f"  Files created: {len(files)}")
        if len(files) == 1:
            print(f"  ✓ File created: {files[0]}")
        else:
            print(f"  ✗ Expected 1 file, got {len(files)}")
            return False
        
        # Test 4: Verify file content
        print("\n[Test 4] Verifying file content...")
        filepath = os.path.join(temp_dir, files[0])
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        print(f"  Predicted type: {data.get('predicted_type')}")
        print(f"  Actual type: {data.get('actual_type')}")
        print(f"  Confidence: {data.get('confidence')}")
        print(f"  Features count: {len(data.get('features', {}))}")
        
        # Verify no raw audio
        forbidden_keys = ['audio', 'raw_audio', 'waveform', 'samples', 'signal']
        has_audio = any(key in data for key in forbidden_keys)
        
        if not has_audio:
            print("  ✓ No raw audio data stored (privacy preserved)")
        else:
            print("  ✗ Raw audio data found in feedback!")
            return False
        
        # Test 5: Retrieve feedback
        print("\n[Test 5] Retrieving feedback...")
        feedback_data = fs.get_feedback_data()
        print(f"  Retrieved entries: {len(feedback_data)}")
        
        if len(feedback_data) == 1:
            print("  ✓ Feedback retrieved successfully")
            entry = feedback_data[0]
            print(f"    - Predicted: {entry['predicted_type']}")
            print(f"    - Actual: {entry['actual_type']}")
            print(f"    - Confidence: {entry['confidence']}")
        else:
            print(f"  ✗ Expected 1 entry, got {len(feedback_data)}")
            return False
        
        # Test 6: Feedback count
        print("\n[Test 6] Checking feedback count...")
        count = fs.get_feedback_count()
        print(f"  Count: {count}")
        
        if count == 1:
            print("  ✓ Count is correct")
        else:
            print(f"  ✗ Expected count 1, got {count}")
            return False
        
        # Test 7: Add more feedback
        print("\n[Test 7] Adding multiple feedback entries...")
        for i in range(4):
            features = {
                'pitch': 300.0 + i * 50,
                'intensity': -20.0 - i * 5,
                'duration': 1.0 + i * 0.5
            }
            
            fs.record_feedback(
                features=features,
                predicted_type='hunger',
                actual_type='sleep_discomfort',
                confidence=60.0 + i * 5,
                timestamp=1000.0 + i
            )
        
        new_count = fs.get_feedback_count()
        print(f"  New count: {new_count}")
        
        if new_count == 5:
            print("  ✓ All entries added successfully")
        else:
            print(f"  ✗ Expected count 5, got {new_count}")
            return False
        
        # Test 8: Export feedback
        print("\n[Test 8] Exporting feedback...")
        export_path = os.path.join(temp_dir, "export.json")
        success = fs.export_feedback(export_path)
        
        if success and os.path.exists(export_path):
            print("  ✓ Feedback exported successfully")
            
            with open(export_path, 'r') as f:
                export_data = json.load(f)
            
            print(f"  Total entries in export: {export_data['total_entries']}")
            
            if export_data['total_entries'] == 5:
                print("  ✓ Export contains all entries")
            else:
                print(f"  ✗ Expected 5 entries, got {export_data['total_entries']}")
                return False
        else:
            print("  ✗ Export failed")
            return False
        
        # Test 9: Feedback summary
        print("\n[Test 9] Getting feedback summary...")
        summary = fs.get_feedback_summary()
        
        print(f"  Total entries: {summary['total_entries']}")
        print(f"  By predicted type: {summary['by_predicted_type']}")
        print(f"  By actual type: {summary['by_actual_type']}")
        print(f"  Correction rate: {summary['correction_rate']:.1f}%")
        
        if summary['total_entries'] == 5:
            print("  ✓ Summary generated successfully")
        else:
            print(f"  ✗ Expected 5 entries, got {summary['total_entries']}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        print(f"\nCleaning up temporary directory...")
        shutil.rmtree(temp_dir)
        print("  ✓ Cleanup complete")


if __name__ == "__main__":
    success = verify_basic_functionality()
    sys.exit(0 if success else 1)
