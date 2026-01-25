import cv2
import numpy as np
import time
import random

class MotionDetector:
    def __init__(self):
        # self.cap = cv2.VideoCapture(0) # Removed internal capture
        self.demo_mode = False
        self.camera_available = True
        self.prev_gray = None
        
        self.last_movement_time = time.time()
        self.smoothed_motion = 0.0
        self.ALPHA = 0.3
        # Lower threshold to make it more sensitive for testing
        self.MOVEMENT_THRESHOLD = 500 
        self.latest_jpeg = None

    def process_frame(self, image_bytes):
        try:
            # Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                print("Error: Could not decode frame")
                return None

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Use slightly larger size for better detection
            gray = cv2.resize(gray, (128, 128)) 

            if self.prev_gray is None:
                self.prev_gray = gray
                return self._build_response(0, 0, "SAFE")

            diff = cv2.absdiff(self.prev_gray, gray)
            motion = np.sum(diff)
            
            # Sensitivity tuning for PROTOTYPE
            # Use lower threshold for pixel intensity change (15 vs 25)
            _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
            motion = np.sum(thresh)
            
            # Smooth motion
            self.smoothed_motion = (
                self.ALPHA * motion + (1 - self.ALPHA) * self.smoothed_motion
            )

            # Update stillness timer using RAW motion for instant reaction
            # Threshold adjusted to detect breathing movements
            # Breathing creates motion values around 50k-200k
            # Complete stillness (no breathing) = values below 50k
            if motion > 50000: 
                self.last_movement_time = time.time()

            still_time = int(time.time() - self.last_movement_time)

            # Reduced thresholds for easier prototype demonstration
            if still_time < 3:
                status = "SAFE"
            elif still_time < 10:
                status = "MONITOR"
            else:
                status = "UNSAFE"

            self.prev_gray = gray
            
            # Debug log active
            print(f"Motion: {motion:.0f} | Still: {still_time}s | Status: {status}")

            return self._build_response(self.smoothed_motion, still_time, status)
            
        except Exception as e:
            print(f"Error in process_frame: {e}")
            return None

    def _build_response(self, motion, still_time, status):
         # Scale down motion for display if it's huge
         display_motion = min(1000, motion) 
         
         return {
            "motion": round(float(motion), 2),
            "stillTime": still_time,
            "status": status,
            "confidence": min(100, int(motion / 100)),
            "mode": "WEB-STREAM"
        }
