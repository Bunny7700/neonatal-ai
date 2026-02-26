# test_feature_extractor.py
"""
Unit tests for FeatureExtractor class

Tests feature extraction functionality including:
- Pitch extraction
- Frequency spectrum analysis
- Intensity calculation
- MFCC extraction
- Duration calculation
- Complete feature extraction
- Edge cases (silence, short audio, extreme values)
"""

import pytest
import numpy as np
from feature_extractor import FeatureExtractor


class TestFeatureExtractor:
    """Test suite for FeatureExtractor class"""
    
    @pytest.fixture
    def extractor(self):
        """Create a FeatureExtractor instance for testing"""
        return FeatureExtractor(sample_rate=16000, n_mfcc=13)
    
    @pytest.fixture
    def sample_audio(self):
        """Generate a sample audio signal (1 second, 440 Hz sine wave)"""
        sample_rate = 16000
        duration = 1.0
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        return audio
    
    @pytest.fixture
    def cry_like_audio(self):
        """Generate a cry-like audio signal (300 Hz with harmonics)"""
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Fundamental frequency at 300 Hz (typical infant cry)
        audio = 0.3 * np.sin(2 * np.pi * 300 * t)
        # Add harmonics
        audio += 0.15 * np.sin(2 * np.pi * 600 * t)
        audio += 0.1 * np.sin(2 * np.pi * 900 * t)
        return audio
    
    # Test pitch extraction
    def test_extract_pitch_normal_audio(self, extractor, cry_like_audio):
        """Test pitch extraction on normal cry-like audio"""
        pitch = extractor.extract_pitch(cry_like_audio)
        # Should detect pitch around 300 Hz (with some tolerance)
        assert 250 <= pitch <= 350, f"Expected pitch around 300 Hz, got {pitch}"
    
    def test_extract_pitch_empty_audio(self, extractor):
        """Test pitch extraction on empty audio"""
        audio = np.array([])
        pitch = extractor.extract_pitch(audio)
        assert pitch == 0.0
    
    def test_extract_pitch_silence(self, extractor):
        """Test pitch extraction on silence"""
        audio = np.zeros(16000)
        pitch = extractor.extract_pitch(audio)
        # Silence should return 0.0 or very low pitch
        assert pitch >= 0.0
    
    def test_extract_pitch_with_nan(self, extractor):
        """Test pitch extraction handles NaN values"""
        audio = np.array([0.1, 0.2, np.nan, 0.3, 0.4] * 3200)
        pitch = extractor.extract_pitch(audio)
        # Should handle NaN gracefully and return a valid value
        assert np.isfinite(pitch)
        assert pitch >= 0.0
    
    # Test frequency spectrum
    def test_extract_frequency_spectrum_normal_audio(self, extractor, sample_audio):
        """Test frequency spectrum extraction on normal audio"""
        spectrum = extractor.extract_frequency_spectrum(sample_audio)
        assert len(spectrum) > 0
        assert np.all(np.isfinite(spectrum))
        # Spectrum should be normalized (sum to 1)
        assert np.abs(np.sum(spectrum) - 1.0) < 0.01
    
    def test_extract_frequency_spectrum_empty_audio(self, extractor):
        """Test frequency spectrum on empty audio"""
        audio = np.array([])
        spectrum = extractor.extract_frequency_spectrum(audio)
        assert len(spectrum) == 0
    
    def test_extract_frequency_spectrum_short_audio(self, extractor):
        """Test frequency spectrum on very short audio"""
        audio = np.array([0.1, 0.2, 0.3])
        spectrum = extractor.extract_frequency_spectrum(audio)
        assert len(spectrum) > 0
        assert np.all(np.isfinite(spectrum))
    
    # Test intensity extraction
    def test_extract_intensity_normal_audio(self, extractor, sample_audio):
        """Test intensity extraction on normal audio"""
        intensity = extractor.extract_intensity(sample_audio)
        # Should return a reasonable dB value
        assert -100 <= intensity <= 0
        assert np.isfinite(intensity)
    
    def test_extract_intensity_silence(self, extractor):
        """Test intensity on silence"""
        audio = np.zeros(16000)
        intensity = extractor.extract_intensity(audio)
        # Silence should have very low intensity
        assert intensity < -50
    
    def test_extract_intensity_loud_audio(self, extractor):
        """Test intensity on very loud audio (clipping)"""
        audio = np.ones(16000)  # Maximum amplitude
        intensity = extractor.extract_intensity(audio)
        # Should be close to 0 dB
        assert intensity > -10
    
    def test_extract_intensity_empty_audio(self, extractor):
        """Test intensity on empty audio"""
        audio = np.array([])
        intensity = extractor.extract_intensity(audio)
        assert intensity == 0.0
    
    # Test MFCC extraction
    def test_extract_mfccs_normal_audio(self, extractor, sample_audio):
        """Test MFCC extraction on normal audio"""
        mfccs = extractor.extract_mfccs(sample_audio)
        assert len(mfccs) == 13
        assert np.all(np.isfinite(mfccs))
    
    def test_extract_mfccs_empty_audio(self, extractor):
        """Test MFCC extraction on empty audio"""
        audio = np.array([])
        mfccs = extractor.extract_mfccs(audio)
        assert len(mfccs) == 13
        assert np.all(mfccs == 0.0)
    
    def test_extract_mfccs_silence(self, extractor):
        """Test MFCC extraction on silence"""
        audio = np.zeros(16000)
        mfccs = extractor.extract_mfccs(audio)
        assert len(mfccs) == 13
        assert np.all(np.isfinite(mfccs))
    
    def test_extract_mfccs_with_inf(self, extractor):
        """Test MFCC extraction handles infinite values"""
        audio = np.array([0.1, 0.2, np.inf, 0.3, 0.4] * 3200)
        mfccs = extractor.extract_mfccs(audio)
        assert len(mfccs) == 13
        assert np.all(np.isfinite(mfccs))
    
    # Test duration extraction
    def test_extract_duration_one_second(self, extractor, sample_audio):
        """Test duration extraction on 1-second audio"""
        duration = extractor.extract_duration(sample_audio)
        assert 0.99 <= duration <= 1.01  # Allow small tolerance
    
    def test_extract_duration_short_audio(self, extractor):
        """Test duration on very short audio (< 100ms)"""
        audio = np.random.randn(800)  # 50ms at 16kHz
        duration = extractor.extract_duration(audio)
        assert 0.04 <= duration <= 0.06
    
    def test_extract_duration_empty_audio(self, extractor):
        """Test duration on empty audio"""
        audio = np.array([])
        duration = extractor.extract_duration(audio)
        assert duration == 0.0
    
    # Test additional spectral features
    def test_extract_spectral_centroid(self, extractor, sample_audio):
        """Test spectral centroid extraction"""
        centroid = extractor.extract_spectral_centroid(sample_audio)
        assert centroid > 0
        assert np.isfinite(centroid)
    
    def test_extract_spectral_rolloff(self, extractor, sample_audio):
        """Test spectral rolloff extraction"""
        rolloff = extractor.extract_spectral_rolloff(sample_audio)
        assert rolloff > 0
        assert np.isfinite(rolloff)
    
    def test_extract_zero_crossing_rate(self, extractor, sample_audio):
        """Test zero-crossing rate extraction"""
        zcr = extractor.extract_zero_crossing_rate(sample_audio)
        assert 0 <= zcr <= 1
        assert np.isfinite(zcr)
    
    def test_extract_pitch_std(self, extractor, cry_like_audio):
        """Test pitch standard deviation extraction"""
        pitch_std = extractor.extract_pitch_std(cry_like_audio)
        assert pitch_std >= 0
        assert np.isfinite(pitch_std)
    
    def test_extract_intensity_std(self, extractor, sample_audio):
        """Test intensity standard deviation extraction"""
        intensity_std = extractor.extract_intensity_std(sample_audio)
        assert intensity_std >= 0
        assert np.isfinite(intensity_std)
    
    # Test complete feature extraction
    def test_extract_all_features_normal_audio(self, extractor, cry_like_audio):
        """Test complete feature extraction on normal audio"""
        features = extractor.extract_all_features(cry_like_audio)
        
        # Check all required features are present
        required_features = [
            'pitch', 'pitch_std', 'intensity', 'intensity_std',
            'mfccs', 'spectral_centroid', 'spectral_rolloff',
            'zero_crossing_rate', 'duration', 'frequency_spectrum'
        ]
        
        for feature_name in required_features:
            assert feature_name in features, f"Missing feature: {feature_name}"
        
        # Check feature types and values
        assert isinstance(features['pitch'], (int, float))
        assert isinstance(features['pitch_std'], (int, float))
        assert isinstance(features['intensity'], (int, float))
        assert isinstance(features['intensity_std'], (int, float))
        assert isinstance(features['mfccs'], np.ndarray)
        assert len(features['mfccs']) == 13
        assert isinstance(features['spectral_centroid'], (int, float))
        assert isinstance(features['spectral_rolloff'], (int, float))
        assert isinstance(features['zero_crossing_rate'], (int, float))
        assert isinstance(features['duration'], (int, float))
        assert isinstance(features['frequency_spectrum'], np.ndarray)
        
        # Check all values are finite
        assert np.isfinite(features['pitch'])
        assert np.isfinite(features['pitch_std'])
        assert np.isfinite(features['intensity'])
        assert np.isfinite(features['intensity_std'])
        assert np.all(np.isfinite(features['mfccs']))
        assert np.isfinite(features['spectral_centroid'])
        assert np.isfinite(features['spectral_rolloff'])
        assert np.isfinite(features['zero_crossing_rate'])
        assert np.isfinite(features['duration'])
        assert np.all(np.isfinite(features['frequency_spectrum']))
    
    def test_extract_all_features_empty_audio(self, extractor):
        """Test complete feature extraction on empty audio"""
        audio = np.array([])
        features = extractor.extract_all_features(audio)
        
        # Should return all features with default values
        assert features['pitch'] == 0.0
        assert features['duration'] == 0.0
        assert len(features['mfccs']) == 13
    
    def test_extract_all_features_silence(self, extractor):
        """Test complete feature extraction on silence"""
        audio = np.zeros(16000)
        features = extractor.extract_all_features(audio)
        
        # All features should be valid (no NaN or Inf)
        assert np.isfinite(features['pitch'])
        assert np.isfinite(features['intensity'])
        assert np.all(np.isfinite(features['mfccs']))
        
        # Duration should be correct
        assert 0.99 <= features['duration'] <= 1.01
    
    def test_extract_all_features_extreme_pitch(self, extractor):
        """Test feature extraction on audio with extreme pitch"""
        # Very high frequency (outside typical cry range)
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 2000 * t)  # 2000 Hz
        
        features = extractor.extract_all_features(audio)
        
        # Should still extract all features without errors
        assert np.all(np.isfinite(features['mfccs']))
        assert np.isfinite(features['intensity'])
        assert np.isfinite(features['spectral_centroid'])
    
    def test_extract_all_features_very_short_audio(self, extractor):
        """Test feature extraction on very short audio (< 100ms)"""
        audio = np.random.randn(800)  # 50ms at 16kHz
        features = extractor.extract_all_features(audio)
        
        # Should handle short audio gracefully
        assert 0.04 <= features['duration'] <= 0.06
        assert len(features['mfccs']) == 13
        assert np.all(np.isfinite(features['mfccs']))
    
    def test_extract_all_features_with_invalid_values(self, extractor):
        """Test feature extraction handles invalid values (NaN, Inf)"""
        audio = np.array([0.1, 0.2, np.nan, 0.3, np.inf, 0.4, -np.inf] * 2000)
        features = extractor.extract_all_features(audio)
        
        # All features should be finite (invalid values handled)
        assert np.isfinite(features['pitch'])
        assert np.isfinite(features['intensity'])
        assert np.all(np.isfinite(features['mfccs']))
        assert np.isfinite(features['spectral_centroid'])
        assert np.isfinite(features['spectral_rolloff'])
        assert np.isfinite(features['zero_crossing_rate'])
    
    # Test different sample rates
    def test_different_sample_rate(self):
        """Test feature extractor with different sample rate"""
        extractor = FeatureExtractor(sample_rate=8000, n_mfcc=13)
        
        # Generate audio at 8kHz
        sample_rate = 8000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 300 * t)
        
        features = extractor.extract_all_features(audio)
        
        # Should work correctly with different sample rate
        assert 0.99 <= features['duration'] <= 1.01
        assert len(features['mfccs']) == 13
    
    def test_different_n_mfcc(self):
        """Test feature extractor with different number of MFCCs"""
        extractor = FeatureExtractor(sample_rate=16000, n_mfcc=20)
        
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 300 * t)
        
        features = extractor.extract_all_features(audio)
        
        # Should return 20 MFCCs instead of 13
        assert len(features['mfccs']) == 20


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
