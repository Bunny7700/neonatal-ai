# 👶 Neonatal AI Monitoring System

A real-time AI-powered baby monitoring system that detects breathing movements and alerts caregivers when no movement is detected for 10 seconds.

## 🌟 Features

- **Real-Time Motion Detection**: Detects subtle breathing movements using OpenCV
- **Breathing Monitoring**: Alerts when no breathing movement detected for 10+ seconds
- **Live Camera Feed**: Side-by-side view of camera and monitoring dashboard
- **Audio & Visual Alerts**: Beeping alarm and red flashing overlay for critical alerts
- **Professional Dashboard**: Real-time statistics and monitoring metrics

## 🚀 Quick Start

### Backend (Python FastAPI)

```bash
cd Hackthon
python main.py
```

Backend runs on: `http://127.0.0.1:5000`

### Frontend (React + Vite)

```bash
cd NeoNatal/frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

## 📊 Detection Thresholds

- **SAFE**: 0-3 seconds of stillness 🟢
- **MONITOR**: 3-10 seconds of stillness 🟡
- **UNSAFE/ALERT**: 10+ seconds (no breathing detected) 🔴

## 🛠️ Tech Stack

### Backend
- Python 3.x
- FastAPI
- OpenCV (cv2)
- NumPy
- Uvicorn

### Frontend
- React 18
- TypeScript
- Vite
- Recharts (data visualization)
- Lucide React (icons)

## 📁 Project Structure

```
PROTOTYPE/
├── Hackthon/                 # Backend
│   ├── main.py              # FastAPI server
│   ├── motion_detection.py  # Motion detection logic
│   └── shared_data.py       # Dashboard data structure
├── NeoNatal/
│   └── frontend/            # Frontend
│       ├── src/
│       │   ├── App.tsx      # Main application
│       │   └── App.css      # Styles
│       └── package.json
└── README.md
```

## 🎯 How It Works

1. **Camera Capture**: Frontend captures video frames at 2 FPS
2. **Frame Processing**: Frames sent to backend for motion analysis
3. **Motion Detection**: OpenCV calculates pixel differences between frames
4. **Breathing Detection**: Motion > 50k indicates breathing/movement
5. **Alert System**: If motion < 50k for 10 seconds → Critical alert

## 🔧 Configuration

### Adjust Detection Sensitivity

Edit `Hackthon/motion_detection.py`:

```python
# Line 54: Motion threshold for breathing detection
if motion > 50000:  # Adjust this value
    self.last_movement_time = time.time()

# Line 59-65: Alert timing thresholds
if still_time < 3:
    status = "SAFE"
elif still_time < 10:  # Adjust warning threshold
    status = "MONITOR"
else:
    status = "UNSAFE"  # Triggers alert
```

## 📝 API Endpoints

- `GET /api/dashboard` - Get all monitoring data
- `POST /api/process_frame` - Send video frame for processing
- `GET /` - API status and endpoints list

## 🎨 Features Implemented

✅ Real-time motion detection  
✅ Breathing movement detection  
✅ Side-by-side camera and dashboard layout  
✅ Audio alarm system  
✅ Visual alert overlays  
✅ Responsive design  
✅ Live statistics display  

## 🚨 Important Notes

- **Camera Access**: Must use `http://localhost` (not IP address) for browser camera permissions
- **Breathing Detection**: System detects chest movements; works best with clear view of torso
- **Alert Timing**: 10-second threshold is configurable for different use cases

## 👥 Use Cases

- SIDS (Sudden Infant Death Syndrome) prevention
- Neonatal intensive care monitoring
- Home baby monitoring
- Sleep apnea detection

## 📄 License

This project is a prototype for demonstration purposes.

## 🙏 Acknowledgments

Built with modern web technologies and computer vision for infant safety monitoring.
