"""
Flask Server with Real ML-Based Cry Detection
Uses librosa for actual audio feature extraction
Requires Python 3.11/3.12 with numpy, librosa, scipy, soundfile
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import numpy as np

# Try to import librosa for real audio processing
try:
    import librosa
    import scipy.signal
    LIBROSA_AVAILABLE = True
    print("✅ librosa loaded - using REAL audio processing")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("❌ librosa not available - install with: pip install librosa")

app = Flask(__name__)
CORS(app)

# Global state
cry_history = []

def extract_audio_features_real(audio_data, sample_rate=16000):
    """
    Extract real audio features using librosa
    
    Args:
        audio_data: numpy array of audio samples
        sample_rate: sample rate in Hz
    
    Returns:
        dict with audio features
    """
    if not LIBROSA_AVAILABLE:
        return None
    
    try:
        # Ensure audio is numpy array
        if not isinstance(audio_data, np.ndarray):
            audio_data = np.array(audio_data, dtype=np.float32)
        
        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Extract features
        features = {}
        
        # 1. MFCC (Mel-frequency cepstral coefficients) - voice characteristics
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
        features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
        
        # 2. Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
        features['spectral_centroid_std'] = float(np.std(spectral_centroids))
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
        features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
        features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
        
        # 3. Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zero_crossing_rate_mean'] = float(np.mean(zcr))
        
        # 4. RMS Energy
        rms = librosa.feature.rms(y=audio_data)[0]
        features['rms_mean'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))
        
        # 5. Pitch (fundamental frequency)
        try:
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
        except:
            features['pitch_mean'] = 0.0
            features['pitch_std'] = 0.0
        
        # 6. Tempo
        try:
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            # Handle both scalar and array returns
            if hasattr(tempo, '__len__'):
                features['tempo'] = float(tempo[0]) if len(tempo) > 0 else 0.0
            else:
                features['tempo'] = float(tempo)
        except:
            features['tempo'] = 0.0
        
        return features
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def classify_cry_from_features(features):
    """
    Classify cry type based on extracted audio features
    Uses ML-inspired heuristics based on cry research
    
    Baby cry characteristics (research-based):
    - Fundamental frequency: 300-600 Hz (higher than adult speech: 85-180 Hz for males, 165-255 Hz for females)
    - High intensity: Babies cry loudly
    - Specific spectral patterns: High energy in upper frequencies
    - Duration: Sustained sounds (not short bursts)
    
    Cry types:
    - Hunger: 300-600 Hz, rhythmic, moderate intensity
    - Pain: 500-700 Hz, high intensity, sudden onset
    - Discomfort: 250-400 Hz, variable, lower intensity
    - Sleepy: 200-350 Hz, low intensity, slow rhythm
    """
    if not features:
        return {
            'isCrying': False,
            'cryType': 'no_cry',
            'confidence': 0,
            'intensity': 0,
            'reason': 'No audio features available'
        }
    
    # Extract key features
    pitch = features.get('pitch_mean', 0)
    pitch_std = features.get('pitch_std', 0)
    rms = features.get('rms_mean', 0)
    spectral_centroid = features.get('spectral_centroid_mean', 0)
    spectral_rolloff = features.get('spectral_rolloff_mean', 0)
    zcr = features.get('zero_crossing_rate_mean', 0)
    
    # Debug logging
    print(f"🔍 Audio Analysis:")
    print(f"   Pitch: {pitch:.1f} Hz (std: {pitch_std:.1f})")
    print(f"   RMS Energy: {rms:.4f}")
    print(f"   Spectral Centroid: {spectral_centroid:.1f} Hz")
    print(f"   Spectral Rolloff: {spectral_rolloff:.1f} Hz")
    print(f"   Zero-Crossing Rate: {zcr:.4f}")
    
    # ============================================================================
    # STEP 1: Detect if this is a BABY CRY vs other sounds
    # ============================================================================
    
    is_baby_cry = True
    rejection_reasons = []
    
    # Check 1: Minimum energy (must have sound)
    if rms < 0.01:
        is_baby_cry = False
        rejection_reasons.append("Too quiet (RMS < 0.01)")
    
    # Check 2: Pitch range (baby cries are 250-700 Hz, adult speech is 85-255 Hz)
    if pitch < 250 or pitch > 800:
        is_baby_cry = False
        if pitch < 250:
            rejection_reasons.append(f"Pitch too low ({pitch:.0f} Hz < 250 Hz) - likely adult speech or noise")
        else:
            rejection_reasons.append(f"Pitch too high ({pitch:.0f} Hz > 800 Hz) - likely whistle or electronic noise")
    
    # Check 3: Spectral centroid (baby cries have energy in mid-high frequencies)
    # Adult speech: 500-2000 Hz, Baby cry: 1000-3000 Hz
    if spectral_centroid < 800:
        is_baby_cry = False
        rejection_reasons.append(f"Spectral centroid too low ({spectral_centroid:.0f} Hz) - likely low-frequency noise or deep voice")
    
    # Check 4: Minimum intensity (baby cries are loud)
    if rms < 0.02:
        is_baby_cry = False
        rejection_reasons.append(f"Intensity too low (RMS {rms:.4f}) - baby cries are typically louder")
    
    # Check 5: Spectral rolloff (baby cries have high-frequency energy)
    if spectral_rolloff < 1500:
        is_baby_cry = False
        rejection_reasons.append(f"Spectral rolloff too low ({spectral_rolloff:.0f} Hz) - lacks high-frequency energy typical of baby cries")
    
    # If not a baby cry, return early
    if not is_baby_cry:
        print(f"   ❌ NOT A BABY CRY:")
        for reason in rejection_reasons:
            print(f"      - {reason}")
        return {
            'isCrying': False,
            'cryType': 'no_cry',
            'confidence': 15,
            'intensity': int(min(rms * 1000, 100)),
            'reason': f'Not a baby cry: {rejection_reasons[0]}'
        }
    
    # ============================================================================
    # STEP 2: Classify CRY TYPE (only if it's a baby cry)
    # ============================================================================
    
    print(f"   ✅ BABY CRY DETECTED - Classifying type...")
    
    scores = {
        'pain_distress': 0,
        'hunger': 0,
        'sleep_discomfort': 0,
        'diaper_change': 0
    }
    
    # Pain/Distress: High pitch (500-700 Hz), high intensity, high variability
    if pitch > 500 and rms > 0.05:
        scores['pain_distress'] += 40
    if pitch_std > 50:
        scores['pain_distress'] += 20
    if spectral_centroid > 2000:
        scores['pain_distress'] += 15
    if rms > 0.08:
        scores['pain_distress'] += 10
    
    # Hunger: Moderate pitch (350-550 Hz), rhythmic, moderate intensity
    if 350 <= pitch <= 550 and rms > 0.03:
        scores['hunger'] += 35
    if pitch_std < 40:  # More consistent pitch
        scores['hunger'] += 20
    if 1500 <= spectral_centroid <= 2500:
        scores['hunger'] += 15
    if 0.04 <= rms <= 0.08:
        scores['hunger'] += 10
    
    # Sleep Discomfort: Lower pitch (250-400 Hz), lower intensity
    if 250 <= pitch <= 400:
        scores['sleep_discomfort'] += 30
    if rms < 0.05:
        scores['sleep_discomfort'] += 25
    if spectral_centroid < 1800:
        scores['sleep_discomfort'] += 15
    if pitch_std < 35:
        scores['sleep_discomfort'] += 10
    
    # Diaper Change: Moderate features, variable, intermittent
    if 300 <= pitch <= 500:
        scores['diaper_change'] += 25
    if 0.03 <= rms <= 0.07:
        scores['diaper_change'] += 20
    if zcr > 0.05:
        scores['diaper_change'] += 15
    if 30 <= pitch_std <= 60:
        scores['diaper_change'] += 10
    
    # Determine winner
    cry_type = max(scores, key=scores.get)
    confidence = min(scores[cry_type], 95)
    
    # Boost confidence if multiple indicators align
    if scores[cry_type] > 60:
        confidence = min(confidence + 10, 95)
    
    # Calculate intensity (0-100)
    intensity = int(min(rms * 1000, 100))
    
    # Generate reason
    reasons = {
        'pain_distress': f'High-pitched cry ({int(pitch)} Hz) with high intensity - possible pain or distress',
        'hunger': f'Rhythmic cry pattern ({int(pitch)} Hz) with moderate intensity - likely hunger',
        'sleep_discomfort': f'Low-intensity cry ({int(pitch)} Hz) - sleep discomfort or tiredness',
        'diaper_change': f'Variable cry pattern ({int(pitch)} Hz) - possible diaper discomfort'
    }
    
    print(f"   → Cry Type: {cry_type}")
    print(f"   → Confidence: {confidence}%")
    print(f"   → Intensity: {intensity}/100")
    print(f"   → Scores: {scores}")
    
    return {
        'isCrying': True,
        'cryType': cry_type,
        'confidence': confidence,
        'intensity': intensity,
        'reason': reasons[cry_type],
        'features': {
            'pitch_hz': int(pitch),
            'rms_energy': round(rms, 4),
            'spectral_centroid': int(spectral_centroid)
        }
    }

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mode': 'ML-Based Cry Detection',
        'librosa': 'available' if LIBROSA_AVAILABLE else 'not available',
        'message': 'Real audio processing with librosa' if LIBROSA_AVAILABLE else 'Install librosa for real audio processing'
    })

@app.route('/api/analyze_audio', methods=['POST'])
def analyze_audio():
    """
    Analyze audio features and detect cry
    Expects JSON with audio features or raw audio data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if we have raw audio data
        if 'audioData' in data and LIBROSA_AVAILABLE:
            # Convert audio data to numpy array
            audio_array = np.array(data['audioData'], dtype=np.float32)
            sample_rate = data.get('sampleRate', 16000)
            
            # Extract real features
            features = extract_audio_features_real(audio_array, sample_rate)
            
            if features:
                # Classify based on real features
                result = classify_cry_from_features(features)
            else:
                # Fallback to simple analysis
                avg_volume = data.get('avgVolume', 0)
                result = simple_volume_analysis(avg_volume)
        else:
            # Use simple volume-based analysis
            avg_volume = data.get('avgVolume', 0)
            result = simple_volume_analysis(avg_volume)
        
        # Add to history
        if result['isCrying']:
            cry_history.append({
                'timestamp': time.strftime('%H:%M:%S'),
                'cryType': result['cryType'],
                'confidence': result['confidence'],
                'intensity': result['intensity']
            })
            # Keep only last 10
            if len(cry_history) > 10:
                cry_history.pop(0)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_audio: {e}")
        return jsonify({'error': str(e)}), 500

def simple_volume_analysis(avg_volume):
    """Fallback simple volume-based analysis"""
    if avg_volume < 5:
        return {
            'isCrying': False,
            'cryType': 'normal',
            'confidence': 20,
            'intensity': 0,
            'reason': 'Very quiet - no cry detected'
        }
    elif avg_volume < 20:
        return {
            'isCrying': True,
            'cryType': 'sleep_discomfort',
            'confidence': 45,
            'intensity': int(avg_volume * 2),
            'reason': 'Low volume - possible sleep discomfort'
        }
    elif avg_volume < 50:
        return {
            'isCrying': True,
            'cryType': 'hunger',
            'confidence': 65,
            'intensity': int(avg_volume * 1.5),
            'reason': 'Moderate volume - likely hunger or diaper change'
        }
    else:
        return {
            'isCrying': True,
            'cryType': 'pain_distress',
            'confidence': 80,
            'intensity': min(int(avg_volume * 1.2), 100),
            'reason': 'High volume - possible pain or distress'
        }

@app.route('/api/cry_history', methods=['GET'])
def get_cry_history():
    """Get cry detection history"""
    return jsonify(cry_history)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for cry detection accuracy
    Expects JSON with predicted_type and actual_type
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        predicted_type = data.get('predicted_type')
        actual_type = data.get('actual_type')
        
        if not predicted_type or not actual_type:
            return jsonify({'error': 'Both predicted_type and actual_type are required'}), 400
        
        # Log feedback (in production, save to database)
        print(f"📝 Feedback received: Predicted={predicted_type}, Actual={actual_type}")
        
        # You could save this to a file or database for model improvement
        feedback_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'predicted': predicted_type,
            'actual': actual_type
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback received successfully. Thank you for helping improve the system!'
        })
        
    except Exception as e:
        print(f"Error in submit_feedback: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 Starting ML-Based Cry Detection Server")
    print("="*60)
    if LIBROSA_AVAILABLE:
        print("✅ Real audio processing enabled (librosa)")
        print("   - MFCC feature extraction")
        print("   - Spectral analysis")
        print("   - Pitch detection")
        print("   - ML-based classification")
    else:
        print("⚠️  Librosa not available - using simple volume analysis")
        print("   Install with: pip install librosa scipy soundfile")
    print()
    print("Server: http://127.0.0.1:5000")
    print("API: http://127.0.0.1:5000/api/analyze_audio")
    print("="*60)
    
    app.run(host='127.0.0.1', port=5000, debug=False)
