# Design Document: Neonatal Cry Detection and Classification

## Overview

This design describes an intelligent neonatal cry detection and classification system that extends the existing YAMNet-based cry detection in the Hackthon application. The system will capture real-time audio, preprocess signals, extract acoustic features, classify cry patterns into five categories (hunger, sleep discomfort, pain/distress, diaper change, normal/unknown), and provide immediate alerts to caregivers with visual indicators.

The design builds upon the existing `cry_detection_yamnet.py` implementation by adding:
- Enhanced audio preprocessing with noise reduction and segmentation
- Comprehensive feature extraction (pitch, frequency, intensity, MFCCs, duration)
- Multi-class cry classification with confidence scoring
- Rich alert generation with color-coded visual indicators
- Caregiver feedback collection for continuous learning
- Privacy-preserving local processing

### Key Design Decisions

1. **Hybrid Model Approach**: Use YAMNet for initial cry detection, then apply a specialized classifier for cry type categorization
2. **Local Processing**: All audio processing and classification happens on-device to protect privacy
3. **Modular Architecture**: Separate components for audio processing, feature extraction, classification, and alerting to support future enhancements
4. **Backward Compatibility**: Extend existing `CryDetector` class to maintain integration with `main.py` and `shared_data.py`

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Neonatal Cry Detection System            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Audio      │─────▶│   Audio      │─────▶│  Feature  │ │
│  │   Capture    │      │ Preprocessor │      │ Extractor │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      │                     ▼       │
│         │                      │              ┌───────────┐ │
│         │                      │              │    Cry    │ │
│         │                      │              │ Classifier│ │
│         │                      │              └───────────┘ │
│         │                      │                     │       │
│         │                      │                     ▼       │
│         │                      │              ┌───────────┐ │
│         │                      └─────────────▶│   Alert   │ │
│         │                                     │  Manager  │ │
│         │                                     └───────────┘ │
│         │                                            │       │
│         │                                            ▼       │
│         │                                     ┌───────────┐ │
│         └────────────────────────────────────▶│ Feedback  │ │
│                                               │  System   │ │
│                                               └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Interactions

1. **Audio Capture** continuously records audio from microphone or external monitor
2. **Audio Preprocessor** applies noise reduction, segmentation, and normalization
3. **Feature Extractor** computes acoustic features (pitch, frequency, MFCCs, etc.)
4. **Cry Classifier** uses YAMNet + specialized model to classify cry type
5. **Alert Manager** generates and displays notifications with visual indicators
6. **Feedback System** collects caregiver corrections for model improvement

## Components and Interfaces

### 1. Audio Capture Module

**Responsibility**: Capture real-time audio from device microphone or external baby monitor

**Interface**:
```python
class AudioCapture:
    def __init__(self, sample_rate: int = 16000, buffer_duration: float = 1.0):
        """Initialize audio capture with specified sample rate and buffer size"""
        
    def start_capture(self) -> None:
        """Begin continuous audio capture in background thread"""
        
    def stop_capture(self) -> None:
        """Stop audio capture and release resources"""
        
    def get_audio_buffer(self) -> np.ndarray:
        """Return the most recent audio buffer as numpy array"""
        
    def is_capturing(self) -> bool:
        """Check if audio capture is active"""
```

**Implementation Notes**:
- Uses `sounddevice` library (already in use) for cross-platform audio capture
- Maintains a circular buffer of 1-second audio segments
- Runs in a separate thread to avoid blocking main application
- Handles device connection/disconnection gracefully

### 2. Audio Preprocessor Module

**Responsibility**: Clean and normalize audio signals for feature extraction

**Interface**:
```python
class AudioPreprocessor:
    def __init__(self, sample_rate: int = 16000):
        """Initialize preprocessor with target sample rate"""
        
    def reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """Apply spectral subtraction to reduce background noise"""
        
    def segment_audio(self, audio: np.ndarray, threshold: float = 0.02) -> List[np.ndarray]:
        """Segment audio into cry episodes based on energy threshold"""
        
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio amplitude to consistent level"""
        
    def preprocess(self, audio: np.ndarray) -> np.ndarray:
        """Apply full preprocessing pipeline"""
```

**Implementation Notes**:
- **Noise Reduction**: Use spectral subtraction or Wiener filtering to remove background noise
- **Segmentation**: Detect cry episodes using short-time energy and zero-crossing rate
- **Normalization**: Scale audio to [-1, 1] range using peak normalization
- Processing time target: < 500ms per 1-second segment

### 3. Feature Extractor Module

**Responsibility**: Extract acoustic features from preprocessed audio

**Interface**:
```python
class FeatureExtractor:
    def __init__(self, sample_rate: int = 16000, n_mfcc: int = 13):
        """Initialize feature extractor with parameters"""
        
    def extract_pitch(self, audio: np.ndarray) -> float:
        """Extract fundamental frequency (F0) using autocorrelation"""
        
    def extract_frequency_spectrum(self, audio: np.ndarray) -> np.ndarray:
        """Compute power spectral density"""
        
    def extract_intensity(self, audio: np.ndarray) -> float:
        """Compute RMS energy of signal"""
        
    def extract_mfccs(self, audio: np.ndarray) -> np.ndarray:
        """Extract Mel-Frequency Cepstral Coefficients"""
        
    def extract_duration(self, audio: np.ndarray) -> float:
        """Compute duration of cry episode in seconds"""
        
    def extract_all_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract complete feature vector"""
```

**Implementation Notes**:
- Use `librosa` library for audio feature extraction
- **Pitch**: Autocorrelation or YIN algorithm for F0 estimation
- **Frequency**: FFT-based spectral analysis focusing on 200-600 Hz range (typical infant cry)
- **Intensity**: RMS energy normalized to dB scale
- **MFCCs**: 13 coefficients capturing spectral envelope
- **Duration**: Time from cry onset to offset
- Return features as dictionary for flexibility

### 4. Cry Classifier Module

**Responsibility**: Classify cry patterns into predefined categories with confidence scores

**Interface**:
```python
class CryClassifier:
    def __init__(self, model_path: Optional[str] = None):
        """Initialize classifier with optional custom model"""
        
    def load_yamnet(self) -> None:
        """Load YAMNet model for initial cry detection"""
        
    def load_cry_type_model(self) -> None:
        """Load specialized cry type classification model"""
        
    def detect_cry(self, audio: np.ndarray) -> Tuple[bool, float]:
        """Use YAMNet to detect if audio contains crying"""
        
    def classify_cry_type(self, features: Dict[str, Any]) -> Tuple[str, float]:
        """Classify cry into specific category with confidence"""
        
    def predict(self, audio: np.ndarray, features: Dict[str, Any]) -> Dict[str, Any]:
        """Complete prediction pipeline"""
```

**Implementation Notes**:
- **Two-Stage Classification**:
  1. YAMNet detects presence of crying (binary: crying/not crying)
  2. Specialized model classifies cry type (5 categories)
- **Cry Type Model Options**:
  - Option A: Fine-tuned YAMNet embeddings + small neural network
  - Option B: Random Forest on extracted features
  - Option C: Lightweight CNN trained on spectrograms
- **Confidence Thresholding**:
  - Confidence < 60%: Classify as "normal/unknown"
  - Confidence ≥ 60%: Return specific category
- **Categories**: hunger, sleep_discomfort, pain_distress, diaper_change, normal_unknown
- Target inference time: < 1 second

### 5. Alert Manager Module

**Responsibility**: Generate and display notifications with visual indicators

**Interface**:
```python
class AlertManager:
    def __init__(self):
        """Initialize alert manager"""
        
    def generate_alert(self, cry_type: str, confidence: float) -> Dict[str, Any]:
        """Create alert message with visual indicators"""
        
    def get_alert_message(self, cry_type: str) -> str:
        """Map cry type to human-readable message"""
        
    def get_alert_color(self, cry_type: str) -> str:
        """Get color code for cry type"""
        
    def get_alert_icon(self, cry_type: str) -> str:
        """Get icon identifier for cry type"""
        
    def update_dashboard(self, alert_data: Dict[str, Any]) -> None:
        """Update shared_data structure with alert information"""
```

**Implementation Notes**:
- **Message Mapping**:
  - hunger → "Baby may be hungry"
  - sleep_discomfort → "Baby may be uncomfortable"
  - pain_distress → "Baby shows signs of pain – immediate attention needed"
  - diaper_change → "Baby may need a diaper change"
  - normal_unknown → "Baby is crying – reason unclear"
- **Color Coding**:
  - pain_distress → Red (#ef4444)
  - hunger/sleep_discomfort/diaper_change → Yellow (#f59e0b)
  - normal_unknown → Green (#10b981)
- **Icons**: Use emoji or icon identifiers (🍼 hunger, 😴 sleep, ⚠️ pain, 🧷 diaper, ❓ unknown)
- Integrates with existing `shared_data.py` dashboard structure

### 6. Feedback System Module

**Responsibility**: Collect caregiver corrections for model improvement

**Interface**:
```python
class FeedbackSystem:
    def __init__(self, storage_path: str = "./feedback_data"):
        """Initialize feedback system with storage location"""
        
    def record_feedback(self, 
                       features: Dict[str, Any],
                       predicted_type: str,
                       actual_type: str,
                       confidence: float,
                       timestamp: float) -> None:
        """Store feedback entry"""
        
    def get_feedback_data(self) -> List[Dict[str, Any]]:
        """Retrieve all feedback entries for retraining"""
        
    def export_feedback(self, output_path: str) -> None:
        """Export feedback data to file for model retraining"""
```

**Implementation Notes**:
- Store feedback as JSON files with feature vectors and labels
- Do NOT store raw audio (privacy requirement)
- Include metadata: timestamp, original prediction, corrected label, confidence
- Feedback data can be used for periodic model retraining
- Storage location: `./feedback_data/` directory

### 7. Enhanced CryDetector Class

**Responsibility**: Main orchestrator that integrates all components and maintains backward compatibility

**Interface**:
```python
class CryDetector:
    def __init__(self):
        """Initialize all sub-components"""
        
    def detect(self) -> Dict[str, Any]:
        """Main detection method called by main.py"""
        
    def process_audio_pipeline(self, audio: np.ndarray) -> Dict[str, Any]:
        """Execute full processing pipeline"""
        
    def submit_feedback(self, predicted_type: str, actual_type: str) -> None:
        """Allow caregiver to provide feedback"""
```

**Implementation Notes**:
- Extends existing `CryDetector` in `cry_detection_yamnet.py`
- Maintains same `detect()` interface for compatibility with `main.py`
- Returns enhanced data structure with cry type, confidence, and alert information
- Coordinates all sub-components

## Data Models

### Audio Data

```python
@dataclass
class AudioSegment:
    """Represents a segment of captured audio"""
    data: np.ndarray          # Audio samples
    sample_rate: int          # Sampling rate (Hz)
    duration: float           # Duration (seconds)
    timestamp: float          # Capture timestamp
```

### Feature Vector

```python
@dataclass
class CryFeatures:
    """Acoustic features extracted from cry audio"""
    pitch: float              # Fundamental frequency (Hz)
    pitch_std: float          # Pitch variation
    intensity: float          # RMS energy (dB)
    intensity_std: float      # Energy variation
    mfccs: np.ndarray        # 13 MFCC coefficients
    spectral_centroid: float  # Center of mass of spectrum
    spectral_rolloff: float   # Frequency below which 85% of energy is contained
    zero_crossing_rate: float # Rate of sign changes
    duration: float           # Cry duration (seconds)
    
    def to_vector(self) -> np.ndarray:
        """Convert to flat numpy array for model input"""
```

### Classification Result

```python
@dataclass
class CryClassification:
    """Result of cry classification"""
    is_crying: bool           # Whether crying was detected
    cry_type: str            # Category: hunger, sleep_discomfort, pain_distress, diaper_change, normal_unknown
    confidence: float         # Confidence score (0-100)
    features: CryFeatures    # Extracted features
    timestamp: float          # Classification timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
```

### Alert Data

```python
@dataclass
class CryAlert:
    """Alert information for display"""
    message: str              # Human-readable alert message
    cry_type: str            # Cry category
    confidence: float         # Confidence score
    color: str               # Color code for visual indicator
    icon: str                # Icon identifier
    timestamp: float          # Alert generation time
    severity: str            # low, medium, high
```

### Feedback Entry

```python
@dataclass
class FeedbackEntry:
    """Caregiver feedback for model improvement"""
    features: CryFeatures     # Audio features
    predicted_type: str       # Model's prediction
    actual_type: str         # Caregiver's correction
    confidence: float         # Original confidence score
    timestamp: float          # Feedback submission time
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*



### Property 1: Audio Buffer Segmentation
*For any* duration of audio capture, the audio buffer should contain segments of exactly 1 second duration (±10ms tolerance for timing precision).
**Validates: Requirements 1.3**

### Property 2: Noise Reduction Effectiveness
*For any* audio signal with added synthetic noise, applying noise reduction should result in a signal with lower RMS energy in the noise frequency bands compared to the original noisy signal.
**Validates: Requirements 2.1**

### Property 3: Silence Segmentation
*For any* audio containing periods of silence (energy below threshold), segmentation should split the audio into multiple non-silent segments, and no segment should contain silence periods longer than 100ms.
**Validates: Requirements 2.2**

### Property 4: Audio Normalization Range
*For any* audio signal, after normalization the amplitude values should fall within the range [-1.0, 1.0], and the peak amplitude should be close to 1.0 (within 0.95-1.0).
**Validates: Requirements 2.3**

### Property 5: Preprocessing Performance
*For any* 1-second audio segment, preprocessing (noise reduction + segmentation + normalization) should complete in less than 500 milliseconds.
**Validates: Requirements 2.5**

### Property 6: Complete Feature Extraction
*For any* valid preprocessed audio segment, the extracted feature vector should contain all required features: pitch, intensity, MFCCs (13 coefficients), spectral_centroid, spectral_rolloff, zero_crossing_rate, and duration, with no missing or null values.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

### Property 7: Valid Cry Classification Categories
*For any* feature vector input, the classifier should return exactly one of the five valid categories: "hunger", "sleep_discomfort", "pain_distress", "diaper_change", or "normal_unknown".
**Validates: Requirements 4.1**

### Property 8: Confidence Score Range
*For any* classification result, the confidence score should be a numeric value in the range [0, 100].
**Validates: Requirements 4.2**

### Property 9: Low Confidence Classification
*For any* classification with confidence score below 60, the cry type should be classified as "normal_unknown".
**Validates: Requirements 4.3, 10.3**

### Property 10: High Confidence Classification
*For any* classification with confidence score of 60 or higher, the cry type should be one of the four specific categories: "hunger", "sleep_discomfort", "pain_distress", or "diaper_change" (not "normal_unknown").
**Validates: Requirements 4.4**

### Property 11: Classification Performance
*For any* feature vector, classification should complete in less than 1 second.
**Validates: Requirements 4.5**

### Property 12: Alert Message Mapping
*For any* cry type, the alert manager should generate the correct corresponding message: hunger→"Baby may be hungry", sleep_discomfort→"Baby may be uncomfortable", pain_distress→"Baby shows signs of pain – immediate attention needed", diaper_change→"Baby may need a diaper change", normal_unknown→"Baby is crying – reason unclear".
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 13: Complete Alert Structure
*For any* generated alert, the alert data should contain all required fields: message (non-empty string), cry_type (valid category), confidence (numeric), color (valid hex color code), icon (non-empty string), and timestamp (positive number).
**Validates: Requirements 5.6, 5.7, 5.9**

### Property 14: Feedback Data Completeness
*For any* feedback submission, the stored feedback entry should contain all required fields: features (complete feature vector), predicted_type (valid category), actual_type (valid category), confidence (numeric), and timestamp (positive number).
**Validates: Requirements 6.3**

### Property 15: Feedback Retrieval
*For any* feedback entry that is stored, retrieving all feedback data should include that entry with all fields intact and unchanged.
**Validates: Requirements 6.4**

### Property 16: Raw Audio Disposal
*For any* audio processing operation, after feature extraction is complete, the raw audio data should not be retained in the system's memory or storage (verified by checking that audio arrays are dereferenced and not stored in any persistent structures).
**Validates: Requirements 8.2**

### Property 17: Feedback Privacy
*For any* stored feedback entry, the data should contain only feature vectors and labels, with no raw audio waveform data present in the stored structure.
**Validates: Requirements 8.3**

### Property 18: Noise Robustness
*For any* valid cry audio sample, adding background noise at various SNR levels (20dB, 15dB, 10dB) should not cause the classification accuracy to drop below 60% of the clean audio accuracy.
**Validates: Requirements 10.4**

### Property 19: Dashboard Update Completeness
*For any* cry detection result, updating the dashboard should set all required fields in shared_data["cryDetection"]: status, cryType, confidence, intensity, duration, and lastDetected.
**Validates: Requirements 11.2**

## Error Handling

### Audio Capture Errors

**Scenario**: Microphone access denied or device unavailable
- **Detection**: Catch `sounddevice` exceptions during initialization
- **Response**: Log error with details, set system status to "error", notify user via alert
- **Recovery**: Retry connection every 30 seconds, allow manual retry via API

**Scenario**: Audio buffer overflow (processing too slow)
- **Detection**: Monitor buffer fill level
- **Response**: Log warning, drop oldest frames to prevent memory issues
- **Recovery**: Increase buffer size or reduce sampling frequency

### Preprocessing Errors

**Scenario**: Invalid audio data (NaN, Inf values)
- **Detection**: Check for non-finite values after each preprocessing step
- **Response**: Replace invalid values with zeros, log warning
- **Recovery**: Continue processing with sanitized data

**Scenario**: Preprocessing timeout (> 500ms)
- **Detection**: Measure processing time
- **Response**: Log performance warning, continue with partial preprocessing
- **Recovery**: Skip expensive operations if consistently slow

### Feature Extraction Errors

**Scenario**: Feature extraction fails (e.g., pitch detection on silence)
- **Detection**: Catch exceptions from librosa functions
- **Response**: Return default feature values (zeros), log warning
- **Recovery**: Mark features as invalid, skip classification for this segment

**Scenario**: Missing or incomplete features
- **Detection**: Validate feature vector completeness
- **Response**: Fill missing features with defaults, log warning
- **Recovery**: Proceed with classification using available features

### Classification Errors

**Scenario**: Model loading fails
- **Detection**: Catch TensorFlow/model loading exceptions
- **Response**: Log critical error, set system to degraded mode
- **Recovery**: Retry loading, fall back to simple threshold-based detection

**Scenario**: Inference fails or times out
- **Detection**: Catch inference exceptions, measure inference time
- **Response**: Return "normal_unknown" with 0% confidence, log error
- **Recovery**: Retry inference once, then skip if still failing

### Alert Generation Errors

**Scenario**: Dashboard update fails
- **Detection**: Catch exceptions when updating shared_data
- **Response**: Log error, continue system operation
- **Recovery**: Retry update on next detection cycle

### Feedback System Errors

**Scenario**: Feedback storage fails (disk full, permissions)
- **Detection**: Catch file I/O exceptions
- **Response**: Log error, notify user that feedback wasn't saved
- **Recovery**: Retry with exponential backoff, clear old feedback if disk full

### Battery Management Errors

**Scenario**: Battery level detection unavailable
- **Detection**: Catch exceptions when querying battery status
- **Response**: Assume normal battery level, log warning
- **Recovery**: Continue normal operation without battery optimization

## Testing Strategy

### Dual Testing Approach

This system requires both **unit tests** and **property-based tests** for comprehensive validation:

- **Unit tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property tests**: Verify universal properties across all inputs through randomized testing

Both approaches are complementary and necessary. Unit tests catch concrete bugs and validate specific scenarios, while property tests verify general correctness across a wide input space.

### Property-Based Testing

**Framework**: Use `hypothesis` library for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each test must reference its design document property
- Tag format: `# Feature: neonatal-cry-detection, Property {number}: {property_text}`

**Test Data Generation**:
- **Audio signals**: Generate synthetic audio with controlled characteristics (frequency, amplitude, duration)
- **Noise**: Add white noise, pink noise, and environmental sounds at various SNR levels
- **Feature vectors**: Generate random but valid feature vectors within realistic ranges
- **Cry types**: Sample from all five categories uniformly
- **Confidence scores**: Generate values across full [0, 100] range

**Property Test Coverage**:
- Properties 1-19 should each have a corresponding property-based test
- Each test should generate diverse inputs and verify the property holds for all

### Unit Testing

**Framework**: Use `pytest` for Python unit testing

**Test Categories**:

1. **Component Integration Tests**:
   - Test AudioCapture → AudioPreprocessor → FeatureExtractor pipeline
   - Test FeatureExtractor → CryClassifier → AlertManager pipeline
   - Test CryDetector orchestration of all components
   - Test integration with existing main.py and shared_data.py

2. **Edge Case Tests**:
   - Empty audio (silence)
   - Very short audio (< 100ms)
   - Very loud audio (clipping)
   - Audio with extreme pitch (very high/low)
   - Confidence scores at exact thresholds (59.9%, 60.0%, 60.1%)

3. **Error Condition Tests**:
   - Microphone access denied
   - Invalid audio data (NaN, Inf)
   - Model loading failure
   - Disk full during feedback storage
   - Battery level detection failure

4. **Specific Example Tests**:
   - Test each cry type message mapping (hunger, sleep_discomfort, etc.)
   - Test color coding for each severity level
   - Test battery threshold behaviors (15%, 5%)
   - Test model accuracy on validation dataset
   - Test model recall for pain/distress category

5. **Performance Tests**:
   - Measure preprocessing time on standard audio
   - Measure classification time on standard features
   - Verify memory usage stays within bounds

**Mock Objects**:
- Mock `sounddevice` for audio capture testing
- Mock YAMNet model for faster testing
- Mock file system for feedback storage testing
- Mock battery API for power management testing

### Test Data Requirements

**Validation Dataset**:
- Minimum 100 labeled cry samples (20 per category)
- Diverse acoustic environments (quiet room, background noise, multiple babies)
- Recorded at 16kHz sample rate
- Labeled by multiple caregivers for ground truth

**Synthetic Test Data**:
- Generated sine waves at infant cry frequencies (200-600 Hz)
- White noise and pink noise samples
- Silence samples
- Mixed signals (cry + noise at various SNRs)

### Continuous Testing

**Pre-commit Checks**:
- Run all unit tests
- Run fast property tests (10 iterations)
- Check code coverage (target: > 80%)

**CI/CD Pipeline**:
- Run full unit test suite
- Run full property test suite (100 iterations)
- Run integration tests with mocked hardware
- Measure and report performance metrics
- Validate model accuracy on validation dataset

### Testing Priorities

**Critical (Must Pass)**:
- Property 9: Low confidence classification
- Property 10: High confidence classification
- Property 16: Raw audio disposal (privacy)
- Property 17: Feedback privacy
- Error handling for model loading failures

**High Priority**:
- Property 6: Complete feature extraction
- Property 7: Valid classification categories
- Property 12: Alert message mapping
- Property 13: Complete alert structure
- Integration with existing system

**Medium Priority**:
- Property 1-5: Audio preprocessing
- Property 11: Classification performance
- Property 18: Noise robustness
- Edge case handling

**Low Priority**:
- Performance optimization tests
- Battery management tests
- UI/UX validation

## Implementation Notes

### Technology Stack

- **Audio Processing**: `sounddevice` (capture), `librosa` (features), `scipy` (signal processing)
- **Machine Learning**: `tensorflow` + `tensorflow_hub` (YAMNet), `scikit-learn` (cry type classifier)
- **Testing**: `pytest` (unit tests), `hypothesis` (property tests)
- **Backend**: FastAPI (existing), Python 3.8+

### Model Training Approach

**Initial Model**:
- Use YAMNet embeddings as features
- Train simple classifier (Random Forest or small neural network) on embeddings
- Train on publicly available infant cry datasets (e.g., Baby Chillanto database)

**Continuous Learning**:
- Collect feedback data from caregivers
- Periodically retrain model with accumulated feedback
- A/B test new models before deployment
- Maintain model versioning

### Performance Optimization

- **Audio Processing**: Use NumPy vectorized operations
- **Feature Extraction**: Cache MFCC filterbanks
- **Classification**: Use TensorFlow Lite for mobile deployment
- **Memory**: Use circular buffers, clear old data promptly
- **Threading**: Run audio capture in separate thread from processing

### Privacy Considerations

- All processing happens on-device
- Raw audio never leaves the device
- Only feature vectors stored for feedback
- No cloud transmission unless explicitly enabled for model updates
- Clear user consent for any data collection

### Integration Strategy

1. **Phase 1**: Extend existing `CryDetector` class with new components
2. **Phase 2**: Add feature extraction and preprocessing modules
3. **Phase 3**: Integrate cry type classifier
4. **Phase 4**: Enhance alert generation with visual indicators
5. **Phase 5**: Add feedback system
6. **Phase 6**: Optimize performance and battery usage

### Deployment Considerations

- Package model weights with application
- Support model updates via API
- Graceful degradation if model unavailable
- Logging and monitoring for production issues
- User feedback mechanism for false positives/negatives
