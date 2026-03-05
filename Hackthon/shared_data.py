# shared_data.py
import random

# This structure matches the Frontend's expected data format
dashboard_data = {
    # Motion monitoring from OpenCV backend
    "motionMonitoring": {
        "status": "SAFE",  # SAFE / MONITOR / ALERT
        "stillTime": 0,
        "motion": 0.0,
        "breathingRate": 45,
        "breathingStatus": "NORMAL",
        "confidence": 98,
        "alertActive": False
    },
    
    # Skin Color & Cyanosis Detection (NeoGuard Vision AI)
    "faceAnalysis": {
        "faceDetected": True,
        "cyanosisStatus": "NORMAL",
        "cyanosisScore": 0,
        "pallorLevel": "none",
        "jaundiceScore": 0,
        "confidence": 92
    },
    
    # Lab Report Integration ( HMIS/LIS Sync )
    "labReports": {
        "lastUpdate": "Mar 05, 10:30",
        "status": "normal",
        "panels": [
            { "name": "ABG (PaO2)", "value": "62", "unit": "mmHg", "status": "normal" },
            { "name": "CRP", "value": "8", "unit": "mg/L", "status": "normal" },
            { "name": "Bilirubin", "value": "4.2", "unit": "mg/dL", "status": "normal" },
            { "name": "Glucose", "value": "4.1", "unit": "mmol/L", "status": "normal" }
        ]
    },
    
    # Patient Demographic Chart
    "patient": {
        "id": "NG-2026-0821",
        "age": "2 days old",
        "weight": "1.85 kg",
        "gestationalAge": "32 weeks",
        "admissionDate": "Mar 03, 2026",
        "status": "Stable",
        "ward": "NICU WARD 4"
    },
    
    "aiStatus": [
        { "title": "Breathing AI", "value": "3Hz Tracking", "confidence": 96, "note": "RGB Fusion", "status": "normal" },
        { "title": "Skin Spectrum", "value": "Trichromatic", "confidence": 92, "note": "Cyanosis Check", "status": "normal" },
        { "title": "Body Temp", "value": "36.8 °C", "confidence": 98, "note": "IRT Fusion", "status": "normal" }
    ],
    
    "vitals": [
        { "title": "Heart Rate", "value": 142, "unit": "bpm", "normalRange": "120-160", "status": "normal" },
        { "title": "Respiratory Rate", "value": 45, "unit": "breaths/min", "normalRange": "30-60", "status": "normal" },
        { "title": "Oxygen Saturation", "value": 98, "unit": "%", "normalRange": "95-100", "status": "normal" },
        { "title": "Body Temp", "value": 36.8, "unit": "°C", "normalRange": "36.5-37.5", "status": "normal" }
    ],
    
    "alerts": [],
    
    "riskAssessment": {
        "overall": "low",
        "phi": 100,
        "confidence": 96,
        "categories": [
            { "name": "Respiratory (30%)", "level": "Low", "color": "#10b981" },
            { "name": "Oxygenation (30%)", "level": "Low", "color": "#10b981" },
            { "name": "Skin Specs (20%)", "level": "Low", "color": "#10b981" },
            { "name": "Thermal (15%)", "level": "Low", "color": "#10b981" },
            { "name": "Lab Results (5%)", "level": "Low", "color": "#10b981" }
        ]
    },
    
    "breathingAnalysis": {
        "rate": 45,
        "status": "NORMAL",
        "pattern": "Regular"
    },
    "events": [
        { "time": "Now", "type": "info", "description": "NeoGuard System Active - Non-Contact Mode" }
    ]
}

def update_dynamic_vitals():
    # Simulate clinical variability for NeoGuard (5-param model)
    is_apnea = dashboard_data["motionMonitoring"]["breathingStatus"] == "BREATHING PAUSE"
    still_time = dashboard_data["motionMonitoring"]["stillTime"]

    for vital in dashboard_data["vitals"]:
        if vital["title"] == "Heart Rate":
            # AOP Criteria: HR < 100 during apnea
            if is_apnea and still_time > 10:
                vital["value"] = random.randint(75, 95)
                vital["status"] = "critical"
            else:
                vital["value"] = random.randint(135, 155)
                vital["status"] = "normal"
        
        elif vital["title"] == "Respiratory Rate":
            if is_apnea:
                vital["value"] = 0
                vital["status"] = "critical"
            else:
                vital["value"] = random.randint(35, 58) # Normal 30-60
                vital["status"] = "normal"
                
        elif vital["title"] == "Oxygen Saturation":
            # Hypoxaemia Thresholds: <90% (Urgent), <85% (Critical)
            if is_apnea and still_time > 15:
                vital["value"] = random.randint(78, 88) 
                vital["status"] = "critical"
            else:
                vital["value"] = random.randint(96, 99)
                vital["status"] = "normal"

        elif vital["title"] == "Body Temp":
            # Normal: 36.5-37.5. <36.0 is critical hypothermia.
            if is_apnea and still_time > 18:
                vital["value"] = round(random.uniform(35.8, 36.2), 1)
                vital["status"] = "warning"
            else:
                vital["value"] = round(random.uniform(36.6, 37.2), 1)
                vital["status"] = "normal"

    # Sync AI Status cards
    for ai in dashboard_data["aiStatus"]:
        if ai["title"] == "Body Temp":
            curr_temp = next(v["value"] for v in dashboard_data["vitals"] if v["title"] == "Body Temp")
            ai["value"] = f"{curr_temp} °C"
            ai["status"] = "normal" if 36.5 <= curr_temp <= 37.5 else "warning"

    # Global Risk Assessment
    calculate_consensus_phi()

def calculate_consensus_phi():
    # PHI (Patient Health Index) starts at 100
    phi = 100
    
    # Check Respiratory Rate
    rr = next(v["value"] for v in dashboard_data["vitals"] if v["title"] == "Respiratory Rate")
    if rr < 30 or rr > 60:
        phi -= 20
        
    # Check Heart Rate
    hr = next(v["value"] for v in dashboard_data["vitals"] if v["title"] == "Heart Rate")
    if hr < 110 or hr > 170:
        phi -= 25
        
    # Check Oxygen
    spo2 = next(v["value"] for v in dashboard_data["vitals"] if v["title"] == "Oxygen Saturation")
    if spo2 < 90:
        phi -= 30
    elif spo2 < 94:
        phi -= 10
        
    # Check Skin Color
    if dashboard_data["faceAnalysis"]["cyanosisScore"] >= 1:
        phi -= 15
        
    # Check Stillness
    if dashboard_data["motionMonitoring"]["stillTime"] >= 20:
        phi -= 15
        
    dashboard_data["riskAssessment"]["phi"] = max(0, phi)
    
    # Map PHI to Overall Risk
    if phi < 40:
        dashboard_data["riskAssessment"]["overall"] = "CRITICAL"
    elif phi < 70:
        dashboard_data["riskAssessment"]["overall"] = "WARNING"
    else:
        dashboard_data["riskAssessment"]["overall"] = "NORMAL"
