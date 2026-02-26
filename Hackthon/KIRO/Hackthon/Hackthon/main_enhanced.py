from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from shared_data import dashboard_data, update_dynamic_vitals
import threading
import time
from contextlib import asynccontextmanager

# Import AI Models
try:
    from motion_detection import MotionDetector
except ImportError as e:
    print(f"⚠️  Motion detection disabled: {e}")
    MotionDetector = None
except Exception as e:
    print(f"⚠️  Motion detection disabled (numpy/opencv issue): {e}")
    MotionDetector = None

# Use enhanced cry detector (Python 3.14 compatible)
try:
    from cry_detection_enhanced import CryDetector
    print("✅ Using Enhanced Cry Detector (Python 3.14 compatible)")
except ImportError as e:
    print(f"Error importing CryDetector: {e}")
    CryDetector = None

# Global instances
motion_detector = None
cry_detector = None

# Background thread for Cry Detection
def run_cry_detection():
    global cry_detector
    if not CryDetector:
        print("CryDetector not found. Skipping.")
        return

    print("🚀 Starting Bio-Acoustic Monitoring...")
    if cry_detector is None:
        cry_detector = CryDetector()
    
    while True:
        try:
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
            
            # Sleep for 2 seconds between detections
            time.sleep(2)
                
        except Exception as e:
            print(f"Cry Loop Error: {e}")
            time.sleep(1)

def add_alert(level, message):
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
    return dashboard_data

@app.post("/api/process_frame")
async def process_frame(file: UploadFile = File(...)):
    global motion_detector
    
    if MotionDetector is None:
        return {"status": "disabled", "message": "Motion detection unavailable (numpy/opencv issue)"}
    
    if motion_detector is None:
        try:
            motion_detector = MotionDetector()
        except Exception as e:
            return {"status": "error", "message": f"Failed to initialize motion detector: {e}"}
    
    try:
        contents = await file.read()
        data = motion_detector.process_frame(contents)
        
        if data:
            dashboard_data["motionMonitoring"].update({
                "status": data["status"],
                "stillTime": data["stillTime"],
                "motion": data["motion"],
                "confidence": data["confidence"],
                "alertActive": data["status"] == "UNSAFE"
            })
            
            if data["status"] == "UNSAFE":
                add_alert("critical", "Prolonged stillness detected!")
                
        return {"status": "processed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"status": "System Online", "mode": "Enhanced (Python 3.14 Compatible)"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting server on http://127.0.0.1:{port}")
    print("📊 Dashboard API: http://127.0.0.1:{port}/api/dashboard")
    uvicorn.run(app, host="127.0.0.1", port=port)
