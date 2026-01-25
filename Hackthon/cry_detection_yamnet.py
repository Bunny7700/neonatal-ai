# cry_detection_yamnet.py
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import time

class CryDetector:
    def __init__(self):
        print("🔊 Loading YAMNet model...")
        self.model = hub.load("https://tfhub.dev/google/yamnet/1")
        self.sample_rate = 16000
        self.last_cry_time = time.time()  # Add this for tracking
        print("✅ YAMNet loaded successfully")

    def record_audio(self, duration=1.0):
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocking=True
        )
        return audio.flatten()

    def detect(self):  # ← Changed from 'analyze' to 'detect'
        try:
            audio = self.record_audio()

            # YAMNet expects 16kHz mono
            scores, embeddings, spectrogram = self.model(audio)
            scores = scores.numpy()

            mean_scores = np.mean(scores, axis=0)
            top_index = np.argmax(mean_scores)
            confidence = float(mean_scores[top_index])

            # Improved cry detection logic
            is_crying = confidence > 0.3
            
            if confidence > 0.5:
                cry_type = "pain"
            elif confidence > 0.35:
                cry_type = "hunger"
            elif confidence > 0.25:
                cry_type = "discomfort"
            else:
                cry_type = "none"

            # Track silent time
            if is_crying:
                self.last_cry_time = time.time()
            
            silent_time = int(time.time() - self.last_cry_time)

            return {
                "cryType": cry_type,
                "confidence": round(confidence * 100, 2),
                "isCrying": is_crying,
                "silentTime": silent_time,
                "timestamp": time.time()
            }
        
        except Exception as e:
            print(f"❌ Cry detection error: {e}")
            return {
                "cryType": "error",
                "confidence": 0,
                "isCrying": False,
                "silentTime": 0,
                "timestamp": time.time()
            }