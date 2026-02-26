#!/usr/bin/env python3
"""
Simple unit tests for FeedbackSystem class.

Tests basic functionality including:
- Feedback recording
- Feedback retrieval
- Feedback export
- Privacy (no raw audio storage)
"""

import os
import json
import shutil
import tempfile
import numpy as np
from feedback_system import FeedbackSystem


def test_feedback_recording():
    """Test that feedback can be recorded successfully."""
    print("Testing feedback recording...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Create sample features (no raw audio!)
        features = {
            'pitch': 350.5,
            'pitch_std': 25.3,
            'intensity': -22.5,
            'intensity_std': 5.2,
            'mfccs': np.array([1.2, 3.4, 5.6, 7.8, 9.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8]),
            'spectral_centroid': 450.0,
            'spectral_rolloff': 800.0,
            'zero_crossing_rate': 0.15,
            'duration': 1.5,
            'frequency_spectrum': np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        }
        
        # Record feedback
        success = fs.record_feedback(
            features=features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5,
            timestamp=1234567890.0
        )
        
        assert success, "Feedback recording should succeed"
        
        # Check that file was created
        files = os.listdir(temp_dir)
        assert len(files) == 1, "Should have created one feedback file"
        assert files[0].startswith("feedback_"), "File should start with 'feedback_'"
        assert files[0].endswith(".json"), "File should end with '.json'"
        
        # Load and verify the file
        with open(os.path.join(temp_dir, files[0]), 'r') as f:
            data = json.load(f)
        
        assert data['predicted_type'] == 'hunger', "Predicted type should match"
        assert data['actual_type'] == 'pain_distress', "Actual type should match"
        assert data['confidence'] == 65.5, "Confidence should match"
        assert data['timestamp'] == 1234567890.0, "Timestamp should match"
        assert 'features' in data, "Should contain features"
        assert 'pitch' in data['features'], "Features should contain pitch"
        
        # Verify no raw audio is stored
        assert 'audio' not in data, "Should NOT contain raw audio"
        assert 'raw_audio' not in data, "Should NOT contain raw audio"
        assert 'waveform' not in data, "Should NOT contain raw audio"
        
        print("✓ Feedback recording test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_feedback_retrieval():
    """Test that feedback can be retrieved successfully."""
    print("Testing feedback retrieval...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Record multiple feedback entries
        for i in range(3):
            features = {
                'pitch': 300.0 + i * 50,
                'intensity': -20.0 - i * 5,
                'mfccs': np.zeros(13),
                'duration': 1.0 + i * 0.5
            }
            
            fs.record_feedback(
                features=features,
                predicted_type='hunger',
                actual_type='sleep_discomfort',
                confidence=60.0 + i * 5,
                timestamp=1000.0 + i
            )
        
        # Retrieve all feedback
        feedback_data = fs.get_feedback_data()
        
        assert len(feedback_data) == 3, "Should retrieve 3 feedback entries"
        
        # Verify entries are sorted by timestamp
        for i in range(len(feedback_data) - 1):
            assert feedback_data[i]['timestamp'] <= feedback_data[i+1]['timestamp'], \
                "Entries should be sorted by timestamp"
        
        # Verify first entry
        entry = feedback_data[0]
        assert entry['predicted_type'] == 'hunger', "Predicted type should match"
        assert entry['actual_type'] == 'sleep_discomfort', "Actual type should match"
        assert entry['confidence'] == 60.0, "Confidence should match"
        assert 'features' in entry, "Should contain features"
        
        # Verify features are deserialized correctly
        assert isinstance(entry['features']['mfccs'], np.ndarray), \
            "MFCCs should be numpy array after deserialization"
        
        print("✓ Feedback retrieval test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_feedback_export():
    """Test that feedback can be exported to a file."""
    print("Testing feedback export...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Record some feedback
        for i in range(2):
            features = {
                'pitch': 350.0,
                'intensity': -25.0,
                'mfccs': np.ones(13),
                'duration': 1.2
            }
            
            fs.record_feedback(
                features=features,
                predicted_type='diaper_change',
                actual_type='hunger',
                confidence=55.0,
                timestamp=2000.0 + i
            )
        
        # Export feedback
        export_path = os.path.join(temp_dir, "export.json")
        success = fs.export_feedback(export_path)
        
        assert success, "Export should succeed"
        assert os.path.exists(export_path), "Export file should exist"
        
        # Load and verify export file
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert 'total_entries' in export_data, "Should contain total_entries"
        assert export_data['total_entries'] == 2, "Should have 2 entries"
        assert 'feedback_entries' in export_data, "Should contain feedback_entries"
        assert len(export_data['feedback_entries']) == 2, "Should have 2 feedback entries"
        
        print("✓ Feedback export test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_feedback_privacy():
    """Test that no raw audio is stored in feedback."""
    print("Testing feedback privacy...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Create features with various data types
        features = {
            'pitch': 400.0,
            'intensity': -18.0,
            'mfccs': np.random.randn(13),
            'frequency_spectrum': np.random.randn(100),
            'duration': 2.0
        }
        
        # Record feedback
        fs.record_feedback(
            features=features,
            predicted_type='pain_distress',
            actual_type='pain_distress',
            confidence=85.0
        )
        
        # Load the feedback file
        files = os.listdir(temp_dir)
        with open(os.path.join(temp_dir, files[0]), 'r') as f:
            data = json.load(f)
        
        # Verify no raw audio fields
        forbidden_keys = ['audio', 'raw_audio', 'waveform', 'samples', 'signal']
        for key in forbidden_keys:
            assert key not in data, f"Should NOT contain '{key}' field"
            assert key not in data.get('features', {}), \
                f"Features should NOT contain '{key}' field"
        
        # Verify only features are stored
        assert 'features' in data, "Should contain features"
        assert 'pitch' in data['features'], "Should contain pitch feature"
        assert 'mfccs' in data['features'], "Should contain mfccs feature"
        
        print("✓ Feedback privacy test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_feedback_count():
    """Test feedback count functionality."""
    print("Testing feedback count...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Initially should be 0
        assert fs.get_feedback_count() == 0, "Initial count should be 0"
        
        # Add some feedback
        features = {'pitch': 300.0, 'intensity': -20.0, 'mfccs': np.zeros(13)}
        
        for i in range(5):
            fs.record_feedback(
                features=features,
                predicted_type='hunger',
                actual_type='hunger',
                confidence=70.0
            )
        
        # Count should be 5
        assert fs.get_feedback_count() == 5, "Count should be 5"
        
        print("✓ Feedback count test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_feedback_summary():
    """Test feedback summary functionality."""
    print("Testing feedback summary...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize feedback system
        fs = FeedbackSystem(storage_path=temp_dir)
        
        # Add feedback with corrections
        features = {'pitch': 300.0, 'intensity': -20.0, 'mfccs': np.zeros(13)}
        
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
        
        assert summary['total_entries'] == 5, "Should have 5 total entries"
        assert summary['by_predicted_type']['hunger'] == 5, "All predicted as hunger"
        assert summary['by_actual_type']['hunger'] == 2, "2 actually hunger"
        assert summary['by_actual_type']['pain_distress'] == 3, "3 actually pain_distress"
        assert summary['correction_rate'] == 60.0, "60% correction rate (3/5)"
        
        print("✓ Feedback summary test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running FeedbackSystem Tests")
    print("=" * 60)
    
    test_feedback_recording()
    test_feedback_retrieval()
    test_feedback_export()
    test_feedback_privacy()
    test_feedback_count()
    test_feedback_summary()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
