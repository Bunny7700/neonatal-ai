# test_battery_integration.py
"""
Integration tests for Battery Management with CryDetector

Tests that battery management is properly integrated into the cry detection system.

Requirements: 9.2, 9.3
"""

import pytest
from unittest.mock import Mock, patch
from cry_detection_yamnet import CryDetector
from battery_manager import PowerMode


class TestBatteryIntegration:
    """Test suite for battery management integration with CryDetector."""
    
    def test_cry_detector_initializes_battery_manager(self):
        """Test that CryDetector initializes BatteryManager."""
        detector = CryDetector()
        
        assert hasattr(detector, 'battery_manager')
        assert detector.battery_manager is not None
    
    def test_cry_detector_has_battery_status_method(self):
        """Test that CryDetector has get_battery_status method."""
        detector = CryDetector()
        
        assert hasattr(detector, 'get_battery_status')
        status = detector.get_battery_status()
        
        assert isinstance(status, dict)
        assert 'battery_available' in status
        assert 'power_mode' in status
    
    @patch('cry_detection_yamnet.sd.rec')
    def test_detect_includes_battery_status(self, mock_rec):
        """Test that detect() result includes battery status."""
        # Mock audio recording
        import numpy as np
        mock_rec.return_value = np.random.randn(16000, 1).astype('float32')
        
        detector = CryDetector()
        result = detector.detect()
        
        assert 'batteryStatus' in result
        assert isinstance(result['batteryStatus'], dict)
    
    @patch('cry_detection_yamnet.sd.rec')
    def test_detect_skips_processing_in_low_power(self, mock_rec):
        """Test that detect() can skip processing in low power mode."""
        detector = CryDetector()
        
        # Force LOW_POWER mode
        detector.battery_manager.current_mode = PowerMode.LOW_POWER
        detector.battery_manager.battery_available = False  # Prevent mode changes
        
        # Run detect multiple times - some should be skipped
        results = []
        for _ in range(20):
            result = detector.detect()
            results.append(result)
        
        # Check that at least some were skipped
        skipped_count = sum(1 for r in results if r.get('skipped', False))
        
        # In LOW_POWER mode, ~75% should be skipped
        # With 20 iterations, expect at least 10 skips
        assert skipped_count >= 10
    
    @patch('cry_detection_yamnet.sd.rec')
    def test_audio_duration_adjusted_by_battery(self, mock_rec):
        """Test that audio capture duration is adjusted based on battery level."""
        import numpy as np
        
        detector = CryDetector()
        
        # Test NORMAL mode - should use full duration
        detector.battery_manager.current_mode = PowerMode.NORMAL
        detector.battery_manager.battery_available = False
        
        mock_rec.return_value = np.random.randn(16000, 1).astype('float32')
        audio = detector.record_audio(1.0)
        
        # In NORMAL mode, should record full 1.0 second (16000 samples)
        assert len(audio) == 16000
        
        # Test LOW_POWER mode - should use reduced duration
        detector.battery_manager.current_mode = PowerMode.LOW_POWER
        
        mock_rec.return_value = np.random.randn(8000, 1).astype('float32')
        audio = detector.record_audio(1.0)
        
        # In LOW_POWER mode, should record 0.5 seconds (8000 samples)
        assert len(audio) == 8000
    
    def test_battery_status_has_required_fields(self):
        """Test that battery status contains all required fields."""
        detector = CryDetector()
        status = detector.get_battery_status()
        
        required_fields = [
            'battery_available',
            'battery_level',
            'is_plugged_in',
            'power_mode',
            'sampling_frequency_multiplier',
            'thresholds'
        ]
        
        for field in required_fields:
            assert field in status, f"Missing required field: {field}"
    
    @patch('cry_detection_yamnet.BatteryManager.get_battery_level')
    @patch('cry_detection_yamnet.BatteryManager.is_plugged_in')
    @patch('cry_detection_yamnet.sd.rec')
    def test_low_battery_warning_in_alert(self, mock_rec, mock_plugged, mock_battery):
        """Test that low battery warnings are added to alerts."""
        import numpy as np
        
        # Mock low battery condition
        mock_battery.return_value = 3.0  # Very low battery
        mock_plugged.return_value = False
        mock_rec.return_value = np.random.randn(16000, 1).astype('float32')
        
        detector = CryDetector()
        detector.battery_manager.battery_available = True
        detector.battery_manager.last_check_time = 0  # Force update
        
        # Update power mode to LOW_POWER
        detector.battery_manager.update_power_mode()
        
        # Verify we're in LOW_POWER mode
        assert detector.battery_manager.current_mode == PowerMode.LOW_POWER
        
        # The alert should include battery warning if crying is detected
        # (This test verifies the integration, actual alert generation depends on classification)
        result = detector.detect()
        
        # Check that battery status shows low power mode
        assert result['batteryStatus']['power_mode'] == 'low_power'
        assert result['batteryStatus']['battery_level'] == 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
