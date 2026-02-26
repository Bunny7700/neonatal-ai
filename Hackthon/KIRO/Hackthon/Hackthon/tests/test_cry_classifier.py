# tests/test_cry_classifier.py
"""
Unit tests for CryClassifier module.

Tests cry detection, classification, confidence thresholding, and edge cases.
"""

import pytest
import numpy as np
from cry_classifier import CryClassifier


class TestCryClassifier:
    """Test suite for CryClassifier class."""
    
    @pytest.fixture
    def classifier(self):
        """Create a CryClassifier instance for testing."""
        return CryClassifier()
    
    @pytest.fixture
    def sample_audio(self):
        """Generate sample audio signal for testing."""
        # Generate 1 second of audio at 16kHz with moderate energy
        duration = 1.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Sine wave at 350 Hz (typical infant cry frequency)
        audio = 0.1 * np.sin(2 * np.pi * 350 * t)
        return audio
    
    @pytest.fixture
    def sample_features(self):
        """Generate sample feature dictionary for testing."""
        return {
            'pitch': 350.0,
            'pitch_std': 25.0,
            'intensity': -25.0,
            'intensity_std': 5.0,
            'mfccs': np.random.randn(13),
            'spectral_centroid': 500.0,
            'spectral_rolloff': 1000.0,
            'zero_crossing_rate': 0.05,
            'duration': 1.0,
            'frequency_spectrum': np.random.rand(100)
        }
    
    def test_initialization(self, classifier):
        """Test that classifier initializes correctly."""
        assert classifier is not None
        assert classifier.yamnet_model is not None
        assert classifier.CONFIDENCE_THRESHOLD == 60.0
        assert len(classifier.CRY_CATEGORIES) == 5
    
    def test_valid_cry_categories(self, classifier):
        """Test that all expected cry categories are defined."""
        expected_categories = [
            'hunger',
            'sleep_discomfort',
            'pain_distress',
            'diaper_change',
            'normal_unknown'
        ]
        assert set(classifier.CRY_CATEGORIES) == set(expected_categories)
    
    def test_detect_cry_with_audio(self, classifier, sample_audio):
        """Test cry detection with valid audio."""
        is_crying, confidence = classifier.detect_cry(sample_audio)
        
        assert isinstance(is_crying, bool)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 100.0
    
    def test_detect_cry_empty_audio(self, classifier):
        """Test cry detection with empty audio."""
        empty_audio = np.array([])
        is_crying, confidence = classifier.detect_cry(empty_audio)
        
        assert is_crying is False
        assert confidence == 0.0
    
    def test_detect_cry_silent_audio(self, classifier):
        """Test cry detection with silent audio."""
        silent_audio = np.zeros(16000)  # 1 second of silence
        is_crying, confidence = classifier.detect_cry(silent_audio)
        
        assert is_crying is False
        assert confidence < 50.0
    
    def test_detect_cry_loud_audio(self, classifier):
        """Test cry detection with loud audio."""
        # Generate loud audio (high energy)
        loud_audio = 0.5 * np.sin(2 * np.pi * 400 * np.linspace(0, 1, 16000))
        is_crying, confidence = classifier.detect_cry(loud_audio)
        
        assert is_crying is True
        assert confidence > 50.0
    
    def test_detect_cry_short_audio(self, classifier):
        """Test cry detection with very short audio."""
        # Generate 0.1 second of audio (too short for crying)
        short_audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 0.1, 1600))
        is_crying, confidence = classifier.detect_cry(short_audio)
        
        # Short audio should not be classified as crying
        assert is_crying is False
    
    def test_detect_cry_with_nan_values(self, classifier):
        """Test cry detection handles NaN values gracefully."""
        audio_with_nan = np.array([0.1, 0.2, np.nan, 0.3, 0.4] * 3200)
        is_crying, confidence = classifier.detect_cry(audio_with_nan)
        
        # Should handle NaN values without crashing
        assert isinstance(is_crying, bool)
        assert isinstance(confidence, float)
    
    def test_classify_cry_type_returns_valid_category(self, classifier, sample_features):
        """Test that classify_cry_type returns a valid category."""
        cry_type, confidence = classifier.classify_cry_type(sample_features)
        
        assert cry_type in classifier.CRY_CATEGORIES
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 100.0
    
    def test_classify_cry_type_pain_distress(self, classifier):
        """Test classification of pain/distress cry."""
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
    
    def test_classify_cry_type_hunger(self, classifier):
        """Test classification of hunger cry."""
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
    
    def test_classify_cry_type_sleep_discomfort(self, classifier):
        """Test classification of sleep discomfort cry."""
        # Features indicating sleep discomfort: variable pitch, low-moderate intensity
        sleep_features = {
            'pitch': 320.0,
            'pitch_std': 50.0,
            'intensity': -30.0,
            'intensity_std': 8.0,
            'zero_crossing_rate': 0.04,
            'duration': 2.0
        }
        
        cry_type, confidence = classifier.classify_cry_type(sleep_features)
        
        # Should classify as sleep_discomfort with reasonable confidence
        assert cry_type == 'sleep_discomfort'
        assert confidence >= 60.0
    
    def test_classify_cry_type_diaper_change(self, classifier):
        """Test classification of diaper change cry."""
        # Features indicating diaper change: high zero-crossing rate
        diaper_features = {
            'pitch': 300.0,
            'pitch_std': 30.0,
            'intensity': -28.0,
            'intensity_std': 6.0,
            'zero_crossing_rate': 0.15,
            'duration': 1.0
        }
        
        cry_type, confidence = classifier.classify_cry_type(diaper_features)
        
        # Should classify as diaper_change with reasonable confidence
        assert cry_type == 'diaper_change'
        assert confidence >= 60.0
    
    def test_classify_cry_type_empty_features(self, classifier):
        """Test classification with empty features."""
        empty_features = {}
        cry_type, confidence = classifier.classify_cry_type(empty_features)
        
        # Should return a valid category even with empty features
        assert cry_type in classifier.CRY_CATEGORIES
        assert isinstance(confidence, float)
    
    def test_predict_no_crying(self, classifier):
        """Test predict method when no crying is detected."""
        silent_audio = np.zeros(16000)
        features = {'pitch': 0.0, 'intensity': -100.0, 'duration': 1.0}
        
        result = classifier.predict(silent_audio, features)
        
        assert result['is_crying'] is False
        assert result['cry_type'] == 'normal_unknown'
        assert result['confidence'] == 0.0
        assert 'detection_confidence' in result
    
    def test_predict_with_crying(self, classifier, sample_audio, sample_features):
        """Test predict method when crying is detected."""
        result = classifier.predict(sample_audio, sample_features)
        
        assert isinstance(result['is_crying'], bool)
        assert result['cry_type'] in classifier.CRY_CATEGORIES
        assert 0.0 <= result['confidence'] <= 100.0
        assert 'detection_confidence' in result
    
    def test_predict_low_confidence_threshold(self, classifier):
        """Test that low confidence predictions are classified as normal_unknown."""
        # Create audio that will be detected as crying
        audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
        
        # Create features that will result in low confidence
        low_confidence_features = {
            'pitch': 200.0,  # Low pitch
            'pitch_std': 10.0,
            'intensity': -50.0,  # Low intensity
            'intensity_std': 2.0,
            'zero_crossing_rate': 0.02,
            'duration': 0.5
        }
        
        result = classifier.predict(audio, low_confidence_features)
        
        # If confidence < 60%, should be classified as normal_unknown
        if result['confidence'] < 60.0:
            assert result['cry_type'] == 'normal_unknown'
    
    def test_predict_high_confidence_not_unknown(self, classifier):
        """Test that high confidence predictions are not normal_unknown."""
        # Create audio that will be detected as crying
        audio = 0.2 * np.sin(2 * np.pi * 450 * np.linspace(0, 1, 16000))
        
        # Create features that will result in high confidence for pain
        high_confidence_features = {
            'pitch': 450.0,
            'pitch_std': 60.0,
            'intensity': -15.0,
            'intensity_std': 10.0,
            'zero_crossing_rate': 0.05,
            'duration': 1.0
        }
        
        result = classifier.predict(audio, high_confidence_features)
        
        # If confidence >= 60%, should be a specific category
        if result['confidence'] >= 60.0:
            assert result['cry_type'] != 'normal_unknown'
            assert result['cry_type'] in ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change']
    
    def test_confidence_threshold_boundary_59_9(self, classifier):
        """Test confidence threshold at 59.9% (below threshold)."""
        audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
        
        # Mock the classify_cry_type to return exactly 59.9% confidence
        original_method = classifier.classify_cry_type
        
        def mock_classify(features):
            return 'hunger', 59.9
        
        classifier.classify_cry_type = mock_classify
        
        result = classifier.predict(audio, {})
        
        # Should be classified as normal_unknown (below 60%)
        assert result['cry_type'] == 'normal_unknown'
        
        # Restore original method
        classifier.classify_cry_type = original_method
    
    def test_confidence_threshold_boundary_60_0(self, classifier):
        """Test confidence threshold at exactly 60.0% (at threshold)."""
        audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
        
        # Mock the classify_cry_type to return exactly 60.0% confidence
        original_method = classifier.classify_cry_type
        
        def mock_classify(features):
            return 'hunger', 60.0
        
        classifier.classify_cry_type = mock_classify
        
        result = classifier.predict(audio, {})
        
        # Should be classified as hunger (at or above 60%)
        assert result['cry_type'] == 'hunger'
        
        # Restore original method
        classifier.classify_cry_type = original_method
    
    def test_confidence_threshold_boundary_60_1(self, classifier):
        """Test confidence threshold at 60.1% (above threshold)."""
        audio = 0.1 * np.sin(2 * np.pi * 350 * np.linspace(0, 1, 16000))
        
        # Mock the classify_cry_type to return exactly 60.1% confidence
        original_method = classifier.classify_cry_type
        
        def mock_classify(features):
            return 'hunger', 60.1
        
        classifier.classify_cry_type = mock_classify
        
        result = classifier.predict(audio, {})
        
        # Should be classified as hunger (above 60%)
        assert result['cry_type'] == 'hunger'
        
        # Restore original method
        classifier.classify_cry_type = original_method
    
    def test_validate_cry_type_valid(self, classifier):
        """Test validate_cry_type with valid categories."""
        for category in classifier.CRY_CATEGORIES:
            assert classifier.validate_cry_type(category) is True
    
    def test_validate_cry_type_invalid(self, classifier):
        """Test validate_cry_type with invalid categories."""
        invalid_categories = ['invalid', 'unknown', 'test', '']
        for category in invalid_categories:
            assert classifier.validate_cry_type(category) is False
    
    def test_predict_result_structure(self, classifier, sample_audio, sample_features):
        """Test that predict returns all required fields."""
        result = classifier.predict(sample_audio, sample_features)
        
        required_fields = ['is_crying', 'cry_type', 'confidence', 'detection_confidence']
        for field in required_fields:
            assert field in result
    
    def test_confidence_score_range(self, classifier, sample_features):
        """Test that confidence scores are always in valid range."""
        # Test multiple times with different features
        for _ in range(10):
            # Randomize some features
            features = sample_features.copy()
            features['pitch'] = np.random.uniform(200, 600)
            features['intensity'] = np.random.uniform(-50, -10)
            
            cry_type, confidence = classifier.classify_cry_type(features)
            
            assert 0.0 <= confidence <= 100.0
            assert isinstance(confidence, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
