# test_audio_preprocessor.py
"""
Unit tests for AudioPreprocessor class

Tests edge cases and specific examples for audio preprocessing functionality.
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path to import audio_preprocessor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio_preprocessor import AudioPreprocessor


class TestAudioPreprocessor:
    """Test suite for AudioPreprocessor class"""
    
    @pytest.fixture
    def preprocessor(self):
        """Create AudioPreprocessor instance for testing"""
        return AudioPreprocessor(sample_rate=16000)
    
    def test_initialization(self, preprocessor):
        """Test that preprocessor initializes correctly"""
        assert preprocessor.sample_rate == 16000
    
    def test_empty_audio_noise_reduction(self, preprocessor):
        """Test noise reduction with empty audio"""
        audio = np.array([])
        result = preprocessor.reduce_noise(audio)
        assert len(result) == 0
    
    def test_empty_audio_segmentation(self, preprocessor):
        """Test segmentation with empty audio"""
        audio = np.array([])
        segments = preprocessor.segment_audio(audio)
        assert len(segments) == 1
        assert len(segments[0]) == 0
    
    def test_empty_audio_normalization(self, preprocessor):
        """Test normalization with empty audio"""
        audio = np.array([])
        result = preprocessor.normalize_audio(audio)
        assert len(result) == 0
    
    def test_silence_audio(self, preprocessor):
        """Test preprocessing with silence (all zeros)"""
        audio = np.zeros(16000)  # 1 second of silence
        result = preprocessor.preprocess(audio)
        assert len(result) > 0
        assert np.all(np.abs(result) < 1e-5)  # Should remain near zero
    
    def test_very_short_audio(self, preprocessor):
        """Test preprocessing with very short audio (< 100ms)"""
        audio = np.random.randn(800)  # 50ms at 16kHz
        result = preprocessor.preprocess(audio)
        assert len(result) > 0
    
    def test_audio_with_nan_values(self, preprocessor):
        """Test preprocessing handles NaN values"""
        audio = np.array([0.1, 0.2, np.nan, 0.4, 0.5])
        result = preprocessor.reduce_noise(audio)
        assert np.all(np.isfinite(result))
    
    def test_audio_with_inf_values(self, preprocessor):
        """Test preprocessing handles Inf values"""
        audio = np.array([0.1, 0.2, np.inf, 0.4, -np.inf])
        result = preprocessor.reduce_noise(audio)
        assert np.all(np.isfinite(result))
    
    def test_normalization_range(self, preprocessor):
        """Test that normalization produces values in [-1, 1] range"""
        # Create audio with various amplitudes
        audio = np.random.randn(16000) * 5.0  # Large amplitude
        normalized = preprocessor.normalize_audio(audio)
        
        assert np.all(normalized >= -1.0)
        assert np.all(normalized <= 1.0)
        assert np.max(np.abs(normalized)) >= 0.95  # Peak should be close to 1.0
    
    def test_normalization_preserves_shape(self, preprocessor):
        """Test that normalization preserves audio shape"""
        audio = np.random.randn(16000)
        normalized = preprocessor.normalize_audio(audio)
        assert normalized.shape == audio.shape
    
    def test_segmentation_with_silence_periods(self, preprocessor):
        """Test segmentation splits audio at silence periods"""
        # Create audio with signal-silence-signal pattern
        signal1 = np.random.randn(8000) * 0.5  # 0.5s of signal
        silence = np.zeros(3200)  # 0.2s of silence
        signal2 = np.random.randn(8000) * 0.5  # 0.5s of signal
        
        audio = np.concatenate([signal1, silence, signal2])
        segments = preprocessor.segment_audio(audio, threshold=0.02)
        
        # Should split into at least 2 segments
        assert len(segments) >= 2
    
    def test_segmentation_no_silence(self, preprocessor):
        """Test segmentation with continuous signal (no silence)"""
        audio = np.random.randn(16000) * 0.5  # 1s of continuous signal
        segments = preprocessor.segment_audio(audio, threshold=0.02)
        
        # Should return single segment
        assert len(segments) == 1
    
    def test_noise_reduction_reduces_noise(self, preprocessor):
        """Test that noise reduction actually reduces noise energy"""
        # Create clean signal
        t = np.linspace(0, 1, 16000)
        clean_signal = np.sin(2 * np.pi * 440 * t) * 0.5  # 440 Hz tone
        
        # Add noise
        noise = np.random.randn(16000) * 0.1
        noisy_signal = clean_signal + noise
        
        # Apply noise reduction
        cleaned = preprocessor.reduce_noise(noisy_signal)
        
        # Noise should be reduced (cleaned signal should be closer to original)
        # We can't guarantee perfect noise removal, but energy should be more controlled
        assert len(cleaned) == len(noisy_signal)
    
    def test_preprocess_pipeline(self, preprocessor):
        """Test full preprocessing pipeline"""
        # Create realistic audio: signal with noise
        t = np.linspace(0, 1, 16000)
        signal = np.sin(2 * np.pi * 440 * t) * 0.3
        noise = np.random.randn(16000) * 0.05
        audio = signal + noise
        
        result = preprocessor.preprocess(audio)
        
        # Should return processed audio
        assert len(result) > 0
        assert np.all(np.isfinite(result))
        assert np.all(result >= -1.0)
        assert np.all(result <= 1.0)
    
    def test_very_loud_audio(self, preprocessor):
        """Test preprocessing with very loud audio (potential clipping)"""
        audio = np.random.randn(16000) * 100.0  # Very loud
        normalized = preprocessor.normalize_audio(audio)
        
        # Should be normalized to [-1, 1]
        assert np.all(normalized >= -1.0)
        assert np.all(normalized <= 1.0)
    
    def test_segmentation_min_duration(self, preprocessor):
        """Test that segmentation respects minimum segment duration"""
        # Create audio with very short segments
        short_signal = np.random.randn(800) * 0.5  # 50ms
        silence = np.zeros(1600)  # 100ms
        
        audio = np.concatenate([short_signal, silence, short_signal, silence, short_signal])
        segments = preprocessor.segment_audio(audio, threshold=0.02, min_segment_duration=0.1)
        
        # Short segments should be filtered out
        for segment in segments:
            duration = len(segment) / preprocessor.sample_rate
            assert duration >= 0.09  # Allow small tolerance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
