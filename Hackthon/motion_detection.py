import cv2
import numpy as np
import time

class MotionDetector:
    def __init__(self):
        self.prev_gray = None
        self.last_movement_time = time.time()
        self.smoothed_motion = 0.0
        self.ALPHA = 0.25 # Smoothing for the signal
        
        # Breathing Analysis
        self.motion_history = []
        self.breathing_rate = 0
        self.breathing_status = "NORMAL"
        self.avg_intensity = 0
        self.last_breath_calc = time.time()
        
        # Thresholds tuned for micro-movement (breathing)
        self.MOVEMENT_PIXEL_THRESHOLD = 50 
        self.MIN_MOTION_AREA = 100 
        self.SIGNIFICANT_MOTION_THRESHOLD = 2000 
        self.LIGHTING_CHANGE_THRESHOLD = 15000 

    def process_frame(self, image_bytes):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None: return None

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (160, 160))
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if self.prev_gray is None:
                self.prev_gray = gray
                self.last_movement_time = time.time()
                return self._build_response(0, 0, "SAFE")

            diff = cv2.absdiff(self.prev_gray, gray)
            _, thresh = cv2.threshold(diff, self.MOVEMENT_PIXEL_THRESHOLD, 255, cv2.THRESH_BINARY)
            motion_pixels = cv2.countNonZero(thresh)
            
            # Help user tune sensitivity
            if motion_pixels > 500: # Only log significant-ish motion
                print(f"DEBUG: Current Motion: {motion_pixels} (Threshold: {self.SIGNIFICANT_MOTION_THRESHOLD})")
            
            if motion_pixels > self.LIGHTING_CHANGE_THRESHOLD:
                self.prev_gray = gray
                return self.get_still_status()

            if motion_pixels < self.MIN_MOTION_AREA:
                motion_pixels = 0

            self.smoothed_motion = (self.ALPHA * motion_pixels + (1 - self.ALPHA) * self.smoothed_motion)
            
            self.motion_history.append(self.smoothed_motion)
            if len(self.motion_history) > 100: self.motion_history.pop(0)

            if time.time() - self.last_breath_calc > 3:
                self._calculate_breathing()
                self.last_breath_calc = time.time()

            if motion_pixels > self.SIGNIFICANT_MOTION_THRESHOLD: 
                self.last_movement_time = time.time()

            still_time = int(time.time() - self.last_movement_time)
            
            # Clinical Status Logic
            if still_time >= 20:
                status = "UNSAFE"
            elif self.breathing_status != "NORMAL":
                status = "WARNING"
            elif still_time > 12:
                status = "STILL"
            else:
                status = "SAFE"

            self.prev_gray = gray
            return self._build_response(self.smoothed_motion, still_time, status)
            
        except Exception as e:
            print(f"Breathing Logic Error: {e}")
            return None

    def _calculate_breathing(self):
        if len(self.motion_history) < 40: return
        
        peaks = 0
        peak_amplitudes = []
        mean_val = np.mean(self.motion_history)
        
        for i in range(1, len(self.motion_history) - 1):
            # Detect peaks with relative amplitude check
            if (self.motion_history[i] > self.motion_history[i-1] and 
                self.motion_history[i] > self.motion_history[i+1] and 
                self.motion_history[i] > mean_val * 1.15):
                peaks += 1
                peak_amplitudes.append(self.motion_history[i])
        
        self.breathing_rate = peaks * 8 # Approx BPM
        self.avg_intensity = np.mean(peak_amplitudes) if peak_amplitudes else 0
        
        # Comprehensive Logic for slow or small breathing
        if self.breathing_rate > 0 and self.breathing_rate < 30:
            self.breathing_status = "SLOW" # Bradypnea
        elif self.breathing_rate > 0 and self.avg_intensity < 200:
            self.breathing_status = "SHALLOW" # Weak signal
        else:
            self.breathing_status = "NORMAL"

    def get_still_status(self):
        still_time = int(time.time() - self.last_movement_time)
        
        if still_time >= 20:
            status = "UNSAFE"
        elif self.breathing_status != "NORMAL":
            status = "WARNING"
        elif still_time > 12:
            status = "STILL"
        else:
            status = "SAFE"
            
        return {
            "stillTime": still_time,
            "status": status,
            "breathingStatus": self.breathing_status,
            "confidence": 98 if still_time < 12 else (70 if still_time < 20 else 30),
            "alertActive": status == "UNSAFE" or status == "WARNING"
        }

    def _build_response(self, motion, still_time, status):
         return {
            "motion": round(float(motion), 2),
            "stillTime": still_time,
            "status": status,
            "breathingRate": self.breathing_rate if status == "SAFE" or status == "WARNING" else 0,
            "breathingStatus": self.breathing_status,
            "confidence": 98 if still_time < 12 else (70 if still_time < 20 else 30),
            "mode": "SINGLE-BABY-BREATHING-CORE"
        }
