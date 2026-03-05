from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from shared_data import dashboard_data, update_dynamic_vitals
import threading
import time
import asyncio
from contextlib import asynccontextmanager

# Import AI Models
try:
    from motion_detection import MotionDetector
except ImportError as e:
    print(f"Error importing MotionDetector: {e}")
    MotionDetector = None

try:
    from cry_detection_yamnet import CryDetector
except ImportError as e:
    print(f"Error importing CryDetector: {e}")
    CryDetector = None

try:
    from face_detection import FaceDetector
except ImportError as e:
    print(f"Error importing FaceDetector: {e}")
    FaceDetector = None

# Global instances
motion_detector = None
cry_detector = None
face_detector = None
camera_enabled = True # Track camera status on backend

def add_alert(level, message, source="System Monitor"):
    # Only add alerts if camera/monitoring is enabled
    if not camera_enabled:
        return
        
    # Prevent duplicate alerts for the same event in a short window
    current_time = time.strftime("%H:%M:%S")
    for alert in dashboard_data["alerts"]:
        if alert["message"] == message and (alert["timestamp"] == "Just now" or alert["timestamp"] == current_time):
            return
            
    dashboard_data["alerts"].insert(0, {
        "type": level,
        "message": message,
        "source": source,
        "timestamp": current_time
    })
    dashboard_data["alerts"] = dashboard_data["alerts"][:15] # Increase log history

def add_event(type, description):
    dashboard_data["events"].insert(0, {
        "time": time.strftime("%H:%M"),
        "type": type,
        "description": description
    })
    dashboard_data["events"] = dashboard_data["events"][:10]

def calculate_consensus_phi():
    """ 
    NEOGUARD UNIFIED RISK ENGINE
    Formula: Risk = (SpO2 score × 0.30) + (RR score × 0.30) + (Skin score × 0.20) + (Temp score × 0.15) + (Lab flag × 0.05)
    Values: 100 = Healthy, 0 = Critical
    """
    global motion_detector, face_detector
    
    phi = 100
    
    mm = dashboard_data["motionMonitoring"]
    fa = dashboard_data["faceAnalysis"]
    lab = dashboard_data["labReports"]
    
    # Extract Vitals
    hr = next((v["value"] for v in dashboard_data["vitals"] if v["title"] == "Heart Rate"), 140)
    rr = next((v["value"] for v in dashboard_data["vitals"] if v["title"] == "Respiratory Rate"), 45)
    spo2 = next((v["value"] for v in dashboard_data["vitals"] if v["title"] == "Oxygen Saturation"), 98)
    temp = next((v["value"] for v in dashboard_data["vitals"] if v["title"] == "Body Temp"), 36.8)
    
    # 1. SpO2 (30%) - Critical emergency threshold < 90%
    if spo2 < 85: phi -= 30
    elif spo2 < 90: phi -= 20
    elif spo2 < 95: phi -= 5
    
    # 2. Breathing Rate (30%) - Normal 30-60 bpm
    if rr > 60 or rr < 30: phi -= 20
    if mm.get("stillTime", 0) >= 20: phi -= 30 # Apnea threshold
    
    # 3. Skin Color (20%) - Cyanosis / Pallor
    cyanosis_score = fa.get("cyanosisScore", 0)
    if cyanosis_score >= 2: phi -= 20
    elif cyanosis_score == 1: phi -= 10
    
    # 4. Temperature (15%) - Hypothermia < 36.0 or Fever > 37.5
    if temp < 36.0 or temp > 37.5: phi -= 15
    elif temp < 36.5: phi -= 5
    
    # 5. Lab Reports (5%) - Secondary confirmation
    if lab["status"] == "abnormal": phi -= 5
    
    phi = max(5, phi)
    
    # AOP OVERRIDE: 20s pause OR 10s pause + bradycardia (<100) or desat (<85)
    apnea_duration = mm.get("stillTime", 0)
    if apnea_duration >= 20 or (apnea_duration >= 10 and (hr < 100 or spo2 < 85)):
        phi = min(phi, 30) # Force high alert
        add_alert("critical", "AOP PROTOCOL: Clinical intervention required.", source="Risk Engine")

    # Update global risk indicators
    dashboard_data["riskAssessment"]["phi"] = int(phi)
    if phi < 40:
        dashboard_data["riskAssessment"]["overall"] = "high"
        dashboard_data["patient"]["status"] = "CRITICAL"
    elif phi < 75:
        dashboard_data["riskAssessment"]["overall"] = "medium"
        dashboard_data["patient"]["status"] = "MONITORING"
    else:
        dashboard_data["riskAssessment"]["overall"] = "low"
        dashboard_data["patient"]["status"] = "STABLE"
        
    return phi


@asynccontextmanager
async def lifespan(app: FastAPI):
    global motion_detector, face_detector
    # Initialize NeoGuard engines
    if MotionDetector:
        motion_detector = MotionDetector()
    if FaceDetector:
        face_detector = FaceDetector()
        
    # Lab sync simulation
    def simulate_lab_polling():
        while True:
            time.sleep(30)
            update_dynamic_vitals()
            
    threading.Thread(target=simulate_lab_polling, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard")
def get_dashboard():
    # Update stillness time and monitoring status
    if motion_detector:
        if camera_enabled:
            # We explicitly update from the last movement time to ensure "stillTime"
            # increases even between processed frames or during total stillness.
            still_status = motion_detector.get_still_status()
            dashboard_data["motionMonitoring"].update(still_status)
            
            # Recalculate PHI with Consensus Logic
            calculate_consensus_phi()
            
            # Auto-alert patterns
            if still_status["status"] == "UNSAFE":
                add_alert("critical", "Prolonged stillness period detected!", source="Motion AI")
            elif still_status["breathingStatus"] == "SLOW":
                add_alert("warning", "Bradypnea (Slow Breathing) pattern!", source="Motion AI")
        else:
            dashboard_data["motionMonitoring"].update({
                "status": "SAFE",
                "stillTime": 0,
                "motion": 0,
                "breathingRate": 0,
                "breathingStatus": "NORMAL",
                "alertActive": False
            })

            
    return dashboard_data

@app.post("/api/camera_status")
async def update_camera_status(status: dict):
    global camera_enabled
    camera_enabled = status.get("enabled", True)
    
    if not camera_enabled:
        # Reset movement timer on backend immediately when camera is turned off
        if motion_detector:
            motion_detector.last_movement_time = time.time()
            
        # Immediately reset dashboard states when camera is disabled
        dashboard_data["motionMonitoring"].update({
            "status": "SAFE",
            "stillTime": 0,
            "motion": 0,
            "breathingRate": 0,
            "breathingStatus": "NORMAL",
            "alertActive": False
        })
        
        dashboard_data["cryDetection"].update({
            "status": "normal",
            "cryType": "Monitoring Paused",
            "intensity": 0,
            "duration": 0,
            "confidence": 0,
            "lastDetected": "None"
        })
        
        # Clear active alerts when camera is disabled (stops the alarm)
        dashboard_data["alerts"] = [] 
        
    return {"status": "updated", "camera_enabled": camera_enabled}

@app.post("/api/process_frame")
async def process_frame(file: UploadFile = File(...)):
    global motion_detector, face_detector
    if motion_detector is None:
        motion_detector = MotionDetector()
    if face_detector is None and FaceDetector:
        face_detector = FaceDetector()
    
    # If camera is disabled, skip processing
    if not camera_enabled:
        return {"status": "skipped", "reason": "camera_disabled"}

    contents = await file.read()
    data = motion_detector.process_frame(contents)
    
    if data:
        dashboard_data["motionMonitoring"].update({
            "status": data["status"],
            "stillTime": data["stillTime"],
            "motion": data["motion"],
            "breathingRate": data.get("breathingRate", 0),
            "breathingStatus": data.get("breathingStatus", "NORMAL"),
            "confidence": data["confidence"],
            "alertActive": data["status"] in ["UNSAFE", "WARNING"]
        })
        
        if data["status"] == "UNSAFE":
            add_alert("critical", "Stillness Threshold Exceeded", source="Motion AI")
        elif data.get("breathingStatus") == "SLOW":
            add_alert("warning", "Low respiratory variability", source="Motion AI")
        elif data.get("breathingStatus") == "SHALLOW":
            add_alert("warning", "Shallow breath depth detected", source="Motion AI")

    # Perform Face Analysis concurrently
    if face_detector:
        face_data = face_detector.detect(contents)
        if face_data:
            dashboard_data["faceAnalysis"].update({
                "faceDetected": face_data["faceDetected"],
                "distressLevel": face_data["distressLevel"],
                "emotionalState": face_data["emotionalState"],
                "facialMovement": face_data["facialMovement"],
                "eyesOpen": face_data["eyesOpen"],
                "mouthOpen": face_data["mouthOpen"],
                "cyanosisStatus": face_data.get("cyanosisStatus", "NORMAL"),
                "cyanosisScore": face_data.get("cyanosisScore", 0),
                "confidence": face_data["confidence"]
            })
            
            # Sync with Breathing Analysis section for UI consistency
            dashboard_data["breathingAnalysis"].update({
                "rate": dashboard_data["motionMonitoring"]["breathingRate"],
                "status": dashboard_data["motionMonitoring"]["breathingStatus"],
                "pattern": "Pause" if dashboard_data["motionMonitoring"]["breathingStatus"] == "BREATHING PAUSE" else "Regular"
            })
            
            # If face is missing for more than 5s while camera is ON, it might be a positioning warning
            # (In a real app we'd add logic here)
            
    return {"status": "processed"}

@app.post("/api/generate_report")
def generate_accuracy_report():
    face_conf = dashboard_data["faceAnalysis"].get("confidence", 92)
    motion_conf = dashboard_data["motionMonitoring"].get("confidence", 98)
    phi_conf = dashboard_data["riskAssessment"].get("confidence", 96)
    
    avg_accuracy = (face_conf + motion_conf + phi_conf) // 3
    
    msg = f"Accuracy Diagnostics Report: System Precision {avg_accuracy}%. Spectral Vision: {face_conf}%, Respiratory Tracking: {motion_conf}%, Consensus Engine: {phi_conf}%."
    
    add_alert("info", msg, source="Diagnostic Engine")
    return {"status": "Report Generated", "accuracy": avg_accuracy}

@app.get("/")
def read_root():
    return {"status": "System Online"}

@app.post("/api/test_alert")
def trigger_test_alert():
    add_alert("critical", "SYS-Override: Test Alert Triggered. Vitals unstable.")
    dashboard_data["motionMonitoring"]["status"] = "UNSAFE"
    dashboard_data["motionMonitoring"]["alertActive"] = True
    dashboard_data["faceAnalysis"]["distressLevel"] = "severe"
    dashboard_data["faceAnalysis"]["faceDetected"] = True
    dashboard_data["faceAnalysis"]["emotionalState"] = "crying"
    dashboard_data["faceAnalysis"]["mouthOpen"] = True
    dashboard_data["patient"]["status"] = "CRITICAL"
    dashboard_data["riskAssessment"]["overall"] = "high"
    return {"status": "Critical simulation active"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
