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

# Global instances
motion_detector = None
cry_detector = None
camera_enabled = True # Track camera status on backend

# Background thread for Cry Detection
def run_cry_detection():
    global cry_detector
    if not CryDetector:
        print("CryDetector not found. Skipping.")
        return

    print("Starting Bio-Acoustic Monitoring...")
    if cry_detector is None:
        cry_detector = CryDetector()
    
    while True:
        try:
            # If camera is disabled, stop detection and alerts
            if not camera_enabled:
                dashboard_data["cryDetection"].update({
                    "status": "normal",
                    "cryType": "Disabled",
                    "confidence": 0,
                    "intensity": 0,
                    "duration": 0,
                    "lastDetected": "Camera Off"
                })
                time.sleep(1)
                continue

            # Perform detection (audio sampling)
            result = cry_detector.detect()
            
            # Update shared data
            dashboard_data["cryDetection"].update({
                "status": "distress" if result["isCrying"] else "normal",
                "cryType": result["cryType"].capitalize(),
                "confidence": result["confidence"],
                "intensity": int(result["confidence"] * 0.8) if result["isCrying"] else 0,
                "duration": result["silentTime"],
                "lastDetected": f"{result['silentTime']}s ago" if not result['isCrying'] else "Now"
            })
            
            if result["isCrying"]:
                add_alert("warning", f"Cry detected: {result['cryType']}")
            
            # Also update dynamic patient vitals in this loop
            update_dynamic_vitals()
                
        except Exception as e:
            print(f"Cry Loop Error: {e}")
            time.sleep(1)

def add_alert(level, message):
    # Only add alerts if camera/monitoring is enabled
    if not camera_enabled:
        return
        
    # Prevent duplicate alerts for the same event
    for alert in dashboard_data["alerts"]:
        if alert["message"] == message and alert["timestamp"] == "Just now":
            return
            
    dashboard_data["alerts"].insert(0, {
        "type": level,
        "message": message,
        "timestamp": "Just now"
    })
    dashboard_data["alerts"] = dashboard_data["alerts"][:5]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global motion_detector, cry_detector
    # Initialize detectors early
    if MotionDetector:
        motion_detector = MotionDetector()
    if CryDetector:
        cry_detector = CryDetector()
        
    # Start the Audio AI Monitoring thread
    t2 = threading.Thread(target=run_cry_detection, daemon=True)
    t2.start()
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
    # Update stillness time only if camera is enabled
    if motion_detector:
        if camera_enabled:
            still_data = motion_detector.get_still_status()
            dashboard_data["motionMonitoring"].update(still_data)
            
            if still_data["status"] == "UNSAFE":
                add_alert("critical", "Prolonged stillness detected!")
            elif still_data["breathingStatus"] == "SLOW":
                add_alert("warning", "Slow breathing detected (Bradypnea)!")
            elif still_data["breathingStatus"] == "SHALLOW":
                add_alert("warning", "Shallow breathing pattern detected!")
        else:
            # If camera is disabled, force safe/reset state
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
    global motion_detector
    if motion_detector is None:
        motion_detector = MotionDetector()
    
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
            add_alert("critical", "Prolonged stillness detected!")
        elif data.get("breathingStatus") == "SLOW":
            add_alert("warning", "Bradypnea (Slow Breathing)!")
        elif data.get("breathingStatus") == "SHALLOW":
            add_alert("warning", "Shallow Breathing Monitoring!")
            
    return {"status": "processed"}

@app.get("/")
def read_root():
    return {"status": "System Online"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
