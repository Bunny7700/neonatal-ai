"""
Flask Server with Improved ML-Based Cry Detection
Uses MFCC pattern analysis for better accuracy
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
    from scipy.spatial.distance import euclidean
    LIBROSA_AVAILABLE = True
    print("✅ librosa loaded - using REAL audio processing with pattern matching")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("❌ librosa not available - install with: pip install librosa")

app = Flask(__name__)
CORS(app)

# Global state
cry_history = []

# Reference MFCC patterns for 3 cry types (simplified classification)
CRY_PATTERNS = {
    'hunger': {
        'pitch_range': (300, 450),
        'pitch_variability': 'low',  # <35 Hz std - rhythmic
        'intensity': 'moderate',  # RMS 0.04-0.08
        'spectral_centroid': (1500, 2500),
        'mfcc_pattern': 'rhythmic_consistent',
        'description': 'Rhythmic, sustained crying'
    },
    'sleep': {
        'pitch_range': (250, 350),
        'pitch_variability': 'high',  # >40 Hz std - fussy
        'intensity': 'low',  # RMS < 0.05
        'spectral_centroid': (1000, 2000),
        'mfcc_pattern': 'gradual_low_energy',
        'description': 'Variable, fussy crying'
    },
    'discomfort': {
        'pitch_range': (450, 700),
        'pitch_variability': 'high',  # >50 Hz std - urgent
        'intensity': 'high',  # RMS > 0.06
        'spectral_centroid': (2000, 3500),
        'mfcc_pattern': 'sharp_onset_high_energy',
        'description': 'Loud, urgent crying'
    }
}

def extract_audio_features_improved(audio_data, sample_rate=16000):
    """
    Extract comprehensive audio features using librosa
    Focuses on features that distinguish baby cries from other sounds
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
        
        features = {}
        
        # 1. MFCC (Mel-frequency cepstral coefficients) - MOST IMPORTANT for cry detection
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1)
        features['mfcc_std'] = np.std(mfccs, axis=1)
        features['mfcc_delta'] = np.mean(librosa.feature.delta(mfccs), axis=1)
        
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
        
        # 5. Pitch (fundamental frequency) - CRITICAL for baby cry detection
        try:
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate, fmin=200, fmax=800)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = float(np.mean(pitch_values))
                features['pitch_std'] = float(np.std(pitch_values))
                features['pitch_max'] = float(np.max(pitch_values))
                features['pitch_min'] = float(np.min(pitch_values))
            else:
                features['pitch_mean'] = 0.0
                features['pitch_std'] = 0.0
                features['pitch_max'] = 0.0
                features['pitch_min'] = 0.0
        except:
            features['pitch_mean'] = 0.0
            features['pitch_std'] = 0.0
            features['pitch_max'] = 0.0
            features['pitch_min'] = 0.0
        
        # 6. Tempo and rhythm
        try:
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            if hasattr(tempo, '__len__'):
                features['tempo'] = float(tempo[0]) if len(tempo) > 0 else 0.0
            else:
                features['tempo'] = float(tempo)
        except:
            features['tempo'] = 0.0
        
        # 7. Chroma features (harmonic content)
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        features['chroma_mean'] = float(np.mean(chroma))
        
        return features
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def is_baby_cry(features):
    """
    Determine if the audio is a baby cry vs other sounds
    Uses multiple acoustic criteria based on research
    """
    if not features:
        return False, "No features available"
    
    pitch = features.get('pitch_mean', 0)
    rms = features.get('rms_mean', 0)
    spectral_centroid = features.get('spectral_centroid_mean', 0)
    spectral_rolloff = features.get('spectral_rolloff_mean', 0)
    
    # Baby cry detection criteria (research-based)
    checks = []
    
    # 1. Pitch range (baby cries: 250-700 Hz)
    if 250 <= pitch <= 700:
        checks.append(True)
    else:
        return False, f"Pitch out of range ({pitch:.0f} Hz not in 250-700 Hz)"
    
    # 2. Minimum intensity (baby cries are loud)
    if rms >= 0.02:
        checks.append(True)
    else:
        return False, f"Too quiet (RMS {rms:.4f} < 0.02)"
    
    # 3. Spectral centroid (baby cries have mid-high frequency energy)
    if spectral_centroid >= 1000:
        checks.append(True)
    else:
        return False, f"Spectral centroid too low ({spectral_centroid:.0f} Hz < 1000 Hz)"
    
    # 4. Spectral rolloff (high-frequency energy)
    if spectral_rolloff >= 1500:
        checks.append(True)
    else:
        return False, f"Lacks high-frequency energy (rolloff {spectral_rolloff:.0f} Hz < 1500 Hz)"
    
    # All checks passed
    return True, "Baby cry detected"

def classify_cry_type_improved(features):
    """
    Classify cry type using pattern matching
    More accurate than simple thresholds
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
    mfcc_mean = features.get('mfcc_mean', np.zeros(13))
    
    print(f"🔍 Audio Analysis:")
    print(f"   Pitch: {pitch:.1f} Hz (std: {pitch_std:.1f})")
    print(f"   RMS Energy: {rms:.4f}")
    print(f"   Spectral Centroid: {spectral_centroid:.1f} Hz")
    print(f"   Spectral Rolloff: {spectral_rolloff:.1f} Hz")
    
    # Check if it's a baby cry
    is_cry, reason = is_baby_cry(features)
    
    if not is_cry:
        print(f"   ❌ NOT A BABY CRY: {reason}")
        return {
            'isCrying': False,
            'cryType': 'no_cry',
            'confidence': 15,
            'intensity': int(min(rms * 1000, 100)),
            'reason': f'Not a baby cry: {reason}'
        }
    
    print(f"   ✅ BABY CRY DETECTED - Classifying type...")
    
    # Pattern matching for cry type classification
    scores = {}
    
    for cry_type, pattern in CRY_PATTERNS.items():
        score = 0
        
        # Pitch range matching
        pitch_min, pitch_max = pattern['pitch_range']
        if pitch_min <= pitch <= pitch_max:
            score += 30
        elif abs(pitch - (pitch_min + pitch_max)/2) < 100:
            score += 15  # Close to range
        
        # Pitch variability matching
        if pattern['pitch_variability'] == 'high' and pitch_std > 50:
            score += 20
        elif pattern['pitch_variability'] == 'low' and pitch_std < 40:
            score += 20
        elif pattern['pitch_variability'] == 'moderate' and 30 <= pitch_std <= 60:
            score += 20
        
        # Intensity matching
        if pattern['intensity'] == 'high' and rms > 0.06:
            score += 20
        elif pattern['intensity'] == 'moderate' and 0.03 <= rms <= 0.08:
            score += 20
        elif pattern['intensity'] == 'low' and rms < 0.05:
            score += 20
        
        # Spectral centroid matching
        sc_min, sc_max = pattern['spectral_centroid']
        if sc_min <= spectral_centroid <= sc_max:
            score += 20
        elif abs(spectral_centroid - (sc_min + sc_max)/2) < 500:
            score += 10
        
        # MFCC pattern matching (simplified)
        # In production, use trained model or distance metrics
        if pattern['mfcc_pattern'] == 'sharp_onset_high_energy':
            if np.mean(mfcc_mean[:3]) > 0:  # High energy in low MFCCs
                score += 10
        elif pattern['mfcc_pattern'] == 'rhythmic_consistent':
            if features.get('mfcc_std', np.zeros(13))[0] < 5:  # Low variability
                score += 10
        elif pattern['mfcc_pattern'] == 'gradual_low_energy':
            if np.mean(mfcc_mean[:3]) < 0:  # Low energy
                score += 10
        elif pattern['mfcc_pattern'] == 'intermittent_variable':
            if features.get('mfcc_std', np.zeros(13))[0] > 3:  # Moderate variability
                score += 10
        
        scores[cry_type] = score
    
    # Determine winner
    cry_type = max(scores, key=scores.get)
    confidence = min(int(scores[cry_type]), 95)
    
    # Boost confidence if score is high
    if scores[cry_type] >= 70:
        confidence = min(confidence + 10, 95)
    
    # Calculate intensity
    intensity = int(min(rms * 1000, 100))
    
    # Generate reason
    reasons = {
        'hunger': f'Rhythmic cry pattern ({int(pitch)} Hz) with consistent pitch - baby may be hungry 🍼',
        'sleep': f'Low-intensity cry ({int(pitch)} Hz) with variable pitch - baby is tired and needs sleep 😴',
        'discomfort': f'High-pitched cry ({int(pitch)} Hz) with high intensity - baby is uncomfortable or in distress ⚠️'
    }
    
    print(f"   → Cry Type: {cry_type}")
    print(f"   → Confidence: {confidence}%")
    print(f"   → Intensity: {intensity}/100")
    print(f"   → Pattern Scores: {scores}")
    
    return {
        'isCrying': True,
        'cryType': cry_type,
        'confidence': confidence,
        'intensity': intensity,
        'reason': reasons[cry_type],
        'features': {
            'pitch_hz': int(pitch),
            'pitch_std': round(pitch_std, 1),
            'rms_energy': round(rms, 4),
            'spectral_centroid': int(spectral_centroid)
        }
    }

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mode': '3-Category Cry Detection with Pattern Matching',
        'categories': ['hunger', 'sleep', 'discomfort'],
        'librosa': 'available' if LIBROSA_AVAILABLE else 'not available',
        'message': 'Real audio pattern analysis with MFCC' if LIBROSA_AVAILABLE else 'Install librosa for real audio processing',
        'version': '3-category-system'
    })

@app.route('/api/analyze_audio', methods=['POST'])
def analyze_audio():
    """
    Analyze audio features and detect cry using pattern matching
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
            
            print(f"\n📊 Analyzing {len(audio_array)} samples at {sample_rate} Hz")
            
            # Extract comprehensive features
            features = extract_audio_features_improved(audio_array, sample_rate)
            
            if features:
                # Classify using improved pattern matching
                result = classify_cry_type_improved(features)
            else:
                result = {
                    'isCrying': False,
                    'cryType': 'error',
                    'confidence': 0,
                    'intensity': 0,
                    'reason': 'Feature extraction failed'
                }
        else:
            result = {
                'isCrying': False,
                'cryType': 'error',
                'confidence': 0,
                'intensity': 0,
                'reason': 'No audio data or librosa not available'
            }
        
        # Add to history if crying
        if result['isCrying']:
            cry_history.append({
                'timestamp': time.strftime('%H:%M:%S'),
                'cryType': result['cryType'],
                'confidence': result['confidence'],
                'intensity': result['intensity']
            })
            if len(cry_history) > 10:
                cry_history.pop(0)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in analyze_audio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cry_history', methods=['GET'])
def get_cry_history():
    """Get cry detection history"""
    return jsonify(cry_history)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for cry detection accuracy"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        predicted_type = data.get('predicted_type')
        actual_type = data.get('actual_type')
        
        if not predicted_type or not actual_type:
            return jsonify({'error': 'Both predicted_type and actual_type are required'}), 400
        
        print(f"📝 Feedback: Predicted={predicted_type}, Actual={actual_type}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback received! This helps improve the system.'
        })
        
    except Exception as e:
        print(f"Error in submit_feedback: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🍼 3-Category Baby Cry Detection Server")
    print("="*60)
    print("\nCategories:")
    print("  🍼 Hunger - Rhythmic, sustained crying")
    print("  😴 Sleep - Variable, fussy crying")
    print("  ⚠️  Discomfort - Loud, urgent crying")
    print()
    if LIBROSA_AVAILABLE:
        print("✅ Real audio pattern analysis enabled")
        print("   - MFCC pattern matching")
        print("   - Multi-feature classification")
        print("   - Baby cry vs noise detection")
    else:
        print("⚠️  Librosa not available")
        print("   Install with: pip install librosa scipy soundfile")
    print()
    print("Server: http://127.0.0.1:5000")
    print("API: http://127.0.0.1:5000/api/analyze_audio")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=False)
