from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from shared_data import dashboard_data
import threading
import time
import asyncio
from contextlib import asynccontextmanager

# Import AI Models (Lazy loading or direct)
# Import AI Models (Lazy loading or direct)
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

# Background thread for Cry Detection
def run_cry_detection():
    global cry_detector
    if not CryDetector:
        print("CryDetector not found. Skipping.")
        return

    print("🚀 Starting Cry Detection Loop...")
    if cry_detector is None:
        cry_detector = CryDetector()
    
    while True:
        try:
            # This is blocking for ~1 second
            result = cry_detector.detect()
            
            # Update shared data
            dashboard_data["cryDetection"].update({
                "status": "distress" if result["isCrying"] else "normal",
                "cryType": result["cryType"],
                "confidence": result["confidence"],
                "duration": result["silentTime"],
                "lastDetected": f"{result['silentTime']}s ago" if not result['isCrying'] else "Now"
            })
            
            if result["isCrying"]:
                add_alert("warning", f"Cry detected: {result['cryType']}")
                
        except Exception as e:
            print(f"Cry Loop Error: {e}")
            time.sleep(1)

def add_alert(level, message):
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
    # Only start CryDetection (Audio) in background
    # Motion detection is now Event-Driven by frontend frames
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

from fastapi import File, UploadFile

@app.post("/api/process_frame")
async def process_frame(file: UploadFile = File(...)):
    global motion_detector
    if motion_detector is None:
        motion_detector = MotionDetector()
    
    contents = await file.read()
    # print(f"Received frame of size: {len(contents)}") # Debug
    data = motion_detector.process_frame(contents)
    
    if data:
        # print(f"Processed Frame: {data}") # Debug
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

@app.get("/")
def read_root():
    return {"status": "System Online", "endpoints": ["/api/dashboard", "/api/process_frame"]}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
