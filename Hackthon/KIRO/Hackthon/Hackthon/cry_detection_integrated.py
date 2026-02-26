# cry_detection_integrated.py
"""
Integrated Cry Detection System using modular architecture
Works without numpy for Python 3.14 compatibility
"""

import time
import random
from alert_manager import AlertManager


class CryDetectorIntegrated:
    """
    Integrated cry detector using the modular architecture.
    
    This version simulates the full pipeline:
    AudioCapture → AudioPreprocessor → FeatureExtractor → CryClassifier → AlertManager
    
    Note: Uses mock implementations for Python 3.14 compatibility.
    For production with Python 3.11/3.12, replace with actual implementations.
    """
    
    def __init__(self):
        print("🔊 Initializing Integrated Cry Detection System...")
        
        # Initialize components
        self.alert_manager = AlertManager()
        self.last_cry_time = time.time()
        self.sample_rate = 16000
        
        # Cry type probabilities for realistic simulation
        self.cry_types = {
            'hunger': 0.30,
            'sleep_discomfort': 0.25,
            'pain_distress': 0.15,
            'diaper_change': 0.20,
            'normal_unknown': 0.10
        }
        
        print("✅ Integrated Cry Detector initialized")
        print("   - AlertManager: Ready")
        print("   - Classification: 5 categories")
        print("   - Mode: Simulated (Python 3.14 compatible)")
    
    def _simulate_audio_capture(self):
        """Simulate audio capture (replaces sounddevice)"""
        # In production: use sounddevice to capture real audio
        return True
    
    def _simulate_preprocessing(self):
        """Simulate audio preprocessing"""
        # In production: use AudioPreprocessor
        # - Noise reduction
        # - Segmentation
        # - Normalization
        return True
    
    def _simulate_feature_extraction(self):
        """Simulate feature extraction"""
        # In production: use FeatureExtractor
        # Returns mock features similar to real extraction
        features = {
            'pitch': random.uniform(250, 500),
            'pitch_std': random.uniform(10, 60),
            'intensity': random.uniform(-40, -15),
            'intensity_std': random.uniform(2, 10),
            'zero_crossing_rate': random.uniform(0.02, 0.15),
            'duration': random.uniform(0.5, 3.0),
            'spectral_centroid': random.uniform(300, 700),
            'spectral_rolloff': random.uniform(600, 1200)
        }
        return features
    
    def _classify_cry(self, features):
        """
        Classify cry type based on features.
        
        Uses rule-based logic similar to CryClassifier but simplified.
        """
        # Determine if crying based on intensity and duration
        is_crying = features['intensity'] > -35 and features['duration'] > 0.3
        
        if not is_crying:
            return {
                'is_crying': False,
                'cry_type': 'normal_unknown',
                'confidence': random.uniform(10, 40),
                'detection_confidence': random.uniform(20, 50)
            }
        
        # Classify cry type based on features
        scores = {
            'pain_distress': 0,
            'hunger': 0,
            'sleep_discomfort': 0,
            'diaper_change': 0,
            'normal_unknown': 20
        }
        
        # Pain/distress: High pitch, high intensity
        if features['pitch'] > 400 and features['intensity'] > -20:
            scores['pain_distress'] += 40
        if features['pitch_std'] > 50:
            scores['pain_distress'] += 20
        if features['intensity'] > -15:
            scores['pain_distress'] += 15
        
        # Hunger: Moderate pitch, rhythmic
        if 300 <= features['pitch'] <= 400 and -30 <= features['intensity'] <= -15:
            scores['hunger'] += 35
        if features['pitch_std'] < 30:
            scores['hunger'] += 20
        if features['duration'] > 1.0:
            scores['hunger'] += 15
        
        # Sleep discomfort: Variable pitch, low-moderate intensity
        if features['pitch_std'] > 40:
            scores['sleep_discomfort'] += 25
        if -40 <= features['intensity'] <= -20:
            scores['sleep_discomfort'] += 20
        if features['duration'] > 1.5:
            scores['sleep_discomfort'] += 20
        
        # Diaper change: High zero-crossing rate
        if features['zero_crossing_rate'] > 0.1:
            scores['diaper_change'] += 30
        if 250 <= features['pitch'] <= 350:
            scores['diaper_change'] += 20
        if -35 <= features['intensity'] <= -20:
            scores['diaper_change'] += 15
        
        # Find best match
        cry_type = max(scores, key=scores.get)
        confidence = min(100.0, max(0.0, scores[cry_type]))
        
        # Apply confidence threshold (< 60% → normal_unknown)
        if confidence < 60.0:
            cry_type = 'normal_unknown'
        
        return {
            'is_crying': True,
            'cry_type': cry_type,
            'confidence': confidence,
            'detection_confidence': random.uniform(70, 95)
        }
    
    def detect(self):
        """
        Main detection method - full pipeline.
        
        Returns:
            Dictionary with detection results and alert data
        """
        try:
            # Step 1: Audio Capture
            audio_captured = self._simulate_audio_capture()
            if not audio_captured:
                return self._error_result("Audio capture failed")
            
            # Step 2: Preprocessing
            preprocessed = self._simulate_preprocessing()
            if not preprocessed:
                return self._error_result("Preprocessing failed")
            
            # Step 3: Feature Extraction
            features = self._simulate_feature_extraction()
            if not features:
                return self._error_result("Feature extraction failed")
            
            # Step 4: Classification
            classification = self._classify_cry(features)
            
            # Step 5: Generate Alert using AlertManager
            if classification['is_crying']:
                alert = self.alert_manager.generate_alert(
                    cry_type=classification['cry_type'],
                    confidence=classification['confidence'],
                    intensity=features['intensity'] + 40,  # Convert to 0-100 scale
                    duration=features['duration']
                )
                self.last_cry_time = time.time()
            else:
                alert = None
            
            # Calculate silent time
            silent_time = int(time.time() - self.last_cry_time)
            
            # Return comprehensive result
            return {
                'isCrying': classification['is_crying'],
                'cryType': classification['cry_type'],
                'confidence': round(classification['confidence'], 2),
                'detectionConfidence': round(classification['detection_confidence'], 2),
                'silentTime': silent_time,
                'timestamp': time.time(),
                'features': features,
                'alert': alert,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Cry detection error: {e}")
            return self._error_result(str(e))
    
    def _error_result(self, error_msg):
        """Return error result"""
        return {
            'isCrying': False,
            'cryType': 'error',
            'confidence': 0,
            'detectionConfidence': 0,
            'silentTime': 0,
            'timestamp': time.time(),
            'features': {},
            'alert': None,
            'status': 'error',
            'error': error_msg
        }


# Alias for compatibility
CryDetector = CryDetectorIntegrated
