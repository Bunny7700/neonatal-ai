#!/usr/bin/env python3
"""
Basic tests for FeedbackSystem without numpy dependency.

Tests core functionality without using numpy arrays.
"""

import os
import json
import shutil
import tempfile
from feedback_system import FeedbackSystem


def test_basic_feedback():
    """Test basic feedback recording and retrieval without numpy."""
    print("Testing basic feedback functionality...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Create simple features (no numpy arrays)
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
        
        # Record feedback
        success = fs.record_feedback(
            features=features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5,
            timestamp=1234567890.0
        )
        
        print(f"  Record feedback: {'✓' if success else '✗'}")
        assert success, "Feedback recording should succeed"
        
        # Check file was created
        files = os.listdir(temp_dir)
        print(f"  Files created: {len(files)}")
        assert len(files) == 1, "Should have created one feedback file"
        
        # Load and verify
        with open(os.path.join(temp_dir, files[0]), 'r') as f:
            data = json.load(f)
        
        print(f"  Predicted type: {data['predicted_type']}")
        print(f"  Actual type: {data['actual_type']}")
        print(f"  Confidence: {data['confidence']}")
        
        assert data['predicted_type'] == 'hunger'
        assert data['actual_type'] == 'pain_distress'
        assert data['confidence'] == 65.5
        assert 'features' in data
        
        # Verify no raw audio
        assert 'audio' not in data
        assert 'raw_audio' not in data
        print("  Privacy check: ✓ (no raw audio)")
        
        # Test retrieval
        feedback_data = fs.get_feedback_data()
        print(f"  Retrieved entries: {len(feedback_data)}")
        assert len(feedback_data) == 1
        
        # Test count
        count = fs.get_feedback_count()
        print(f"  Feedback count: {count}")
        assert count == 1
        
        print("✓ Basic feedback test passed\n")
        
    finally:
        shutil.rmtree(temp_dir)


def test_multiple_entries():
    """Test multiple feedback entries."""
    print("Testing multiple feedback entries...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Add 5 entries
        for i in range(5):
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
        
        # Check count
        count = fs.get_feedback_count()
        print(f"  Total entries: {count}")
        assert count == 5
        
        # Retrieve all
        feedback_data = fs.get_feedback_data()
        print(f"  Retrieved entries: {len(feedback_data)}")
        assert len(feedback_data) == 5
        
        # Check sorting
        for i in range(len(feedback_data) - 1):
            assert feedback_data[i]['timestamp'] <= feedback_data[i+1]['timestamp']
        print("  Sorting: ✓")
        
        print("✓ Multiple entries test passed\n")
        
    finally:
        shutil.rmtree(temp_dir)


def test_export():
    """Test feedback export."""
    print("Testing feedback export...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Add some entries
        for i in range(3):
            features = {'pitch': 350.0, 'intensity': -25.0}
            fs.record_feedback(
                features=features,
                predicted_type='diaper_change',
                actual_type='hunger',
                confidence=55.0,
                timestamp=2000.0 + i
            )
        
        # Export
        export_path = os.path.join(temp_dir, "export.json")
        success = fs.export_feedback(export_path)
        
        print(f"  Export success: {'✓' if success else '✗'}")
        assert success
        assert os.path.exists(export_path)
        
        # Load export
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        print(f"  Total entries in export: {export_data['total_entries']}")
        assert export_data['total_entries'] == 3
        assert len(export_data['feedback_entries']) == 3
        
        print("✓ Export test passed\n")
        
    finally:
        shutil.rmtree(temp_dir)


def test_summary():
    """Test feedback summary."""
    print("Testing feedback summary...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        fs = FeedbackSystem(storage_path=temp_dir)
        
        features = {'pitch': 300.0, 'intensity': -20.0}
        
        # 2 correct predictions
        for i in range(2):
            fs.record_feedback(
                features=features,
                predicted_type='hunger',
                actual_type='hunger',
                confidence=70.0
            )
        
        # 3 incorrect predictions
        for i in range(3):
            fs.record_feedback(
                features=features,
                predicted_type='hunger',
                actual_type='pain_distress',
                confidence=65.0
            )
        
        # Get summary
        summary = fs.get_feedback_summary()
        
        print(f"  Total entries: {summary['total_entries']}")
        print(f"  Predicted as hunger: {summary['by_predicted_type'].get('hunger', 0)}")
        print(f"  Actually hunger: {summary['by_actual_type'].get('hunger', 0)}")
        print(f"  Actually pain_distress: {summary['by_actual_type'].get('pain_distress', 0)}")
        print(f"  Correction rate: {summary['correction_rate']}%")
        
        assert summary['total_entries'] == 5
        assert summary['by_predicted_type']['hunger'] == 5
        assert summary['by_actual_type']['hunger'] == 2
        assert summary['by_actual_type']['pain_distress'] == 3
        assert summary['correction_rate'] == 60.0
        
        print("✓ Summary test passed\n")
        
    finally:
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running FeedbackSystem Basic Tests")
    print("=" * 60)
    print()
    
    test_basic_feedback()
    test_multiple_entries()
    test_export()
    test_summary()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
