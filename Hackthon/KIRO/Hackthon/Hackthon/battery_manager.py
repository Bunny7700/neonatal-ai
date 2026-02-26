# battery_manager.py
"""
Battery Management Module for Neonatal Cry Detection System

This module provides battery level detection and power-saving features:
- Detects battery level using platform-specific APIs
- Reduces sampling frequency when battery < 15%
- Enters low-power mode when battery < 5%

Requirements: 9.2, 9.3
"""

import time
from typing import Dict, Any, Optional
from enum import Enum


class PowerMode(Enum):
    """Power modes for the system."""
    NORMAL = "normal"
    REDUCED_SAMPLING = "reduced_sampling"  # Battery < 15%
    LOW_POWER = "low_power"  # Battery < 5%
    UNKNOWN = "unknown"  # Battery detection unavailable


class BatteryManager:
    """
    Manages battery monitoring and power-saving features.
    
    Features:
    - Cross-platform battery level detection
    - Automatic power mode adjustment based on battery level
    - Configurable thresholds for power-saving modes
    - Graceful fallback when battery detection is unavailable
    """
    
    def __init__(self, 
                 reduced_sampling_threshold: float = 15.0,
                 low_power_threshold: float = 5.0,
                 check_interval: float = 60.0):
        """
        Initialize battery manager.
        
        Args:
            reduced_sampling_threshold: Battery % to trigger reduced sampling (default: 15%)
            low_power_threshold: Battery % to trigger low-power mode (default: 5%)
            check_interval: Seconds between battery checks (default: 60s)
        """
        self.reduced_sampling_threshold = reduced_sampling_threshold
        self.low_power_threshold = low_power_threshold
        self.check_interval = check_interval
        
        self.current_mode = PowerMode.NORMAL
        self.last_check_time = 0
        self.battery_available = False
        self.last_battery_level = None
        
        # Try to import psutil for battery detection
        try:
            import psutil
            self.psutil = psutil
            # Test if battery is available
            battery = psutil.sensors_battery()
            self.battery_available = battery is not None
            if self.battery_available:
                print("🔋 Battery monitoring enabled")
            else:
                print("⚠️ Battery monitoring unavailable (desktop/server mode)")
        except ImportError:
            print("⚠️ psutil not installed - battery monitoring disabled")
            self.psutil = None
            self.battery_available = False
        except Exception as e:
            print(f"⚠️ Battery detection error: {e}")
            self.psutil = None
            self.battery_available = False
    
    def get_battery_level(self) -> Optional[float]:
        """
        Get current battery level as percentage.
        
        Returns:
            Battery level (0-100) or None if unavailable
            
        Validates: Requirements 9.2, 9.3
        """
        if not self.battery_available or self.psutil is None:
            return None
        
        try:
            battery = self.psutil.sensors_battery()
            if battery is None:
                return None
            
            # Battery level is returned as percentage (0-100)
            self.last_battery_level = battery.percent
            return battery.percent
        except Exception as e:
            print(f"⚠️ Error reading battery level: {e}")
            return None
    
    def is_plugged_in(self) -> bool:
        """
        Check if device is plugged into power.
        
        Returns:
            True if plugged in, False if on battery, False if unknown
        """
        if not self.battery_available or self.psutil is None:
            return False
        
        try:
            battery = self.psutil.sensors_battery()
            if battery is None:
                return False
            return battery.power_plugged
        except Exception as e:
            print(f"⚠️ Error checking power status: {e}")
            return False
    
    def update_power_mode(self) -> PowerMode:
        """
        Update power mode based on current battery level.
        
        Checks battery level and adjusts power mode according to thresholds:
        - Battery < 5%: LOW_POWER mode
        - Battery < 15%: REDUCED_SAMPLING mode
        - Battery >= 15%: NORMAL mode
        - Battery unavailable: UNKNOWN mode (treated as NORMAL)
        
        Returns:
            Current power mode
            
        Validates: Requirements 9.2, 9.3
        """
        current_time = time.time()
        
        # Only check battery at specified intervals
        if current_time - self.last_check_time < self.check_interval:
            return self.current_mode
        
        self.last_check_time = current_time
        
        # If battery detection is unavailable, stay in NORMAL mode
        if not self.battery_available:
            self.current_mode = PowerMode.UNKNOWN
            return self.current_mode
        
        # If plugged in, always use NORMAL mode
        if self.is_plugged_in():
            if self.current_mode != PowerMode.NORMAL:
                print("🔌 Device plugged in - switching to NORMAL mode")
                self.current_mode = PowerMode.NORMAL
            return self.current_mode
        
        # Get current battery level
        battery_level = self.get_battery_level()
        if battery_level is None:
            # Battery detection failed, stay in current mode
            return self.current_mode
        
        # Determine power mode based on battery level
        previous_mode = self.current_mode
        
        if battery_level < self.low_power_threshold:
            # Battery < 5%: Enter low-power mode
            self.current_mode = PowerMode.LOW_POWER
            if previous_mode != PowerMode.LOW_POWER:
                print(f"⚠️ Battery critically low ({battery_level:.1f}%) - entering LOW_POWER mode")
        elif battery_level < self.reduced_sampling_threshold:
            # Battery < 15%: Reduce sampling frequency
            self.current_mode = PowerMode.REDUCED_SAMPLING
            if previous_mode != PowerMode.REDUCED_SAMPLING:
                print(f"🔋 Battery low ({battery_level:.1f}%) - entering REDUCED_SAMPLING mode")
        else:
            # Battery >= 15%: Normal operation
            self.current_mode = PowerMode.NORMAL
            if previous_mode != PowerMode.NORMAL and previous_mode != PowerMode.UNKNOWN:
                print(f"✅ Battery sufficient ({battery_level:.1f}%) - returning to NORMAL mode")
        
        return self.current_mode
    
    def get_sampling_frequency(self, base_frequency: float = 1.0) -> float:
        """
        Get adjusted sampling frequency based on power mode.
        
        Args:
            base_frequency: Base sampling frequency in Hz (default: 1.0 Hz = 1 sample/sec)
            
        Returns:
            Adjusted sampling frequency in Hz
            
        Sampling adjustments:
        - NORMAL: 100% of base frequency
        - REDUCED_SAMPLING: 50% of base frequency
        - LOW_POWER: 25% of base frequency
        - UNKNOWN: 100% of base frequency (no battery info)
        
        Validates: Requirements 9.2
        """
        mode = self.current_mode
        
        if mode == PowerMode.LOW_POWER:
            return base_frequency * 0.25  # 25% frequency
        elif mode == PowerMode.REDUCED_SAMPLING:
            return base_frequency * 0.5  # 50% frequency
        else:
            return base_frequency  # 100% frequency (NORMAL or UNKNOWN)
    
    def get_audio_duration(self, base_duration: float = 1.0) -> float:
        """
        Get adjusted audio capture duration based on power mode.
        
        In low-power modes, we can reduce the duration of audio capture
        to save processing time and battery.
        
        Args:
            base_duration: Base audio duration in seconds (default: 1.0s)
            
        Returns:
            Adjusted audio duration in seconds
            
        Duration adjustments:
        - NORMAL: 100% of base duration
        - REDUCED_SAMPLING: 75% of base duration
        - LOW_POWER: 50% of base duration
        - UNKNOWN: 100% of base duration
        
        Validates: Requirements 9.3
        """
        mode = self.current_mode
        
        if mode == PowerMode.LOW_POWER:
            return base_duration * 0.5  # 50% duration
        elif mode == PowerMode.REDUCED_SAMPLING:
            return base_duration * 0.75  # 75% duration
        else:
            return base_duration  # 100% duration
    
    def should_skip_processing(self) -> bool:
        """
        Determine if current processing cycle should be skipped for power saving.
        
        In LOW_POWER mode, we skip some processing cycles to conserve battery.
        
        Returns:
            True if processing should be skipped, False otherwise
            
        Validates: Requirements 9.3
        """
        mode = self.current_mode
        
        # In LOW_POWER mode, skip 75% of processing cycles
        if mode == PowerMode.LOW_POWER:
            import random
            return random.random() < 0.75
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current battery and power management status.
        
        Returns:
            Dictionary with status information:
            - battery_available: Whether battery detection is available
            - battery_level: Current battery percentage (or None)
            - is_plugged_in: Whether device is plugged in
            - power_mode: Current power mode
            - sampling_frequency_multiplier: Current sampling frequency multiplier
            - last_check_time: Timestamp of last battery check
        """
        battery_level = self.get_battery_level()
        
        # Calculate sampling frequency multiplier
        if self.current_mode == PowerMode.LOW_POWER:
            freq_multiplier = 0.25
        elif self.current_mode == PowerMode.REDUCED_SAMPLING:
            freq_multiplier = 0.5
        else:
            freq_multiplier = 1.0
        
        return {
            "battery_available": self.battery_available,
            "battery_level": battery_level,
            "is_plugged_in": self.is_plugged_in(),
            "power_mode": self.current_mode.value,
            "sampling_frequency_multiplier": freq_multiplier,
            "last_check_time": self.last_check_time,
            "thresholds": {
                "reduced_sampling": self.reduced_sampling_threshold,
                "low_power": self.low_power_threshold
            }
        }
    
    def notify_low_battery(self) -> Optional[str]:
        """
        Generate notification message for low battery conditions.
        
        Returns:
            Notification message string, or None if no notification needed
            
        Validates: Requirements 9.3
        """
        mode = self.current_mode
        battery_level = self.last_battery_level
        
        if mode == PowerMode.LOW_POWER and battery_level is not None:
            return f"⚠️ CRITICAL: Battery at {battery_level:.1f}% - System in low-power mode. Please charge device."
        elif mode == PowerMode.REDUCED_SAMPLING and battery_level is not None:
            return f"🔋 WARNING: Battery at {battery_level:.1f}% - Reduced sampling to conserve power."
        
        return None
