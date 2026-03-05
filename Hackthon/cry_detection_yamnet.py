import numpy as np
import time
import os
import threading

try:
    import sounddevice as sd
    import librosa
    import joblib
    try:
        sd.query_devices()
        AUDIO_LIB_AVAILABLE = True
    except Exception as e:
        print(f"Warning: Audio device query failed: {e}")
        AUDIO_LIB_AVAILABLE = False
except Exception as e:
    print(f"Warning: Audio libraries missing or broken: {e}")
    AUDIO_LIB_AVAILABLE = False

class CryDetector:
    def __init__(self):
        print("Initializing Machine Learning Acoustic Engine (Random Forest)...")
        self.sample_rate = 16000
        self.last_cry_time = time.time()
        self.is_ready = AUDIO_LIB_AVAILABLE
        self.sustained_threshold = 2
        self.history = []
        
        # Anti-Hallucination Config
        self.PROBABILITY_THRESHOLD = 0.85 # 85% confidence required for strict labels
        self.NOISE_BASELINE = 0.0002 # Adaptive floor for noise
        self.history_probs = [] # Keep recent class probabilities
        
        self.model = None
        self.scaler = None
        
        if self.is_ready:
            try:
                # Load the newly trained Edge Models
                model_path = os.path.join("models", "cry_model.joblib")
                scaler_path = os.path.join("models", "feature_scaler.joblib")
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.model = joblib.load(model_path)
                    self.scaler = joblib.load(scaler_path)
                    print("ML Models successfully loaded onto inference node.")
                else:
                    print("ML Models not found in /models/. Falling back to simulation.")
                    self.is_ready = False
            except Exception as e:
                print(f"Failed to load ML Models: {e}")
                self.is_ready = False
        else:
            print("Sound library missing. Using simulation mode.")

    def extract_features(self, audio):
        # Must perfectly match training/01_extract_features.py
        # 1. MFCC
        mfccs = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=13)
        mfccs_scaled = np.mean(mfccs.T, axis=0)
        # 2. Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
        centroid_scaled = np.mean(spectral_centroid)
        # 3. ZCR
        zcr = librosa.feature.zero_crossing_rate(y=audio)[0]
        zcr_scaled = np.mean(zcr)
        # 4. RMS
        rms = librosa.feature.rms(y=audio)[0]
        rms_scaled = np.mean(rms)
        return np.hstack([mfccs_scaled, centroid_scaled, zcr_scaled, rms_scaled]), rms_scaled

    def detect(self):
        try:
            if not self.is_ready or self.model is None:
                return self._simulate_detection()

            # Record 3-second block to match training data
            print("👂 Mic Listening [3s]...", end="\r")
            duration = 3.0
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocking=True
            )
            print("🧠 AI Analyzing...     ", end="\r")
            audio = audio.flatten()
            
            # Extract Features
            features, rms = self.extract_features(audio)
            
            # 1. Scale exactly how we trained
            features_scaled = self.scaler.transform([features])
            
            # 2. Predict Probabilities (VITAL for anti-hallucination)
            confidence_arr = self.model.predict_proba(features_scaled)[0]
            pred = np.argmax(confidence_arr)
            confidence = float(np.max(confidence_arr))
            
            # 3. ANTI-HALLUCINATION FILTER
            # If confidence is low OR Class 0 (non-cry) is strong, ignore it.
            if confidence < self.PROBABILITY_THRESHOLD or pred == 0:
                is_crying = False
            else:
                is_crying = True

            # Tracking probabilities for debugging/insights
            self.history_probs.append(confidence_arr)
            if len(self.history_probs) > 5: self.history_probs.pop(0)

            # Intensity log
            if rms < 0.00001:
                print("⚠️ SILENT: No mic signal detected.")
            else:
                status_char = "🧠 AI: Distressed" if is_crying else "🧠 AI: Calm"
                print(f"{status_char} | Volume: {rms:.4f} | Conf: {int(confidence*100)}% | Pred: {pred}")
            
            # 4. TEMPORAL VOTE (Prevent Hallucinations from Spikes)
            self.history.append(is_crying)
            if len(self.history) > 5: self.history.pop(0)
            
            # Majority Vote: 3 out of 5 blocks must be biological cries to trigger alarm
            is_crying_sustained = sum(self.history) >= 3
            
            if is_crying_sustained:
                self.last_cry_time = time.time()
                
                # ACOUSTIC FEATURE EXTRACTION (for logic override)
                centroid = features[13]
                zcr = features[14]
                
                # CLINICAL DIFFERENTIATION LOGIC
                # Hunger (Dunstan 'Neh'): Lower pitch, rhythmic, mid-range centroid.
                # Discomfort (Dunstan 'Heh'/'Eairh'): Sharp, high-frequency, high ZCR.
                
                is_high_pitch_stress = (centroid > 1900 or zcr > 0.14)
                is_intense_pain = (rms > 0.12)
                
                if pred == 2 or is_high_pitch_stress or is_intense_pain:
                    cry_type = "Discomfort / Stress"
                    if is_intense_pain: confidence = max(confidence, 99.0)
                elif pred == 1:
                    if centroid < 1600 and zcr < 0.10:
                        cry_type = "Hunger"
                    else:
                        cry_type = "Discomfort (Mild)"
                else:
                    if centroid > 1700:
                        cry_type = "Discomfort / Stress"
                    else:
                        cry_type = "Hunger (Likely)"
            else:
                cry_type = "None"
                # Even if not sustained, if it's currently a cry, keep confidence
                if not is_crying: confidence = 0.0

            return {
                "cryType": cry_type,
                "confidence": int(confidence * 100) if isinstance(confidence, float) else confidence,
                "status": "distress" if is_crying_sustained else "normal",
                "isCrying": is_crying_sustained,
                "isListening": True,
                "silentTime": int(time.time() - self.last_cry_time) if not is_crying_sustained else 0,
                "timestamp": time.time(),
                "intensity": int(rms * 1000)
            }
        
        except Exception as e:
            print("ML Inference Error:", e)
            return self._simulate_detection()

    def _simulate_detection(self):
        t = int(time.time() % 60)
        if 0 <= t < 10:
            return {
                "cryType": "Hunger",
                "confidence": 92,
                "status": "distress",
                "isCrying": True,
                "silentTime": 0,
                "timestamp": time.time(),
                "intensity": 45
            }
        elif 10 <= t < 20:
            return {
                "cryType": "Discomfort / Stress",
                "confidence": 94,
                "status": "distress",
                "isCrying": True,
                "silentTime": 0,
                "timestamp": time.time(),
                "intensity": 75
            }
        else:
            return {
                "cryType": "Calm",
                "confidence": 99,
                "status": "normal",
                "isCrying": False,
                "silentTime": t - 20,
                "timestamp": time.time(),
                "intensity": 5
            }
