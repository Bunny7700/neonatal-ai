from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    from feedback_system import FeedbackSystem
except ImportError as e:
    print(f"Error importing FeedbackSystem: {e}")
    FeedbackSystem = None

# Global instances
motion_detector = None
cry_detector = None
feedback_system = None

# Store last features for feedback
last_detection_features = None
last_detection_result = None

# Background thread for Cry Detection
def run_cry_detection():
    global cry_detector, last_detection_features, last_detection_result
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
            
            # Store last detection for feedback
            last_detection_result = result
            if 'features' in result:
                last_detection_features = result['features']
            
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
    global feedback_system
    # Initialize feedback system
    if FeedbackSystem:
        feedback_system = FeedbackSystem()
        print("✅ Feedback system initialized")
    
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

# Pydantic model for feedback request
class FeedbackRequest(BaseModel):
    predicted_type: str
    actual_type: str

@app.get("/api/dashboard")
def get_dashboard():
    return dashboard_data

@app.post("/api/process_frame")
async def process_frame(file: UploadFile = File(...)):
    global motion_detector
    if motion_detector is None:
        motion_detector = MotionDetector()
    
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

@app.get("/")
def read_root():
    return {"status": "System Online"}

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit caregiver feedback for cry classification.
    
    This endpoint allows caregivers to confirm or correct the system's
    cry type predictions, enabling continuous model improvement.
    
    Requirements: 6.1, 6.2, 6.3
    """
    global feedback_system, last_detection_features, last_detection_result
    
    # Validate feedback system is available
    if not feedback_system:
        raise HTTPException(
            status_code=503,
            detail="Feedback system not available"
        )
    
    # Validate cry types
    valid_types = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']
    if feedback.predicted_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid predicted_type. Must be one of: {', '.join(valid_types)}"
        )
    if feedback.actual_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid actual_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Check if we have recent detection data
    if not last_detection_features or not last_detection_result:
        raise HTTPException(
            status_code=400,
            detail="No recent detection data available for feedback"
        )
    
    # Get confidence from last detection
    confidence = last_detection_result.get('confidence', 0)
    
    try:
        # Record feedback with features
        success = feedback_system.record_feedback(
            features=last_detection_features,
            predicted_type=feedback.predicted_type,
            actual_type=feedback.actual_type,
            confidence=confidence,
            timestamp=time.time()
        )
        
        if success:
            return {
                "status": "success",
                "message": "Feedback recorded successfully",
                "feedback": {
                    "predicted_type": feedback.predicted_type,
                    "actual_type": feedback.actual_type,
                    "confidence": confidence,
                    "timestamp": time.time()
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to store feedback"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error recording feedback: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="127.0.0.1", port=port)
