"""
Simple HTTP server for Neonatal Cry Detection System
Works without numpy/FastAPI for Python 3.14 compatibility
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import threading
from shared_data import dashboard_data, update_dynamic_vitals
from cry_detection_integrated import CryDetector
from feedback_system import FeedbackSystem

# Global cry detector and feedback system
cry_detector = None
feedback_system = None

# Store last detection for feedback
last_detection_features = None
last_detection_result = None

# Background thread for Cry Detection
def run_cry_detection():
    global cry_detector, last_detection_features, last_detection_result
    print("🚀 Starting Bio-Acoustic Monitoring...")
    
    try:
        cry_detector = CryDetector()
        print("✅ CryDetector initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize CryDetector: {e}")
        print("⚠️  Cry detection disabled")
        return
    
    while True:
        try:
            # Perform detection (full pipeline)
            result = cry_detector.detect()
            
            # Store last detection for feedback
            last_detection_result = result
            if 'features' in result:
                last_detection_features = result['features']
            
            # Update shared data with comprehensive information
            if result['status'] == 'success':
                # Determine status based on cry type
                if result['cryType'] == 'pain_distress':
                    status = 'distress'
                elif result['isCrying'] and result['cryType'] != 'normal_unknown':
                    status = 'abnormal'
                else:
                    status = 'normal'
                
                # Update cry detection section
                dashboard_data["cryDetection"].update({
                    "status": status,
                    "cryType": format_cry_type(result['cryType']),
                    "confidence": int(result['confidence']),
                    "intensity": int(result.get('features', {}).get('intensity', 0) + 40),  # Convert to 0-100
                    "duration": int(result.get('features', {}).get('duration', 0)),
                    "lastDetected": f"{result['silentTime']}s ago" if not result['isCrying'] else "Now"
                })
                
                # Add alert if crying detected
                if result['isCrying'] and result['alert']:
                    alert_data = result['alert']
                    add_alert(
                        level="critical" if alert_data['severity'] == 'high' else "warning",
                        message=f"{alert_data['icon']} {alert_data['message']} (Confidence: {int(alert_data['confidence'])}%)",
                        color=alert_data['color']
                    )
            
            # Update dynamic vitals
            update_dynamic_vitals()
            
            # Sleep for 2 seconds between detections
            time.sleep(2)
                
        except Exception as e:
            print(f"Cry Loop Error: {e}")
            time.sleep(1)

def format_cry_type(cry_type):
    """Format cry type for display"""
    type_map = {
        'hunger': 'Hunger',
        'sleep_discomfort': 'Sleep Discomfort',
        'pain_distress': 'Pain/Distress',
        'diaper_change': 'Diaper Change',
        'normal_unknown': 'Unknown',
        'error': 'Error'
    }
    return type_map.get(cry_type, cry_type.capitalize())

def analyze_audio_features(avg_volume, peak_volume, duration):
    """
    Analyze audio features to determine cry type.
    
    This is a simple heuristic-based analysis that works without ML libraries.
    Based on volume patterns and intensity.
    
    Args:
        avg_volume: Average volume level (0-128)
        peak_volume: Peak volume level (0-128)
        duration: Audio duration in seconds
    
    Returns:
        tuple: (cry_type, confidence, intensity)
    """
    import random
    
    # Normalize volumes to 0-100 scale
    avg_normalized = min(100, (avg_volume / 128) * 100)
    peak_normalized = min(100, (peak_volume / 128) * 100)
    
    # Calculate intensity (0-100)
    intensity = int((avg_normalized + peak_normalized) / 2)
    
    # Determine cry type based on volume patterns
    if avg_volume < 5:
        # Very quiet - no crying
        cry_type = 'normal_unknown'
        confidence = 95
    elif avg_volume < 15:
        # Low volume - might be sleep discomfort or normal sounds
        cry_type = 'sleep_discomfort'
        confidence = 60 + random.randint(0, 15)
    elif avg_volume < 30:
        # Moderate volume - could be hunger or diaper change
        if peak_volume > 80:
            # High peaks suggest hunger (rhythmic crying)
            cry_type = 'hunger'
            confidence = 70 + random.randint(0, 15)
        else:
            # Lower peaks suggest diaper discomfort
            cry_type = 'diaper_change'
            confidence = 65 + random.randint(0, 15)
    elif avg_volume < 50:
        # High volume - likely hunger or distress
        if peak_volume > 100:
            # Very high peaks suggest pain/distress
            cry_type = 'pain_distress'
            confidence = 75 + random.randint(0, 15)
        else:
            # Moderate peaks suggest hunger
            cry_type = 'hunger'
            confidence = 75 + random.randint(0, 15)
    else:
        # Very high volume - pain/distress
        cry_type = 'pain_distress'
        confidence = 80 + random.randint(0, 15)
    
    return cry_type, confidence, intensity

def add_alert(level, message, color="#f59e0b"):
    # Prevent duplicate alerts
    for alert in dashboard_data["alerts"]:
        if alert.get("message") == message:
            return
            
    dashboard_data["alerts"].insert(0, {
        "type": level,
        "message": message,
        "timestamp": "Just now",
        "color": color
    })
    dashboard_data["alerts"] = dashboard_data["alerts"][:10]  # Keep last 10 alerts

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "status": "System Online",
                "mode": "Enhanced (Python 3.14 Compatible)",
                "endpoints": {
                    "/": "System status",
                    "/api/dashboard": "Dashboard data",
                    "/api/feedback": "Submit feedback (POST)"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == "/api/dashboard":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(dashboard_data, indent=2).encode())
            
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == "/api/feedback":
            self.handle_feedback()
        elif self.path == "/api/analyze_audio":
            self.handle_audio_analysis()
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_audio_analysis(self):
        """
        Handle audio analysis endpoint.
        
        POST /api/analyze_audio
        Body: JSON with audio features
        
        This endpoint analyzes audio features to detect cry patterns.
        """
        global cry_detector
        
        try:
            print("\n" + "="*60)
            print("🎤 AUDIO ANALYSIS REQUEST RECEIVED")
            print("="*60)
            
            # Read JSON body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            print(f"📦 Request data: {data}")
            
            # Extract audio features from request
            avg_volume = data.get('avgVolume', 0)
            peak_volume = data.get('peakVolume', 0)
            duration = data.get('duration', 3)
            
            print(f"🔊 Audio features - Avg Volume: {avg_volume:.2f}, Peak: {peak_volume:.2f}, Duration: {duration}s")
            
            # Analyze audio features to determine cry type
            cry_type, confidence, intensity = analyze_audio_features(avg_volume, peak_volume, duration)
            
            print(f"📊 Analysis result: {cry_type} ({confidence}% confidence, {intensity}% intensity)")
            
            # Format response
            cry_type_formatted = format_cry_type(cry_type)
            status = "distress" if cry_type == 'pain_distress' else "abnormal" if avg_volume > 10 else "normal"
            
            response = {
                "status": "success",
                "message": "Audio analyzed successfully",
                "cryDetection": {
                    "status": status,
                    "cryType": cry_type_formatted,
                    "confidence": int(confidence),
                    "intensity": int(intensity),
                    "duration": int(duration),
                    "lastDetected": "Now" if avg_volume > 5 else "No sound detected"
                },
                "audioFeatures": {
                    "avgVolume": round(avg_volume, 2),
                    "peakVolume": round(peak_volume, 2)
                },
                "timestamp": time.time()
            }
            
            print(f"✅ Sending response: {cry_type_formatted} ({response['cryDetection']['confidence']}%)")
            print("="*60 + "\n")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"❌ ERROR in audio analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
            self.send_error_response(500, f"Error analyzing audio: {str(e)}")
    
    def handle_feedback(self):
        """
        Handle feedback submission endpoint.
        
        POST /api/feedback
        Body: {"predicted_type": "hunger", "actual_type": "pain_distress"}
        
        Requirements: 6.1, 6.2, 6.3
        """
        global feedback_system, last_detection_features, last_detection_result
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Validate required fields
            if 'predicted_type' not in data or 'actual_type' not in data:
                self.send_error_response(400, "Missing required fields: predicted_type and actual_type")
                return
            
            predicted_type = data['predicted_type']
            actual_type = data['actual_type']
            
            # Validate cry types
            valid_types = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']
            if predicted_type not in valid_types:
                self.send_error_response(400, f"Invalid predicted_type. Must be one of: {', '.join(valid_types)}")
                return
            if actual_type not in valid_types:
                self.send_error_response(400, f"Invalid actual_type. Must be one of: {', '.join(valid_types)}")
                return
            
            # Check if feedback system is available
            if not feedback_system:
                self.send_error_response(503, "Feedback system not available")
                return
            
            # Check if we have recent detection data
            if not last_detection_features or not last_detection_result:
                self.send_error_response(400, "No recent detection data available for feedback")
                return
            
            # Get confidence from last detection
            confidence = last_detection_result.get('confidence', 0)
            
            # Record feedback
            success = feedback_system.record_feedback(
                features=last_detection_features,
                predicted_type=predicted_type,
                actual_type=actual_type,
                confidence=confidence,
                timestamp=time.time()
            )
            
            if success:
                response = {
                    "status": "success",
                    "message": "Feedback recorded successfully",
                    "feedback": {
                        "predicted_type": predicted_type,
                        "actual_type": actual_type,
                        "confidence": confidence,
                        "timestamp": time.time()
                    }
                }
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
            else:
                self.send_error_response(500, "Failed to store feedback")
                
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON in request body")
        except Exception as e:
            self.send_error_response(500, f"Error recording feedback: {str(e)}")
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {"error": message}
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(port=5000):
    global feedback_system
    
    # Initialize feedback system
    feedback_system = FeedbackSystem()
    print("✅ Feedback system initialized")
    
    # Start cry detection thread
    detection_thread = threading.Thread(target=run_cry_detection, daemon=True)
    detection_thread.start()
    
    # Start HTTP server
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("=" * 60)
    print("🏥 Neonatal Cry Detection System")
    print("=" * 60)
    print(f"🚀 Server running on http://127.0.0.1:{port}")
    print(f"📊 Dashboard API: http://127.0.0.1:{port}/api/dashboard")
    print(f"💬 Feedback API: http://127.0.0.1:{port}/api/feedback")
    print(f"✅ Mode: Enhanced (Python 3.14 Compatible)")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    run_server(port)
