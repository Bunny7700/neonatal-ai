"""
Unit tests for FeedbackSystem class.

Tests feedback recording, retrieval, export, and privacy features.
Requirements: 6.3, 6.4, 8.3
"""

import pytest
import os
import json
import shutil
import tempfile
from feedback_system import FeedbackSystem


@pytest.fixture
def temp_storage():
    """Create a temporary directory for feedback storage."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def feedback_system(temp_storage):
    """Create a FeedbackSystem instance with temporary storage."""
    return FeedbackSystem(storage_path=temp_storage)


@pytest.fixture
def sample_features():
    """Create sample features for testing (no numpy arrays)."""
    return {
        'pitch': 350.5,
        'pitch_std': 25.3,
        'intensity': -22.5,
        'intensity_std': 5.2,
        'spectral_centroid': 450.0,
        'spectral_rolloff': 800.0,
        'zero_crossing_rate': 0.15,
        'duration': 1.5
    }


class TestFeedbackRecording:
    """Tests for feedback recording functionality."""
    
    def test_record_feedback_success(self, feedback_system, temp_storage, sample_features):
        """Test that feedback can be recorded successfully."""
        success = feedback_system.record_feedback(
            features=sample_features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5,
            timestamp=1234567890.0
        )
        
        assert success, "Feedback recording should succeed"
        
        # Check that file was created
        files = os.listdir(temp_storage)
        assert len(files) == 1, "Should have created one feedback file"
        assert files[0].startswith("feedback_"), "File should start with 'feedback_'"
        assert files[0].endswith(".json"), "File should end with '.json'"
    
    def test_record_feedback_content(self, feedback_system, temp_storage, sample_features):
        """Test that recorded feedback contains correct data."""
        feedback_system.record_feedback(
            features=sample_features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5,
            timestamp=1234567890.0
        )
        
        # Load and verify the file
        files = os.listdir(temp_storage)
        with open(os.path.join(temp_storage, files[0]), 'r') as f:
            data = json.load(f)
        
        assert data['predicted_type'] == 'hunger', "Predicted type should match"
        assert data['actual_type'] == 'pain_distress', "Actual type should match"
        assert data['confidence'] == 65.5, "Confidence should match"
        assert data['timestamp'] == 1234567890.0, "Timestamp should match"
        assert 'features' in data, "Should contain features"
        assert 'pitch' in data['features'], "Features should contain pitch"
    
    def test_record_feedback_no_raw_audio(self, feedback_system, temp_storage, sample_features):
        """Test that no raw audio is stored (privacy requirement)."""
        feedback_system.record_feedback(
            features=sample_features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5
        )
        
        # Load the file
        files = os.listdir(temp_storage)
        with open(os.path.join(temp_storage, files[0]), 'r') as f:
            data = json.load(f)
        
        # Verify no raw audio fields
        forbidden_keys = ['audio', 'raw_audio', 'waveform', 'samples', 'signal']
        for key in forbidden_keys:
            assert key not in data, f"Should NOT contain '{key}' field"
            assert key not in data.get('features', {}), \
                f"Features should NOT contain '{key}' field"
    
    def test_record_multiple_feedback(self, feedback_system, temp_storage, sample_features):
        """Test recording multiple feedback entries."""
        for i in range(3):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='hunger',
                actual_type='sleep_discomfort',
                confidence=60.0 + i * 5,
                timestamp=1000.0 + i
            )
        
        files = os.listdir(temp_storage)
        assert len(files) == 3, "Should have created three feedback files"


class TestFeedbackRetrieval:
    """Tests for feedback retrieval functionality."""
    
    def test_get_feedback_data_empty(self, feedback_system):
        """Test retrieving feedback when none exists."""
        feedback_data = feedback_system.get_feedback_data()
        assert len(feedback_data) == 0, "Should return empty list"
    
    def test_get_feedback_data_single(self, feedback_system, sample_features):
        """Test retrieving a single feedback entry."""
        feedback_system.record_feedback(
            features=sample_features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=65.5,
            timestamp=1234567890.0
        )
        
        feedback_data = feedback_system.get_feedback_data()
        assert len(feedback_data) == 1, "Should retrieve 1 feedback entry"
        
        entry = feedback_data[0]
        assert entry['predicted_type'] == 'hunger'
        assert entry['actual_type'] == 'pain_distress'
        assert entry['confidence'] == 65.5
        assert 'features' in entry
    
    def test_get_feedback_data_sorted(self, feedback_system, sample_features):
        """Test that retrieved feedback is sorted by timestamp."""
        # Add entries in reverse order
        for i in range(3, 0, -1):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='hunger',
                actual_type='sleep_discomfort',
                confidence=60.0,
                timestamp=float(i)
            )
        
        feedback_data = feedback_system.get_feedback_data()
        
        # Verify entries are sorted by timestamp (ascending)
        for i in range(len(feedback_data) - 1):
            assert feedback_data[i]['timestamp'] <= feedback_data[i+1]['timestamp'], \
                "Entries should be sorted by timestamp"


class TestFeedbackExport:
    """Tests for feedback export functionality."""
    
    def test_export_feedback_success(self, feedback_system, temp_storage, sample_features):
        """Test that feedback can be exported successfully."""
        # Add some feedback
        for i in range(2):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='diaper_change',
                actual_type='hunger',
                confidence=55.0,
                timestamp=2000.0 + i
            )
        
        # Export
        export_path = os.path.join(temp_storage, "export.json")
        success = feedback_system.export_feedback(export_path)
        
        assert success, "Export should succeed"
        assert os.path.exists(export_path), "Export file should exist"
    
    def test_export_feedback_content(self, feedback_system, temp_storage, sample_features):
        """Test that exported feedback contains correct data."""
        # Add feedback
        feedback_system.record_feedback(
            features=sample_features,
            predicted_type='hunger',
            actual_type='pain_distress',
            confidence=70.0,
            timestamp=3000.0
        )
        
        # Export
        export_path = os.path.join(temp_storage, "export.json")
        feedback_system.export_feedback(export_path)
        
        # Load and verify
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert 'total_entries' in export_data
        assert export_data['total_entries'] == 1
        assert 'feedback_entries' in export_data
        assert len(export_data['feedback_entries']) == 1
    
    def test_export_feedback_empty(self, feedback_system, temp_storage):
        """Test exporting when no feedback exists."""
        export_path = os.path.join(temp_storage, "export.json")
        success = feedback_system.export_feedback(export_path)
        
        assert not success, "Export should fail when no feedback exists"


class TestFeedbackCount:
    """Tests for feedback count functionality."""
    
    def test_get_feedback_count_empty(self, feedback_system):
        """Test count when no feedback exists."""
        count = feedback_system.get_feedback_count()
        assert count == 0, "Initial count should be 0"
    
    def test_get_feedback_count_multiple(self, feedback_system, sample_features):
        """Test count with multiple entries."""
        for i in range(5):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='hunger',
                actual_type='hunger',
                confidence=70.0
            )
        
        count = feedback_system.get_feedback_count()
        assert count == 5, "Count should be 5"


class TestFeedbackSummary:
    """Tests for feedback summary functionality."""
    
    def test_get_feedback_summary_empty(self, feedback_system):
        """Test summary when no feedback exists."""
        summary = feedback_system.get_feedback_summary()
        
        assert summary['total_entries'] == 0
        assert summary['by_predicted_type'] == {}
        assert summary['by_actual_type'] == {}
        assert summary['correction_rate'] == 0.0
    
    def test_get_feedback_summary_with_corrections(self, feedback_system, sample_features):
        """Test summary with correct and incorrect predictions."""
        # 2 correct predictions
        for i in range(2):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='hunger',
                actual_type='hunger',
                confidence=70.0
            )
        
        # 3 incorrect predictions
        for i in range(3):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='hunger',
                actual_type='pain_distress',
                confidence=65.0
            )
        
        summary = feedback_system.get_feedback_summary()
        
        assert summary['total_entries'] == 5
        assert summary['by_predicted_type']['hunger'] == 5
        assert summary['by_actual_type']['hunger'] == 2
        assert summary['by_actual_type']['pain_distress'] == 3
        assert summary['correction_rate'] == 60.0  # 3/5 = 60%


class TestFeedbackClear:
    """Tests for feedback clearing functionality."""
    
    def test_clear_feedback(self, feedback_system, sample_features):
        """Test clearing all feedback."""
        # Add some feedback
        for i in range(3):
            feedback_system.record_feedback(
                features=sample_features,
                predicted_type='hunger',
                actual_type='hunger',
                confidence=70.0
            )
        
        # Verify feedback exists
        assert feedback_system.get_feedback_count() == 3
        
        # Clear feedback
        success = feedback_system.clear_feedback()
        assert success, "Clear should succeed"
        
        # Verify feedback is cleared
        assert feedback_system.get_feedback_count() == 0
