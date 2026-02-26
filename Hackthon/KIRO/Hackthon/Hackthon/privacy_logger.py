# privacy_logger.py
"""
Privacy Logger for Neonatal Cry Detection System

This module provides logging and verification utilities to ensure
privacy safeguards are properly implemented:
- No raw audio transmitted over network
- Raw audio cleared from memory after processing
- Only features stored, never raw audio

Requirements: 8.1, 8.2
"""

import logging
import sys
import time
from typing import Any, Dict, Optional
import traceback


class PrivacyLogger:
    """
    Logger for privacy-related operations in the cry detection system.
    
    Tracks and verifies:
    - Audio data lifecycle (capture → processing → disposal)
    - Memory cleanup operations
    - Network transmission prevention
    - Feature storage without raw audio
    """
    
    def __init__(self, log_file: str = "privacy_audit.log"):
        """
        Initialize privacy logger.
        
        Args:
            log_file: Path to privacy audit log file
        """
        self.log_file = log_file
        
        # Configure logger
        self.logger = logging.getLogger("PrivacyLogger")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[PRIVACY] %(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for audit trail
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Statistics
        self.stats = {
            'audio_captured': 0,
            'audio_disposed': 0,
            'features_extracted': 0,
            'network_checks': 0,
            'privacy_violations': 0
        }
        
        self.logger.info("Privacy Logger initialized")
        self.logger.info(f"Audit log: {log_file}")
    
    def log_audio_capture(self, audio_size: int, duration: float) -> None:
        """
        Log audio capture event.
        
        Args:
            audio_size: Size of audio array (number of samples)
            duration: Duration in seconds
        """
        self.stats['audio_captured'] += 1
        self.logger.info(
            f"Audio captured: {audio_size} samples, {duration:.2f}s duration "
            f"(Total captures: {self.stats['audio_captured']})"
        )
    
    def log_audio_disposal(self, stage: str, success: bool = True) -> None:
        """
        Log audio disposal event.
        
        Args:
            stage: Processing stage where disposal occurred
            success: Whether disposal was successful
        """
        if success:
            self.stats['audio_disposed'] += 1
            self.logger.info(
                f"[OK] Raw audio disposed at stage: {stage} "
                f"(Total disposals: {self.stats['audio_disposed']})"
            )
        else:
            self.stats['privacy_violations'] += 1
            self.logger.error(
                f"[VIOLATION] Failed to dispose audio at stage: {stage}"
            )
    
    def log_feature_extraction(self, feature_count: int, has_raw_audio: bool = False) -> None:
        """
        Log feature extraction event.
        
        Args:
            feature_count: Number of features extracted
            has_raw_audio: Whether raw audio is present in features (should be False)
        """
        self.stats['features_extracted'] += 1
        
        if has_raw_audio:
            self.stats['privacy_violations'] += 1
            self.logger.error(
                f"[VIOLATION] Raw audio found in feature vector! "
                f"Features: {feature_count}"
            )
        else:
            self.logger.info(
                f"[OK] Features extracted without raw audio: {feature_count} features "
                f"(Total extractions: {self.stats['features_extracted']})"
            )
    
    def log_network_check(self, endpoint: str, has_audio: bool = False) -> None:
        """
        Log network transmission check.
        
        Args:
            endpoint: API endpoint being checked
            has_audio: Whether raw audio is present in transmission (should be False)
        """
        self.stats['network_checks'] += 1
        
        if has_audio:
            self.stats['privacy_violations'] += 1
            self.logger.error(
                f"[VIOLATION] Raw audio detected in network transmission to {endpoint}!"
            )
        else:
            self.logger.info(
                f"[OK] Network transmission verified safe: {endpoint} "
                f"(Total checks: {self.stats['network_checks']})"
            )
    
    def log_feedback_storage(self, has_raw_audio: bool = False) -> None:
        """
        Log feedback storage event.
        
        Args:
            has_raw_audio: Whether raw audio is present in stored data (should be False)
        """
        if has_raw_audio:
            self.stats['privacy_violations'] += 1
            self.logger.error(
                "[VIOLATION] Raw audio found in feedback storage!"
            )
        else:
            self.logger.info(
                "[OK] Feedback stored without raw audio (features only)"
            )
    
    def log_privacy_violation(self, violation_type: str, details: str) -> None:
        """
        Log a privacy violation.
        
        Args:
            violation_type: Type of violation
            details: Detailed description
        """
        self.stats['privacy_violations'] += 1
        self.logger.error(
            f"[VIOLATION] [{violation_type}]: {details}"
        )
        
        # Also log stack trace for debugging
        self.logger.debug(f"Stack trace:\n{''.join(traceback.format_stack())}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get privacy statistics.
        
        Returns:
            Dictionary with privacy statistics
        """
        return {
            **self.stats,
            'disposal_rate': (
                self.stats['audio_disposed'] / self.stats['audio_captured'] * 100
                if self.stats['audio_captured'] > 0 else 0
            ),
            'violation_rate': (
                self.stats['privacy_violations'] / 
                (self.stats['audio_captured'] + self.stats['network_checks']) * 100
                if (self.stats['audio_captured'] + self.stats['network_checks']) > 0 else 0
            )
        }
    
    def print_summary(self) -> None:
        """Print privacy audit summary."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("PRIVACY AUDIT SUMMARY")
        print("="*60)
        print(f"Audio Captured:        {stats['audio_captured']}")
        print(f"Audio Disposed:        {stats['audio_disposed']}")
        print(f"Features Extracted:    {stats['features_extracted']}")
        print(f"Network Checks:        {stats['network_checks']}")
        print(f"Privacy Violations:    {stats['privacy_violations']}")
        print(f"Disposal Rate:         {stats['disposal_rate']:.1f}%")
        print(f"Violation Rate:        {stats['violation_rate']:.1f}%")
        print("="*60)
        
        if stats['privacy_violations'] > 0:
            print("WARNING: Privacy violations detected! Review audit log.")
        else:
            print("SUCCESS: No privacy violations detected.")
        print()


def verify_no_raw_audio_in_dict(data: Dict[str, Any], path: str = "") -> bool:
    """
    Recursively verify that a dictionary does not contain raw audio data.
    
    Raw audio is typically stored as:
    - numpy arrays with dtype float32/float64
    - lists of floats representing samples
    - keys like 'audio', 'raw_audio', 'samples', 'waveform'
    
    Args:
        data: Dictionary to check
        path: Current path in nested structure (for error reporting)
        
    Returns:
        True if no raw audio found, False otherwise
    """
    import numpy as np
    
    # Forbidden keys that might contain raw audio
    forbidden_keys = ['audio', 'raw_audio', 'samples', 'waveform', 'signal', 'audio_data']
    
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key
        
        # Check for forbidden keys
        if key.lower() in forbidden_keys:
            print(f"⚠️  Found forbidden key: {current_path}")
            return False
        
        # Check for numpy arrays (potential audio data)
        if isinstance(value, np.ndarray):
            # Allow small arrays (likely features), reject large arrays (likely audio)
            if value.size > 100:  # Audio would have thousands of samples
                print(f"⚠️  Found large numpy array at {current_path}: {value.shape}")
                return False
        
        # Check for large lists of numbers (potential audio samples)
        elif isinstance(value, (list, tuple)):
            if len(value) > 100 and all(isinstance(x, (int, float)) for x in value[:10]):
                print(f"⚠️  Found large numeric list at {current_path}: {len(value)} items")
                return False
        
        # Recursively check nested dictionaries
        elif isinstance(value, dict):
            if not verify_no_raw_audio_in_dict(value, current_path):
                return False
    
    return True


# Global privacy logger instance
_privacy_logger: Optional[PrivacyLogger] = None


def get_privacy_logger() -> PrivacyLogger:
    """
    Get or create the global privacy logger instance.
    
    Returns:
        Global PrivacyLogger instance
    """
    global _privacy_logger
    if _privacy_logger is None:
        _privacy_logger = PrivacyLogger()
    return _privacy_logger
