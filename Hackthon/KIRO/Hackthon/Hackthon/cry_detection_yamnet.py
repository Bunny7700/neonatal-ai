# cry_detection_yamnet.py
"""
Enhanced Cry Detection System using modular architecture

This module integrates the following components:
- AudioPreprocessor: Noise reduction, segmentation, normalization
- FeatureExtractor: Comprehensive audio feature extraction
- CryClassifier: Multi-class cry classification with confidence scoring
- AlertManager: Rich alert generation with visual indicators
- FeedbackSystem: Caregiver feedback collection for model improvement

Maintains backward compatibility with existing return format.

Requirements: 1.1, 1.3, 1.4, 2.4, 8.2, 11.1, 11.2, 11.3, 11.4
"""

import numpy as np
import sounddevice as sd
import time
from typing import Dict, Any, Optional

# Import modular components
from audio_preprocessor import AudioPreprocessor
from feature_extractor import FeatureExtractor
from cry_classifier import CryClassifier
from alert_manager import AlertManager
from feedback_system import FeedbackSystem
from privacy_logger import get_privacy_logger, verify_no_raw_audio_in_dict
from battery_manager import BatteryManager, PowerMode


class CryDetector:
    """
    Enhanced cry detector using modular architecture.
    
    Pipeline: Audio Capture → Preprocessing → Feature Extraction → 
              Classification → Alert Generation
    
    Maintains backward compatibility with existing detect() interface.
    """
    
    def __init__(self):
        """Initialize all sub-components and audio capture settings."""
        print("🔊 Initializing Enhanced Cry Detection System...")
        
        # Audio capture settings
        self.sample_rate = 16000
        self.last_cry_time = time.time()
        
        # Initialize privacy logger
        self.privacy_logger = get_privacy_logger()
        self.privacy_logger.logger.info("Cry Detection System initializing with privacy safeguards")
        
        # Initialize battery manager
        print("   - Loading BatteryManager...")
        self.battery_manager = BatteryManager(
            reduced_sampling_threshold=15.0,
            low_power_threshold=5.0,
            check_interval=60.0
        )
        
        # Initialize modular components
        try:
            print("   - Loading AudioPreprocessor...")
            self.preprocessor = AudioPreprocessor(sample_rate=self.sample_rate)
            
            print("   - Loading FeatureExtractor...")
            self.feature_extractor = FeatureExtractor(sample_rate=self.sample_rate, n_mfcc=13)
            
            print("   - Loading CryClassifier...")
            self.classifier = CryClassifier()
            
            print("   - Loading AlertManager...")
            self.alert_manager = AlertManager()
            
            print("   - Loading FeedbackSystem...")
            self.feedback_system = FeedbackSystem(storage_path="./feedback_data")
            
            print("✅ Enhanced Cry Detection System initialized successfully")
            print("   - Modular architecture: Ready")
            print("   - Classification: 5 categories")
            print("   - Privacy: Raw audio disposal enabled")
            print("   - Privacy logging: Active")
            print("   - Battery management: Enabled")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize all components: {e}")
            print("   Falling back to basic detection mode")
            # Set components to None to indicate fallback mode
            self.preprocessor = None
            self.feature_extractor = None
            self.classifier = None
            self.alert_manager = None
            self.feedback_system = None

    def record_audio(self, duration: float = 1.0) -> Optional[np.ndarray]:
        """
        Capture audio from microphone.
        
        Args:
            duration: Recording duration in seconds (default: 1.0)
            
        Returns:
            Audio signal as numpy array, or None if capture fails
            
        Validates: Requirements 1.1, 1.3, 1.4, 9.2, 9.3
        """
        try:
            # Adjust duration based on battery level
            adjusted_duration = self.battery_manager.get_audio_duration(duration)
            
            audio = sd.rec(
                int(adjusted_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocking=True
            )
            audio_flat = audio.flatten()
            
            # Log audio capture for privacy audit
            self.privacy_logger.log_audio_capture(
                audio_size=len(audio_flat),
                duration=adjusted_duration
            )
            
            return audio_flat
        except Exception as e:
            print(f"❌ Audio capture error: {e}")
            return None

    def detect(self) -> Dict[str, Any]:
        """
        Main detection method - full pipeline with modular architecture.
        
        Pipeline stages:
        1. Battery Check: Update power mode and check if processing should be skipped
        2. Audio Capture: Record audio from microphone
        3. Preprocessing: Noise reduction, segmentation, normalization
        4. Feature Extraction: Extract acoustic features
        5. Classification: Classify cry type with confidence scoring
        6. Alert Generation: Generate rich alerts with visual indicators
        7. Privacy: Dispose of raw audio data
        
        Returns:
            Dictionary with detection results (backward compatible format):
            - cryType: Cry category (hunger, sleep_discomfort, pain_distress, 
                      diaper_change, normal_unknown, or error)
            - confidence: Confidence score (0-100)
            - isCrying: Boolean indicating if crying was detected
            - silentTime: Seconds since last cry detected
            - timestamp: Detection timestamp
            - alert: Alert data (if crying detected)
            - features: Extracted features (for debugging/feedback)
            - batteryStatus: Battery and power management status
            
        Validates: Requirements 1.1, 1.3, 1.4, 2.4, 8.2, 9.2, 9.3, 11.1, 11.2, 11.3, 11.4
        """
        try:
            # Stage 0: Battery Management
            # Update power mode based on battery level
            power_mode = self.battery_manager.update_power_mode()
            
            # Check if we should skip processing to save battery
            if self.battery_manager.should_skip_processing():
                # Return minimal result without processing
                return {
                    "cryType": "skipped",
                    "confidence": 0,
                    "isCrying": False,
                    "silentTime": int(time.time() - self.last_cry_time),
                    "timestamp": time.time(),
                    "alert": None,
                    "features": {},
                    "detectionConfidence": 0,
                    "batteryStatus": self.battery_manager.get_status(),
                    "skipped": True,
                    "reason": "Low battery - processing skipped to conserve power"
                }
            
            # Check for low battery notification
            battery_notification = self.battery_manager.notify_low_battery()
            if battery_notification:
                print(battery_notification)
            
            # Check if components are initialized
            if self.preprocessor is None or self.classifier is None:
                result = self._fallback_detect()
                result["batteryStatus"] = self.battery_manager.get_status()
                return result
            
            # Stage 1: Audio Capture
            audio = self.record_audio()
            if audio is None:
                result = self._error_result("Audio capture failed")
                result["batteryStatus"] = self.battery_manager.get_status()
                return result
            
            # Stage 2: Preprocessing
            try:
                preprocessed_audio = self.preprocessor.preprocess(audio)
            except Exception as e:
                print(f"⚠️ Preprocessing error: {e}")
                # Continue with raw audio if preprocessing fails
                preprocessed_audio = audio
            
            # Stage 3: Feature Extraction
            try:
                features = self.feature_extractor.extract_all_features(preprocessed_audio)
                
                # Verify no raw audio in features (privacy check)
                if not verify_no_raw_audio_in_dict(features):
                    self.privacy_logger.log_privacy_violation(
                        "FEATURE_EXTRACTION",
                        "Raw audio detected in feature vector"
                    )
                else:
                    self.privacy_logger.log_feature_extraction(
                        feature_count=len(features),
                        has_raw_audio=False
                    )
                    
            except Exception as e:
                print(f"❌ Feature extraction error: {e}")
                result = self._error_result("Feature extraction failed")
                result["batteryStatus"] = self.battery_manager.get_status()
                return result
            
            # Stage 4: Classification
            try:
                classification = self.classifier.predict(preprocessed_audio, features)
            except Exception as e:
                print(f"❌ Classification error: {e}")
                result = self._error_result("Classification failed")
                result["batteryStatus"] = self.battery_manager.get_status()
                return result
            
            # Stage 5: Alert Generation
            alert = None
            if classification['is_crying']:
                try:
                    # Convert intensity from dB to 0-100 scale
                    intensity_db = features.get('intensity', -40)
                    intensity_normalized = max(0, min(100, (intensity_db + 40) * 2.5))
                    
                    alert = self.alert_manager.generate_alert(
                        cry_type=classification['cry_type'],
                        confidence=classification['confidence'],
                        intensity=intensity_normalized,
                        duration=features.get('duration', 0.0)
                    )
                    
                    # Add battery warning to alert if in low power mode
                    if power_mode == PowerMode.LOW_POWER or power_mode == PowerMode.REDUCED_SAMPLING:
                        if alert and battery_notification:
                            alert['battery_warning'] = battery_notification
                    
                except Exception as e:
                    print(f"⚠️ Alert generation error: {e}")
                    alert = None
                
                # Update last cry time
                self.last_cry_time = time.time()
            
            # Calculate silent time
            silent_time = int(time.time() - self.last_cry_time)
            
            # Stage 6: Privacy - Dispose of raw audio data
            # Explicitly delete audio arrays to ensure privacy (Requirement 8.2)
            try:
                del audio
                del preprocessed_audio
                self.privacy_logger.log_audio_disposal("post_classification", success=True)
            except Exception as e:
                self.privacy_logger.log_audio_disposal("post_classification", success=False)
                self.privacy_logger.log_privacy_violation(
                    "AUDIO_DISPOSAL",
                    f"Failed to dispose audio: {e}"
                )
            
            # Verify result doesn't contain raw audio before returning
            result = {
                "cryType": classification['cry_type'],
                "confidence": round(classification['confidence'], 2),
                "isCrying": classification['is_crying'],
                "silentTime": silent_time,
                "timestamp": time.time(),
                "alert": alert,
                "features": features,
                "detectionConfidence": round(classification.get('detection_confidence', 0), 2),
                "batteryStatus": self.battery_manager.get_status()
            }
            
            # Privacy check on result
            if not verify_no_raw_audio_in_dict(result):
                self.privacy_logger.log_privacy_violation(
                    "RESULT_VALIDATION",
                    "Raw audio detected in detection result"
                )
            
            # Return result in backward-compatible format
            return result
        
        except Exception as e:
            print(f"❌ Cry detection error: {e}")
            result = self._error_result(str(e))
            result["batteryStatus"] = self.battery_manager.get_status()
            return result
    
    def _fallback_detect(self) -> Dict[str, Any]:
        """
        Fallback detection method when modular components are not available.
        
        Uses simple audio energy-based detection without classification.
        
        Returns:
            Basic detection result
        """
        try:
            audio = self.record_audio()
            if audio is None:
                return self._error_result("Audio capture failed")
            
            # Simple energy-based detection
            rms = np.sqrt(np.mean(audio ** 2))
            is_crying = rms > 0.01
            confidence = min(95.0, rms * 1000) if is_crying else rms * 500
            
            if is_crying:
                self.last_cry_time = time.time()
            
            silent_time = int(time.time() - self.last_cry_time)
            
            # Dispose of raw audio
            try:
                del audio
                self.privacy_logger.log_audio_disposal("fallback_mode", success=True)
            except Exception as e:
                self.privacy_logger.log_audio_disposal("fallback_mode", success=False)
            
            return {
                "cryType": "normal_unknown" if is_crying else "none",
                "confidence": round(confidence, 2),
                "isCrying": is_crying,
                "silentTime": silent_time,
                "timestamp": time.time(),
                "alert": None,
                "features": {},
                "detectionConfidence": round(confidence, 2)
            }
        
        except Exception as e:
            print(f"❌ Fallback detection error: {e}")
            return self._error_result(str(e))
    
    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """
        Generate error result in backward-compatible format.
        
        Args:
            error_msg: Error message string
            
        Returns:
            Error result dictionary
        """
        return {
            "cryType": "error",
            "confidence": 0,
            "isCrying": False,
            "silentTime": 0,
            "timestamp": time.time(),
            "alert": None,
            "features": {},
            "detectionConfidence": 0,
            "error": error_msg
        }
    
    def submit_feedback(self, predicted_type: str, actual_type: str, 
                       features: Optional[Dict[str, Any]] = None,
                       confidence: float = 0.0) -> bool:
        """
        Allow caregiver to provide feedback on predictions.
        
        This method enables continuous learning by collecting caregiver
        corrections. Only features and labels are stored (no raw audio).
        
        Args:
            predicted_type: Model's original prediction
            actual_type: Caregiver's correction
            features: Extracted features (optional, uses last detection if None)
            confidence: Original confidence score
            
        Returns:
            True if feedback was successfully recorded, False otherwise
            
        Validates: Requirements 6.1, 6.2, 6.3, 8.3
        """
        if self.feedback_system is None:
            print("⚠️ Feedback system not available")
            return False
        
        try:
            # Privacy check: verify no raw audio in features
            features_to_store = features or {}
            if not verify_no_raw_audio_in_dict(features_to_store):
                self.privacy_logger.log_privacy_violation(
                    "FEEDBACK_STORAGE",
                    "Attempted to store raw audio in feedback"
                )
                self.privacy_logger.log_feedback_storage(has_raw_audio=True)
                return False
            
            self.privacy_logger.log_feedback_storage(has_raw_audio=False)
            
            return self.feedback_system.record_feedback(
                features=features_to_store,
                predicted_type=predicted_type,
                actual_type=actual_type,
                confidence=confidence
            )
        except Exception as e:
            print(f"❌ Feedback submission error: {e}")
            return False
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get summary of collected feedback data.
        
        Returns:
            Dictionary with feedback statistics
        """
        if self.feedback_system is None:
            return {"total_entries": 0}
        
        try:
            return self.feedback_system.get_feedback_summary()
        except Exception as e:
            print(f"❌ Error getting feedback summary: {e}")
            return {"total_entries": 0, "error": str(e)}
    
    def get_privacy_statistics(self) -> Dict[str, Any]:
        """
        Get privacy audit statistics.
        
        Returns:
            Dictionary with privacy statistics including:
            - audio_captured: Number of audio captures
            - audio_disposed: Number of successful disposals
            - features_extracted: Number of feature extractions
            - privacy_violations: Number of violations detected
            - disposal_rate: Percentage of audio properly disposed
            
        Validates: Requirements 8.1, 8.2
        """
        return self.privacy_logger.get_statistics()
    
    def get_battery_status(self) -> Dict[str, Any]:
        """
        Get current battery and power management status.
        
        Returns:
            Dictionary with battery status information
            
        Validates: Requirements 9.2, 9.3
        """
        return self.battery_manager.get_status()
    
    def print_privacy_summary(self) -> None:
        """
        Print privacy audit summary to console.
        
        Validates: Requirements 8.1, 8.2
        """
        self.privacy_logger.print_summary()