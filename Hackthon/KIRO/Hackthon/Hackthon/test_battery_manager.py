# test_battery_manager.py
"""
Unit tests for Battery Management Module

Tests battery level detection, power mode transitions, and power-saving features.

Requirements: 9.2, 9.3
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from battery_manager import BatteryManager, PowerMode


class TestBatteryManager:
    """Test suite for BatteryManager class."""
    
    def test_initialization_with_defaults(self):
        """Test BatteryManager initializes with default thresholds."""
        manager = BatteryManager()
        
        assert manager.reduced_sampling_threshold == 15.0
        assert manager.low_power_threshold == 5.0
        assert manager.check_interval == 60.0
        assert manager.current_mode == PowerMode.NORMAL
    
    def test_initialization_with_custom_thresholds(self):
        """Test BatteryManager initializes with custom thresholds."""
        manager = BatteryManager(
            reduced_sampling_threshold=20.0,
            low_power_threshold=10.0,
            check_interval=30.0
        )
        
        assert manager.reduced_sampling_threshold == 20.0
        assert manager.low_power_threshold == 10.0
        assert manager.check_interval == 30.0
    
    def test_get_battery_level_unavailable(self):
        """Test battery level when battery detection is unavailable."""
        manager = BatteryManager()
        manager.battery_available = False
        
        level = manager.get_battery_level()
        
        assert level is None
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    @patch('battery_manager.BatteryManager.is_plugged_in')
    def test_update_power_mode_normal(self, mock_plugged, mock_battery):
        """Test power mode stays NORMAL when battery is sufficient."""
        mock_plugged.return_value = False
        mock_battery.return_value = 50.0
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.last_check_time = 0  # Force update
        
        mode = manager.update_power_mode()
        
        assert mode == PowerMode.NORMAL
        assert manager.current_mode == PowerMode.NORMAL
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    @patch('battery_manager.BatteryManager.is_plugged_in')
    def test_update_power_mode_reduced_sampling(self, mock_plugged, mock_battery):
        """Test power mode switches to REDUCED_SAMPLING when battery < 15%."""
        mock_plugged.return_value = False
        mock_battery.return_value = 12.0
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.last_check_time = 0  # Force update
        
        mode = manager.update_power_mode()
        
        assert mode == PowerMode.REDUCED_SAMPLING
        assert manager.current_mode == PowerMode.REDUCED_SAMPLING
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    @patch('battery_manager.BatteryManager.is_plugged_in')
    def test_update_power_mode_low_power(self, mock_plugged, mock_battery):
        """Test power mode switches to LOW_POWER when battery < 5%."""
        mock_plugged.return_value = False
        mock_battery.return_value = 3.0
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.last_check_time = 0  # Force update
        
        mode = manager.update_power_mode()
        
        assert mode == PowerMode.LOW_POWER
        assert manager.current_mode == PowerMode.LOW_POWER
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    @patch('battery_manager.BatteryManager.is_plugged_in')
    def test_update_power_mode_plugged_in_overrides(self, mock_plugged, mock_battery):
        """Test that plugged in status overrides low battery."""
        mock_plugged.return_value = True
        mock_battery.return_value = 3.0  # Very low battery
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.last_check_time = 0  # Force update
        
        mode = manager.update_power_mode()
        
        # Should be NORMAL because plugged in
        assert mode == PowerMode.NORMAL
        assert manager.current_mode == PowerMode.NORMAL
    
    def test_update_power_mode_battery_unavailable(self):
        """Test power mode when battery detection is unavailable."""
        manager = BatteryManager()
        manager.battery_available = False
        manager.last_check_time = 0  # Force update
        
        mode = manager.update_power_mode()
        
        assert mode == PowerMode.UNKNOWN
        assert manager.current_mode == PowerMode.UNKNOWN
    
    def test_get_sampling_frequency_normal(self):
        """Test sampling frequency in NORMAL mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.NORMAL
        
        freq = manager.get_sampling_frequency(1.0)
        
        assert freq == 1.0  # 100% of base frequency
    
    def test_get_sampling_frequency_reduced(self):
        """Test sampling frequency in REDUCED_SAMPLING mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.REDUCED_SAMPLING
        
        freq = manager.get_sampling_frequency(1.0)
        
        assert freq == 0.5  # 50% of base frequency
    
    def test_get_sampling_frequency_low_power(self):
        """Test sampling frequency in LOW_POWER mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.LOW_POWER
        
        freq = manager.get_sampling_frequency(1.0)
        
        assert freq == 0.25  # 25% of base frequency
    
    def test_get_audio_duration_normal(self):
        """Test audio duration in NORMAL mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.NORMAL
        
        duration = manager.get_audio_duration(1.0)
        
        assert duration == 1.0  # 100% of base duration
    
    def test_get_audio_duration_reduced(self):
        """Test audio duration in REDUCED_SAMPLING mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.REDUCED_SAMPLING
        
        duration = manager.get_audio_duration(1.0)
        
        assert duration == 0.75  # 75% of base duration
    
    def test_get_audio_duration_low_power(self):
        """Test audio duration in LOW_POWER mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.LOW_POWER
        
        duration = manager.get_audio_duration(1.0)
        
        assert duration == 0.5  # 50% of base duration
    
    def test_should_skip_processing_normal(self):
        """Test that processing is not skipped in NORMAL mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.NORMAL
        
        # Should never skip in NORMAL mode
        for _ in range(10):
            assert manager.should_skip_processing() is False
    
    def test_should_skip_processing_reduced(self):
        """Test that processing is not skipped in REDUCED_SAMPLING mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.REDUCED_SAMPLING
        
        # Should never skip in REDUCED_SAMPLING mode
        for _ in range(10):
            assert manager.should_skip_processing() is False
    
    def test_should_skip_processing_low_power(self):
        """Test that processing is sometimes skipped in LOW_POWER mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.LOW_POWER
        
        # In LOW_POWER mode, should skip ~75% of the time
        # Run 100 times and check that some are skipped
        skip_count = sum(1 for _ in range(100) if manager.should_skip_processing())
        
        # Should skip between 60-90% (allowing for randomness)
        assert 60 <= skip_count <= 90
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    def test_get_status(self, mock_battery):
        """Test get_status returns complete status information."""
        mock_battery.return_value = 45.0
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.current_mode = PowerMode.NORMAL
        
        status = manager.get_status()
        
        assert status['battery_available'] is True
        assert status['battery_level'] == 45.0
        assert status['power_mode'] == 'normal'
        assert status['sampling_frequency_multiplier'] == 1.0
        assert 'thresholds' in status
        assert status['thresholds']['reduced_sampling'] == 15.0
        assert status['thresholds']['low_power'] == 5.0
    
    def test_notify_low_battery_normal(self):
        """Test no notification in NORMAL mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.NORMAL
        manager.last_battery_level = 50.0
        
        notification = manager.notify_low_battery()
        
        assert notification is None
    
    def test_notify_low_battery_reduced_sampling(self):
        """Test notification in REDUCED_SAMPLING mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.REDUCED_SAMPLING
        manager.last_battery_level = 12.0
        
        notification = manager.notify_low_battery()
        
        assert notification is not None
        assert "12.0%" in notification
        assert "Reduced sampling" in notification
    
    def test_notify_low_battery_low_power(self):
        """Test notification in LOW_POWER mode."""
        manager = BatteryManager()
        manager.current_mode = PowerMode.LOW_POWER
        manager.last_battery_level = 3.0
        
        notification = manager.notify_low_battery()
        
        assert notification is not None
        assert "3.0%" in notification
        assert "CRITICAL" in notification
        assert "low-power mode" in notification
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    @patch('battery_manager.BatteryManager.is_plugged_in')
    def test_battery_threshold_boundary_15_percent(self, mock_plugged, mock_battery):
        """Test exact threshold at 15% battery."""
        mock_plugged.return_value = False
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.last_check_time = 0
        
        # Test at exactly 15% - should be NORMAL (>= 15%)
        mock_battery.return_value = 15.0
        mode = manager.update_power_mode()
        assert mode == PowerMode.NORMAL
        
        # Test just below 15% - should be REDUCED_SAMPLING
        manager.last_check_time = 0
        mock_battery.return_value = 14.9
        mode = manager.update_power_mode()
        assert mode == PowerMode.REDUCED_SAMPLING
    
    @patch('battery_manager.BatteryManager.get_battery_level')
    @patch('battery_manager.BatteryManager.is_plugged_in')
    def test_battery_threshold_boundary_5_percent(self, mock_plugged, mock_battery):
        """Test exact threshold at 5% battery."""
        mock_plugged.return_value = False
        
        manager = BatteryManager()
        manager.battery_available = True
        manager.last_check_time = 0
        
        # Test at exactly 5% - should be REDUCED_SAMPLING (>= 5%)
        mock_battery.return_value = 5.0
        mode = manager.update_power_mode()
        assert mode == PowerMode.REDUCED_SAMPLING
        
        # Test just below 5% - should be LOW_POWER
        manager.last_check_time = 0
        mock_battery.return_value = 4.9
        mode = manager.update_power_mode()
        assert mode == PowerMode.LOW_POWER


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
