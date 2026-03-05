import cv2
import numpy as np

class FaceDetector:
    def __init__(self):
        # Load pre-trained Haar cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        self.last_face_rect = None
        self.face_movement_ema = 0.0
        self.frames_since_last_face = 0 # Memory buffer for flickering
        
    def detect(self, image_bytes):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return self._get_empty_result()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Enhance contrast for better detection in bad lighting
            gray = cv2.equalizeHist(gray)
            
            # Lower minNeighbors to 3 to aggressively detect faces (allows more false positives but better for demos)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(40, 40))
            
            if len(faces) == 0:
                self.frames_since_last_face += 1
                if self.frames_since_last_face > 5 and self.last_face_rect is None:
                    return self._get_empty_result()
                elif self.frames_since_last_face <= 5 and self.last_face_rect is not None:
                    # Use last known face location for a few frames to prevent flickering
                    (x, y, w, h) = self.last_face_rect
                else:
                    self.last_face_rect = None
                    return self._get_empty_result()
            else:
                self.frames_since_last_face = 0
                (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
                
            roi_gray = gray[y:y+h, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5))
            eyes_open = len(eyes) >= 1
            
            smiles = self.mouth_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=20, minSize=(10, 10))
            mouth_open = len(smiles) > 0

            movement_score = 0.0
            if self.last_face_rect is not None:
                lx, ly, lw, lh = self.last_face_rect
                movement_score = np.sqrt((x-lx)**2 + (y-ly)**2)
            
            self.last_face_rect = (x, y, w, h)
            
            alpha = 0.2
            self.face_movement_ema = (alpha * movement_score) + ((1 - alpha) * self.face_movement_ema)
            
            emotional_state = "sleeping" if not eyes_open else "calm"
            distress_level = "none"
            
            if mouth_open and self.face_movement_ema > 5.0:
                emotional_state = "fussy"
                distress_level = "mild"
            elif self.face_movement_ema > 12.0:
                emotional_state = "active"
                
            facial_movement = "minimal"
            if self.face_movement_ema > 5.0:
                facial_movement = "moderate"
            elif self.face_movement_ema > 15.0:
                facial_movement = "active"


            # --- CYANOSIS DETECTION (SKIN COLOR ANALYSIS) ---
            # Extract lip and cheek regions from the face ROI
            fh, fw = roi_gray.shape
            # Cheek ROIs (Left and Right)
            l_cheek = frame[y + int(fh*0.4):y + int(fh*0.6), x + int(fw*0.1):x + int(fw*0.3)]
            r_cheek = frame[y + int(fh*0.4):y + int(fh*0.6), x + int(fw*0.7):x + int(fw*0.9)]
            # Lip ROI
            lips_roi = frame[y + int(fh*0.7):y + int(fh*0.9), x + int(fw*0.3):x + int(fw*0.7)]
            
            cyanosis_score = 0
            if lips_roi.size > 0:
                # Calculate mean BGR values
                mean_bgr = cv2.mean(lips_roi)[:3]
                b, g, r = mean_bgr
                # Blue-to-Red ratio (Cyanosis indicator)
                # Normal skin r > b. Cyanosis b increases relative to r.
                br_ratio = b / (r + 1e-6)
                if br_ratio > 1.05: # Threshold for bluish tint
                    cyanosis_score = 1 # Potential Cyanosis
                if br_ratio > 1.2:
                    cyanosis_score = 2 # Likely Cyanosis
            
            cyanosis_status = "NORMAL"
            if cyanosis_score == 1:
                cyanosis_status = "MILD DISCOLORATION"
            elif cyanosis_score == 2:
                cyanosis_status = "CYANOSIS DETECTED"

            return {
                "faceDetected": True,
                "distressLevel": str(distress_level),
                "emotionalState": str(emotional_state),
                "facialMovement": str(facial_movement),
                "eyesOpen": bool(eyes_open),
                "mouthOpen": bool(mouth_open),
                "cyanosisStatus": cyanosis_status,
                "cyanosisScore": cyanosis_score,
                "confidence": int(90),
                "rect": [int(x), int(y), int(w), int(h)]
            }

        except Exception as e:
            print(f"Face Detection Error: {e}")
            return self._get_empty_result()

    def _get_empty_result(self):
        return {
            "faceDetected": False,
            "distressLevel": "none",
            "emotionalState": "unknown",
            "facialMovement": "none",
            "eyesOpen": False,
            "mouthOpen": False,
            "cyanosisStatus": "UNKNOWN",
            "cyanosisScore": 0,
            "confidence": 0,
            "rect": None
        }
