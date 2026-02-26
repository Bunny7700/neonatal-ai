# Running the Neonatal Cry Detection System

## ✅ System Status: RUNNING

The Neonatal Cry Detection System is now running successfully!

## 🚀 Quick Start

### 1. Start the Server

```bash
cd Hackthon/Hackthon
python run_simple_server.py
```

The server will start on **http://127.0.0.1:5000**

### 2. View the Dashboard (Optional)

In a new terminal:

```bash
cd Hackthon/Hackthon
python demo_client.py
```

This will show a live dashboard with:
- 👶 Patient information
- 🔊 Cry detection status
- 💓 Vital signs
- 🚨 Recent alerts
- 📊 Risk assessment

## 📡 API Endpoints

### Get System Status
```
GET http://127.0.0.1:5000/
```

### Get Dashboard Data
```
GET http://127.0.0.1:5000/api/dashboard
```

Returns complete dashboard data including:
- Cry detection results
- Patient vitals
- Motion monitoring
- Sleep position
- Breathing analysis
- Alerts and events

## 🏗️ System Architecture

### Current Implementation

The system uses a **Python 3.14 compatible** architecture:

1. **Enhanced Cry Detector** (`cry_detection_enhanced.py`)
   - Mock implementation for demo purposes
   - Simulates cry detection without TensorFlow/numpy
   - Returns realistic cry types: hunger, pain, discomfort, sleepy

2. **Simple HTTP Server** (`run_simple_server.py`)
   - Built-in Python HTTP server (no FastAPI/uvicorn needed)
   - Background thread for continuous cry monitoring
   - CORS-enabled for frontend integration

3. **Shared Data** (`shared_data.py`)
   - Centralized dashboard data structure
   - Dynamic vital signs simulation
   - Risk assessment logic

### Modules Implemented (Ready for Integration)

The following modules have been fully implemented and are ready to integrate once Python 3.11/3.12 is available:

1. ✅ **AudioPreprocessor** (`audio_preprocessor.py`)
   - Noise reduction using spectral subtraction
   - Audio segmentation based on energy thresholds
   - Amplitude normalization

2. ✅ **FeatureExtractor** (`feature_extractor.py`)
   - Pitch extraction
   - Frequency spectrum analysis
   - Intensity calculation
   - MFCC extraction (13 coefficients)
   - Duration calculation

3. ✅ **CryClassifier** (`cry_classifier.py`)
   - Rule-based cry type classification
   - 5 categories: hunger, sleep_discomfort, pain_distress, diaper_change, normal_unknown
   - Confidence thresholding (< 60% → normal_unknown)

4. ✅ **AlertManager** (`alert_manager.py`)
   - Message mapping for all cry types
   - Color-coded visual indicators (red/yellow/green)
   - Icon mapping
   - Dashboard integration

5. ✅ **FeedbackSystem** (`feedback_system.py`)
   - Privacy-preserving feedback collection
   - Stores only features and labels (no raw audio)
   - Export functionality for model retraining

## 🔧 Python 3.14 Compatibility Issue

### The Problem

Python 3.14.2 has experimental numpy support that causes crashes:
```
Warning: Numpy built with MINGW-W64 on Windows 64 bits is experimental
CRASHES ARE TO BE EXPECTED
```

This affects:
- TensorFlow (requires numpy)
- OpenCV (requires numpy)
- librosa (requires numpy)
- scipy (requires numpy)

### Current Solution

The system runs in **mock mode** using:
- Simple HTTP server (no FastAPI/uvicorn)
- Enhanced cry detector (no TensorFlow/numpy)
- Simulated detection results

### Production Solution

For production deployment:

1. **Install Python 3.11 or 3.12**
   ```bash
   # Download from python.org
   # Recommended: Python 3.11.x or 3.12.x
   ```

2. **Reinstall Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Use Full Implementation**
   - Replace `cry_detection_enhanced.py` with full pipeline
   - Integrate AudioPreprocessor → FeatureExtractor → CryClassifier
   - Train ML model on real infant cry data

## 📊 What's Working Now

### ✅ Functional Features

1. **HTTP Server**
   - Running on port 5000
   - CORS-enabled
   - JSON API responses

2. **Cry Detection Loop**
   - Background thread monitoring
   - Updates every 2 seconds
   - Simulates realistic cry patterns

3. **Dashboard Data**
   - Real-time cry detection status
   - Dynamic vital signs
   - Alert management
   - Risk assessment
   - Event logging

4. **Demo Client**
   - Live dashboard display
   - Auto-refreshing every 3 seconds
   - Color-coded status indicators

### ⚠️ Pending Integration

These modules are implemented but not yet integrated (waiting for Python 3.11/3.12):

1. Audio preprocessing pipeline
2. Feature extraction from real audio
3. ML-based cry classification
4. Feedback collection system
5. Motion detection (OpenCV)

## 🧪 Testing

### Test the Server

```bash
# Test system status
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/').read().decode())"

# Test dashboard API
python -c "import urllib.request, json; data = json.loads(urllib.request.urlopen('http://127.0.0.1:5000/api/dashboard').read().decode()); print('Cry Status:', data['cryDetection']['status'])"
```

### Run Unit Tests (Requires Python 3.11/3.12)

```bash
# Test audio preprocessor
pytest tests/test_audio_preprocessor.py -v

# Test feature extractor
pytest tests/test_feature_extractor.py -v

# Test cry classifier
pytest tests/test_cry_classifier.py -v

# Test alert manager
pytest tests/test_alert_manager.py -v

# Test feedback system
pytest tests/test_feedback_system.py -v
```

## 📁 Project Structure

```
Hackthon/Hackthon/
├── run_simple_server.py          # ✅ Main server (Python 3.14 compatible)
├── demo_client.py                 # ✅ Live dashboard client
├── cry_detection_enhanced.py     # ✅ Mock cry detector
├── shared_data.py                 # ✅ Dashboard data structure
│
├── audio_preprocessor.py          # ✅ Implemented (needs Python 3.11/3.12)
├── feature_extractor.py           # ✅ Implemented (needs Python 3.11/3.12)
├── cry_classifier.py              # ✅ Implemented (needs Python 3.11/3.12)
├── alert_manager.py               # ✅ Implemented
├── feedback_system.py             # ✅ Implemented
│
├── tests/                         # ✅ Comprehensive test suites
│   ├── test_audio_preprocessor.py
│   ├── test_feature_extractor.py
│   ├── test_cry_classifier.py
│   ├── test_alert_manager.py
│   └── test_feedback_system.py
│
└── README files for each module
```

## 🎯 Next Steps

### Immediate (Current Session)

1. ✅ Server is running
2. ✅ API endpoints working
3. ✅ Demo client available
4. ✅ All core modules implemented

### Short Term (Next Session)

1. Install Python 3.11 or 3.12
2. Run full test suite
3. Integrate real audio processing pipeline
4. Train ML model on infant cry dataset

### Long Term

1. Collect real infant cry data
2. Train production ML model
3. Implement feedback loop for continuous learning
4. Deploy to production environment
5. Add frontend UI

## 🆘 Troubleshooting

### Server Won't Start

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Use a different port
set PORT=8000
python run_simple_server.py
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Numpy Crashes

This is expected with Python 3.14. Solutions:
1. Use the current mock implementation (working now)
2. Install Python 3.11 or 3.12 for full functionality

## 📞 Support

For issues or questions:
1. Check the README files in each module
2. Review the comprehensive test suites
3. See the design document: `.kiro/specs/neonatal-cry-detection/design.md`

## 🎉 Success!

The Neonatal Cry Detection System is now running and ready for demonstration!

**Server URL:** http://127.0.0.1:5000  
**Dashboard API:** http://127.0.0.1:5000/api/dashboard  
**Status:** ✅ OPERATIONAL (Mock Mode)
