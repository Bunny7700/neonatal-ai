import cv2
import numpy as np
import time

class MotionDetector:
    def __init__(self):
        self.last_movement_time = time.time()
        
        # Dense Optical Flow memory
        self.prev_gray = None
        
        # Micro-movement (breathing) history
        self.motion_history = []
        self.breathing_rate = 0
        self.breathing_status = "NORMAL"
        self.last_breath_calc = time.time()
        
        # Clinical Thresholds (Aligned with AOP Criteria)
        self.STILL_LIMIT = 20  # Diagnostic apnea duration
        self.MONITOR_LIMIT = 10 # Short apnea monitoring start
        
        # Calibration / Smoothing
        self.motion_ema = 0.0 # Exponential Moving Average
        self.noise_floor = 1.2 # Adaptive threshold
        self.frame_history = []

        
    def process_frame(self, image_bytes):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None: return None

            # 1. Preprocessing for Optical Flow
            # Resize for performance and normalize
            small_frame = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            # CLAHE to equalize lighting across the image
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            # 2. Dense Optical Flow (Farneback)
            if self.prev_gray is None:
                self.prev_gray = gray
                return None

            flow = cv2.calcOpticalFlowFarneback(
                self.prev_gray, gray, None, 
                pyr_scale=0.5, levels=3, winsize=15, 
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0
            )
            
            # 3. ADAPTIVE NOISE CALIBRATION
            # Measure local variance to detect sensor "snow" or compression artifacts
            diff = cv2.absdiff(self.prev_gray, gray)
            std_dev = np.std(diff)
            self.noise_floor = max(1.2, std_dev * 0.8) # Adjust floor based on camera quality
            
            self.prev_gray = gray

            # Extract magnitude of motion
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            # 4. Filter out noise (adaptive thresholding)
            significant_movement = magnitude > self.noise_floor

            
            # Average significant movement across the frame
            current_score = np.sum(magnitude[significant_movement]) / (magnitude.size)
            
            # Apply Smoothing (EMA) for biological signals
            alpha = 0.4
            self.motion_ema = (alpha * current_score) + ((1 - alpha) * self.motion_ema)
            
            # 5. Breathing History (capture rhythmic data)
            self.motion_history.append(self.motion_ema)
            if len(self.motion_history) > 150: # Increased window (~7-8s)
                self.motion_history.pop(0)

            # 6. Movement Logic - HIGH SENSITIVITY
            # Dense optical flow is highly robust to light shifts
            is_moving = self.motion_ema > 0.3
            
            if is_moving:
                self.last_movement_time = time.time()

            # 7. Periodic Breathing Analysis
            if time.time() - self.last_breath_calc > 1.5:
                self._analyze_rhythm()
                self.last_breath_calc = time.time()

            still_time = int(time.time() - self.last_movement_time)
            
            # 8. Status Logic
            if still_time >= self.STILL_LIMIT:
                status = "UNSAFE"
            elif still_time >= self.MONITOR_LIMIT or self.breathing_status in ["SLOW", "IRREGULAR"]:
                status = "WARNING"
            elif still_time > 5:
                status = "STILL"
            else:
                status = "SAFE"

            return self._build_response(float(self.motion_ema * 50), still_time, status) # Scaled up EMA for UI
            
        except Exception as e:
            print(f"Motion/Optical Flow Error: {e}")
            return None

    def _analyze_rhythm(self):
        if len(self.motion_history) < 10: return # Reduced threshold to 10 for prototype demo
        
        data = np.array(self.motion_history)
        
        # 1. Signal Smoothing (Low-pass filter to remove micro-jitter)
        # Using a moving average convolution to simulate a smooth respiratory wave
        window_size = 5
        smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
        
        mean_val = np.mean(smoothed)
        std_val = np.std(smoothed)
        
        # Peak Detection over Optical Flow magnitude
        peaks = 0
        threshold = mean_val + (0.1 * std_val) # Adjusted threshold for smoothed data
        
        if std_val > 0.002: # Detect macro-variations (chest movement)
            last_peak_idx = -10
            for i in range(1, len(smoothed) - 1):
                if smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1] and smoothed[i] > threshold:
                    # 2. Peak Debouncing: Prevent double-counting a single breath cycle
                    # At 3Hz, 3 frames = ~1 second (Max neonatal HR is ~60BPM)
                    if (i - last_peak_idx) >= 3:
                        peaks += 1
                        last_peak_idx = i
        
        # Calculate BPM
        # At 3Hz (333ms), window duration is len(smoothed) * 0.33
        interval = 0.33
        window_duration_seconds = len(smoothed) * interval
        
        # KEY CLINICAL FIX: Optical flow magnitude measures speed of movement.
        # One complete breath cycle (inhale -> pause -> exhale -> pause) creates TWO peaks in movement speed.
        # Therefore, we divide the raw peaks by 2 to get the actual breathing rhythm.
        actual_breaths = peaks / 2 
        raw_bpm = (actual_breaths / window_duration_seconds) * 60
        
        # 3. Output Stabilization
        if not hasattr(self, 'stable_bpm'):
            self.stable_bpm = raw_bpm
        else:
            self.stable_bpm = (0.2 * raw_bpm) + (0.8 * self.stable_bpm) # EMA smoothing
            
        self.breathing_rate = int(self.stable_bpm)
        
        # SENSE CHECK: If motion is extremely low, breathing is likely ABSENT
        if std_val <= 0.002: self.breathing_rate = 0

        
        # Clinical status logic
        if self.breathing_rate == 0:
            still_time = time.time() - self.last_movement_time
            if still_time > 10:
                self.breathing_status = "BREATHING PAUSE" # Apnea risk
            else:
                self.breathing_status = "IRREGULAR"
        elif self.breathing_rate < 30:
            self.breathing_status = "BRADYPNEA (SLOW)"
        elif self.breathing_rate > 60:
            self.breathing_status = "TACHYPNEA (RAPID)"
        else:
            self.breathing_status = "NORMAL (30-60 BPM)"

    def get_still_status(self):
        still_time = int(time.time() - self.last_movement_time)
        status = "SAFE"
        if still_time >= self.STILL_LIMIT: status = "UNSAFE"
        elif still_time >= self.MONITOR_LIMIT: status = "WARNING"
        
        return {
            "stillTime": int(still_time),
            "status": str(status),
            "breathingRate": int(self.breathing_rate),
            "breathingStatus": str(self.breathing_status),
            "motion": float(self.motion_ema * 50),
            "confidence": 95 if still_time < 5 else 85,
            "alertActive": bool(status in ["UNSAFE", "WARNING"])
        }

    def _build_response(self, motion, still_time, status):
         confidence = 98
         if still_time > 5: confidence = 90
         if still_time > 15: confidence = 70
         
         return {
            "motion": round(float(motion), 2),
            "stillTime": int(still_time),
            "status": str(status),
            "breathingRate": int(self.breathing_rate),
            "breathingStatus": str(self.breathing_status),
            "confidence": int(confidence),
            "alertActive": bool(status in ["UNSAFE", "WARNING"])
        }
