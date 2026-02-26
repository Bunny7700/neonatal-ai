"""
Flask Server with 3-Category Cry Detection
Categories: Hunger, Sleep, Discomfort
Uses MFCC pattern analysis with updated classification
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import time
import numpy as np
import os
from io import BytesIO

# Import PDF generation components
from pdf_report_generator import CryReportPDFGenerator
from gemini_client import GeminiInsightsClient, GeminiAPIError

# Try to import librosa for real audio processing
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ librosa loaded - using REAL audio processing")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("❌ librosa not available - install with: pip install librosa")

app = Flask(__name__)
CORS(app)

# Global state
cry_history = []

# Initialize PDF generator and Gemini client
pdf_generator = CryReportPDFGenerator()

# Get Gemini API key from environment (with fallback to hardcoded key)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDCl6YJQPi2RDwKKLcWHUzI7gcsT9__l10')
try:
    gemini_client = GeminiInsightsClient(GEMINI_API_KEY)
    print("✅ Gemini client initialized")
except Exception as e:
    gemini_client = None
    print(f"⚠️  Gemini client initialization failed: {e}")

# Reference patterns for 3 cry types
CRY_PATTERNS = {
    'hunger': {
        'pitch_range': (300, 450),
        'pitch_variability': 'low',  # <35 Hz std - rhythmic
        'intensity': 'moderate',  # RMS 0.04-0.08
        'spectral_centroid': (1500, 2500),
        'description': 'Rhythmic, sustained crying'
    },
    'sleep': {
        'pitch_range': (250, 350),
        'pitch_variability': 'high',  # >40 Hz std - fussy
        'intensity': 'low',  # RMS < 0.05
        'spectral_centroid': (1000, 2000),
        'description': 'Variable, fussy crying'
    },
    'discomfort': {
        'pitch_range': (450, 700),
        'pitch_variability': 'high',  # >50 Hz std - urgent
        'intensity': 'high',  # RMS > 0.06
        'spectral_centroid': (2000, 3500),
        'description': 'Loud, urgent crying'
    }
}

def extract_audio_features(audio_data, sample_rate=16000):
    """Extract comprehensive audio features using librosa"""
    if not LIBROSA_AVAILABLE:
        return None
    
    try:
        # Ensure audio is numpy array
        if not isinstance(audio_data, np.ndarray):
            audio_data = np.array(audio_data, dtype=np.float32)
        
        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        features = {}
        
        # 1. MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
        features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
        
        # 2. Pitch (fundamental frequency)
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if pitch_values:
            features['pitch_mean'] = float(np.mean(pitch_values))
            features['pitch_std'] = float(np.std(pitch_values))
        else:
            features['pitch_mean'] = 0.0
            features['pitch_std'] = 0.0
        
        # 3. Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
        features['spectral_centroid_std'] = float(np.std(spectral_centroids))
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
        features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
        
        # 4. RMS energy (intensity)
        rms = librosa.feature.rms(y=audio_data)[0]
        features['rms_mean'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))
        
        # 5. Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zero_crossing_rate_mean'] = float(np.mean(zcr))
        
        return features
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def classify_cry_3categories(features):
    """
    Classify cry into 3 categories: hunger, sleep, discomfort
    Uses rule-based scoring system
    """
    if not features:
        return 'discomfort', 0.0
    
    pitch = features.get('pitch_mean', 0)
    pitch_std = features.get('pitch_std', 0)
    rms = features.get('rms_mean', 0)
    spectral_centroid = features.get('spectral_centroid_mean', 0)
    zcr = features.get('zero_crossing_rate_mean', 0)
    
    scores = {
        'hunger': 0.0,
        'sleep': 0.0,
        'discomfort': 0.0
    }
    
    # HUNGER SCORING
    if 300 <= pitch <= 450:
        scores['hunger'] += 35
    if pitch_std < 35:  # Rhythmic
        scores['hunger'] += 25
    if 0.04 <= rms <= 0.08:  # Moderate intensity
        scores['hunger'] += 20
    if spectral_centroid < 2000:
        scores['hunger'] += 10
    
    # SLEEP SCORING
    if pitch_std > 40:  # Variable/fussy
        scores['sleep'] += 30
    if rms < 0.05:  # Lower intensity
        scores['sleep'] += 25
    if pitch < 350:  # Lower pitch
        scores['sleep'] += 20
    if spectral_centroid < 2000:
        scores['sleep'] += 15
    
    # DISCOMFORT SCORING
    if pitch > 450:  # High pitch
        scores['discomfort'] += 40
    if rms > 0.06:  # High intensity
        scores['discomfort'] += 30
    if pitch_std > 50:  # Very irregular
        scores['discomfort'] += 15
    if zcr > 0.12:  # Harsh sound
        scores['discomfort'] += 10
    if spectral_centroid > 2500:
        scores['discomfort'] += 10
    
    # Find best match
    cry_type = max(scores, key=scores.get)
    confidence = min(100.0, scores[cry_type] * 0.95)
    
    return cry_type, confidence

def is_baby_cry(features):
    """
    Determine if audio contains baby crying
    Returns (is_crying, confidence)
    """
    if not features:
        return False, 0.0
    
    rms = features.get('rms_mean', 0)
    pitch = features.get('pitch_mean', 0)
    
    # Baby cry characteristics:
    # - RMS > 0.01 (sufficient energy)
    # - Pitch in baby cry range (200-800 Hz)
    is_crying = rms > 0.01 and 200 <= pitch <= 800
    
    if is_crying:
        confidence = min(95.0, 50.0 + (rms * 500))
    else:
        confidence = max(5.0, rms * 300)
    
    return is_crying, confidence

@app.route('/api/analyze_audio', methods=['POST'])
def analyze_audio():
    """
    Analyze audio and classify cry type
    Expects: { "audio": [float array], "sampleRate": 16000 }
    Returns: { "cryType": "hunger|sleep|discomfort", "confidence": 0-100, ... }
    """
    try:
        data = request.json
        audio_samples = data.get('audio', [])
        sample_rate = data.get('sampleRate', 16000)
        
        if not audio_samples:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Convert to numpy array
        audio_data = np.array(audio_samples, dtype=np.float32)
        
        # Extract features
        features = extract_audio_features(audio_data, sample_rate)
        
        if not features:
            return jsonify({'error': 'Failed to extract features'}), 500
        
        # Check if it's a cry
        is_crying, detection_confidence = is_baby_cry(features)
        
        if not is_crying:
            return jsonify({
                'isCrying': False,
                'cryType': 'none',
                'confidence': 0,
                'detectionConfidence': detection_confidence,
                'message': 'No baby cry detected',
                'timestamp': time.time()
            })
        
        # Classify cry type
        cry_type, confidence = classify_cry_3categories(features)
        
        # Get pattern description
        pattern_info = CRY_PATTERNS.get(cry_type, {})
        
        # Create result
        result = {
            'isCrying': True,
            'cryType': cry_type,
            'confidence': round(confidence, 1),
            'detectionConfidence': round(detection_confidence, 1),
            'message': get_cry_message(cry_type),
            'icon': get_cry_icon(cry_type),
            'color': get_cry_color(cry_type),
            'pattern': pattern_info.get('description', ''),
            'features': {
                'pitch': round(features.get('pitch_mean', 0), 1),
                'pitch_std': round(features.get('pitch_std', 0), 1),
                'intensity': round(features.get('rms_mean', 0), 3),
                'spectral_centroid': round(features.get('spectral_centroid_mean', 0), 1)
            },
            'timestamp': time.time()
        }
        
        # Add to history
        cry_history.append(result)
        if len(cry_history) > 50:
            cry_history.pop(0)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        return jsonify({'error': str(e)}), 500

def get_cry_message(cry_type):
    """Get human-readable message for cry type"""
    messages = {
        'hunger': 'Baby may be hungry 🍼',
        'sleep': 'Baby is tired and needs sleep 😴',
        'discomfort': 'Baby is uncomfortable or in distress ⚠️'
    }
    return messages.get(cry_type, 'Unknown cry type')

def get_cry_icon(cry_type):
    """Get icon for cry type"""
    icons = {
        'hunger': '🍼',
        'sleep': '😴',
        'discomfort': '⚠️'
    }
    return icons.get(cry_type, '❓')

def get_cry_color(cry_type):
    """Get color code for cry type"""
    colors = {
        'hunger': '#f59e0b',      # Orange
        'sleep': '#3b82f6',       # Blue
        'discomfort': '#ef4444'   # Red
    }
    return colors.get(cry_type, '#6b7280')

@app.route('/api/cry_history', methods=['GET'])
def get_cry_history():
    """Get recent cry detection history"""
    return jsonify({
        'history': cry_history[-20:],  # Last 20 detections
        'count': len(cry_history)
    })

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback on cry classification
    Expects: { "predicted": "hunger", "actual": "sleep", "timestamp": 123456 }
    """
    try:
        data = request.json
        predicted = data.get('predicted')
        actual = data.get('actual')
        timestamp = data.get('timestamp')
        
        # Store feedback (in production, save to database)
        feedback_entry = {
            'predicted': predicted,
            'actual': actual,
            'timestamp': timestamp,
            'received_at': time.time()
        }
        
        print(f"Feedback received: {predicted} -> {actual}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded'
        })
        
    except Exception as e:
        print(f"Error recording feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'categories': ['hunger', 'sleep', 'discomfort'],
        'librosa_available': LIBROSA_AVAILABLE,
        'total_detections': len(cry_history),
        'version': '3-category-system',
        'pdf_export_available': True,
        'gemini_available': gemini_client is not None
    })

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """
    Generate PDF report from cry detection data
    
    Request Body:
    {
        "cry_type": "hunger",
        "confidence": 85.5,
        "intensity": 65,
        "timestamp": 1234567890,
        "features": {
            "pitch": 425.3,
            "pitch_std": 32.1,
            "intensity_db": -25.4,
            "spectral_centroid": 1850.2,
            "zero_crossing_rate": 0.08,
            "duration": 2.5
        }
    }
    
    Response: PDF file (application/pdf)
    """
    try:
        # Parse request data
        cry_data = request.json
        
        if not cry_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['cry_type', 'confidence', 'timestamp', 'features']
        for field in required_fields:
            if field not in cry_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate AI insights (if Gemini is available)
        ai_insights = None
        if gemini_client:
            try:
                print("Generating AI insights with Gemini...")
                ai_insights = gemini_client.generate_insights(cry_data)
                print("AI insights generated successfully")
            except GeminiAPIError as e:
                print(f"Gemini API failed: {e}")
                # Continue without insights
        else:
            print("Gemini client not available, skipping AI insights")
        
        # Generate PDF
        print("Generating PDF report...")
        pdf_bytes = pdf_generator.generate_report(cry_data, ai_insights)
        
        # Create response with PDF
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = cry_data.get('timestamp', time.time())
        filename = f"cry_report_{int(timestamp)}.pdf"
        
        print(f"PDF report generated: {filename}")
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': '3-Category Baby Cry Detection Server',
        'categories': ['hunger', 'sleep', 'discomfort'],
        'endpoints': {
            '/api/analyze_audio': 'POST - Analyze audio and classify cry',
            '/api/generate_report': 'POST - Generate PDF report',
            '/api/cry_history': 'GET - Get recent detections',
            '/api/feedback': 'POST - Submit feedback',
            '/api/status': 'GET - Server status'
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🍼 3-Category Baby Cry Detection Server")
    print("="*60)
    print("\nCategories:")
    print("  🍼 Hunger - Rhythmic, sustained crying")
    print("  😴 Sleep - Variable, fussy crying")
    print("  ⚠️  Discomfort - Loud, urgent crying")
    print("\nServer starting on http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
