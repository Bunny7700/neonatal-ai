# shared_data.py
import random

# This structure matches the Frontend's expected data format
dashboard_data = {
    # Motion monitoring from OpenCV backend
    "motionMonitoring": {
        "status": "SAFE",  # SAFE / MONITOR / ALERT
        "stillTime": 0,
        "motion": 0.0,
        "confidence": 98,
        "alertActive": False
    },
    
    # Cry Detection AI
    "cryDetection": {
        "status": "normal",  # normal / abnormal / distress
        "cryType": "None detected",  # hunger, pain, discomfort, none
        "intensity": 0,  # 0-100
        "duration": 0,  # seconds
        "confidence": 0,
        "lastDetected": "None",
        "audioWaveform": [0.1] * 10  # Placeholder
    },
    
    # Sleep Position Monitoring (Mock for now)
    "sleepPosition": {
        "position": "Back",
        "status": "safe",
        "riskLevel": "low",
        "timeInPosition": 12,
        "confidence": 92,
        "recommendations": "Position is optimal for breathing",
        "positionHistory": [
             { "time": "12:00", "position": "Back" }
        ]
    },
    
    # Breathing Pattern Analysis (Mock for now)
    "breathingAnalysis": {
        "rate": 42,
        "pattern": "Regular",
        "status": "normal",
        "oxygenLevel": 98,
        "confidence": 89,
        "irregularities": 0,
        "trend": "stable"
    },
    
    # Face & Distress Detection (Mock for now)
    "faceAnalysis": {
        "faceDetected": True,
        "distressLevel": "none",
        "emotionalState": "calm",
        "facialMovement": "minimal",
        "eyesOpen": False,
        "mouthOpen": False,
        "confidence": 88,
        "alerts": []
    },
    
    # Patient Info (Dynamic updates)
    "patient": {
        "id": "NB-2026-001",
        "age": "3 days old",
        "weight": "3.2 kg",
        "gestationalAge": "38 weeks",
        "admissionDate": "Jan 21, 2026",
        "status": "Stable"
    },
    
    "aiStatus": [
        { "title": "Cry Pattern", "value": "Active", "confidence": 92, "note": "Audio listening", "status": "normal" },
        { "title": "Sleep Position", "value": "Safe", "confidence": 95, "note": "Vision active", "status": "normal" },
        { "title": "Body Temperature", "value": "36.8 °C", "confidence": 98, "note": "Infrared active", "status": "normal" }
    ],
    
    "vitals": [
        { "title": "Heart Rate", "value": 142, "unit": "bpm", "normalRange": "120-160", "status": "normal" },
        { "title": "Respiratory Rate", "value": 45, "unit": "breaths/min", "normalRange": "40-60", "status": "normal" },
        { "title": "Oxygen Saturation", "value": 98, "unit": "%", "normalRange": "95-100", "status": "normal" }
    ],
    
    "alerts": [],
    
    "riskAssessment": {
        "overall": "low",
        "confidence": 94,
        "categories": [
            { "name": "Respiratory", "level": "Low", "color": "#10b981" },
            { "name": "Cardiac", "level": "Low", "color": "#10b981" },
            { "name": "Neurological", "level": "Low", "color": "#10b981" },
            { "name": "Thermal", "level": "Low", "color": "#10b981" }
        ]
    },
    
    "trainingData": [
        { "epoch": 1, "accuracy": 62, "loss": 0.92 },
        { "epoch": 2, "accuracy": 68, "loss": 0.81 },
        { "epoch": 3, "accuracy": 74, "loss": 0.69 },
        { "epoch": 4, "accuracy": 81, "loss": 0.54 },
        { "epoch": 5, "accuracy": 88, "loss": 0.38 }
    ],
    
    "events": [
        { "time": "Now", "type": "info", "description": "System Started" }
    ]
}

def update_dynamic_vitals():
    # Simulate medical variability in vitals
    for vital in dashboard_data["vitals"]:
        if vital["title"] == "Heart Rate":
            vital["value"] = random.randint(135, 155)
            vital["status"] = "normal" if 120 <= vital["value"] <= 160 else "warning"
        elif vital["title"] == "Respiratory Rate":
            vital["value"] = random.randint(40, 50)
        elif vital["title"] == "Oxygen Saturation":
            vital["value"] = random.randint(97, 99)

    # Risk assessment logic based on stability
    stability = 0
    if dashboard_data["motionMonitoring"]["status"] == "UNSAFE": stability += 1
    if dashboard_data["cryDetection"]["status"] == "distress": stability += 1
    
    if stability == 0:
        dashboard_data["riskAssessment"]["overall"] = "low"
        dashboard_data["patient"]["status"] = "Stable"
    elif stability == 1:
        dashboard_data["riskAssessment"]["overall"] = "medium"
        dashboard_data["patient"]["status"] = "Monitoring"
    else:
        dashboard_data["riskAssessment"]["overall"] = "high"
        dashboard_data["patient"]["status"] = "CRITICAL"
