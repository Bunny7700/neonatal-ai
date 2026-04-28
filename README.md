👶 Neonatal AI Monitoring System
A real-time AI-powered predictive neonatal monitoring system that detects breathing patterns, identifies early distress, and provides live NICU access for parents.

🌟 Features
Real-Time Breathing Detection (camera-based, non-contact)

Early Warning System for neonatal distress

Predictive Monitoring using AI models

Live NICU Streaming for Parents 👨‍👩‍👧

Baby Status Updates (feeding, sleeping, care activity)

Doctor Dashboard with alerts & risk levels

Audio + Visual Emergency Alerts

🤖 AI Models & Technologies Used
Google Gemini
→ System logic, reasoning, and intelligent workflow design

TensorFlow (Google)
→ Predictive model for neonatal risk detection

MediaPipe (Google)
→ Real-time motion tracking for breathing detection

OpenCV (cv2)
→ Frame processing & motion detection

🧠 System Architecture (Updated Flow)
Camera Capture (NICU crib monitoring)

Video Processing (face + chest detection)

AI Analysis

Breathing pattern detection

Skin color (cyanosis) detection

Predictive risk scoring

Decision Engine

Normal / Warning / Critical

Output

Doctor Dashboard (alerts + vitals)

Parent Interface (live stream + baby updates)

🚀 Key Innovation (NEW 🔥)
Non-contact monitoring (no sensors attached to baby)

Predictive + not just reactive system

Dual Interface: Doctor + Parent ecosystem

Emotional + clinical impact combined

📊 Detection Logic
Motion detected → Normal breathing

No motion > 10 sec → Critical alert

Pattern irregularity → Early warning

🛠️ Tech Stack
Backend
Python, FastAPI

OpenCV, NumPy

TensorFlow

Frontend
React + TypeScript

Vite

Recharts

👨‍⚕️👨‍👩‍👧 Use Cases
NICU monitoring

Early detection of neonatal distress

Parent reassurance via live access

SIDS risk reduction

🎯 Vision
To build a scalable AI-driven neonatal care platform that improves survival rates while enhancing transparency between hospitals and families.

