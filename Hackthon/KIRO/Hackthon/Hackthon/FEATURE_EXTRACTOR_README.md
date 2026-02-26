# Feature Extractor Module

## Overview

The `feature_extractor.py` module provides comprehensive audio feature extraction functionality for the Neonatal Cry Detection System. It extracts acoustic features from preprocessed audio signals that are used for cry classification.

## Requirements Implemented

This module implements the following requirements from the specification:

- **Requirement 3.1**: Pitch extraction using autocorrelation (via librosa's piptrack)
- **Requirement 3.2**: Frequency spectrum analysis using FFT
- **Requirement 3.3**: Intensity (RMS energy) calculation in dB scale
- **Requirement 3.4**: MFCC extraction (13 coefficients by default)
- **Requirement 3.5**: Duration calculation in seconds
- **Requirement 3.6**: Complete feature dictionary with all extracted features

## Class: FeatureExtractor

### Initialization

```python
from feature_extractor import FeatureExtractor

extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)
```

**Parameters:**
- `sample_rate` (int): Audio sample rate in Hz (default: 16000)
- `n_mfcc` (int): Number of MFCC coefficients to extract (default: 13)

### Methods

#### 1. `extract_pitch(audio: np.ndarray) -> float`

Extracts the fundamental frequency (F0) using librosa's piptrack algorithm.

**Parameters:**
- `audio`: Input audio signal as numpy array

**Returns:**
- Fundamental frequency in Hz (0.0 if pitch cannot be detected)

**Features:**
- Focuses on typical infant cry range (200-600 Hz)
- Returns median pitch across all frames for robustness
- Handles invalid values (NaN, Inf) gracefully

**Example:**
```python
pitch = extractor.extract_pitch(audio)
print(f"Pitch: {pitch:.2f} Hz")
```

#### 2. `extract_frequency_spectrum(audio: np.ndarray) -> np.ndarray`

Computes the power spectral density using FFT.

**Parameters:**
- `audio`: Input audio signal as numpy array

**Returns:**
- Normalized power spectral density as numpy array

**Features:**
- Uses FFT with appropriate window size
- Normalizes spectrum to sum to 1
- Focuses on frequency range relevant for infant cries (0-2000 Hz)

**Example:**
```python
spectrum = extractor.extract_frequency_spectrum(audio)
print(f"Spectrum shape: {spectrum.shape}")
```

#### 3. `extract_intensity(audio: np.ndarray) -> float`

Computes RMS energy of the signal in decibel scale.

**Parameters:**
- `audio`: Input audio signal as numpy array

**Returns:**
- RMS energy in dB (0.0 if audio is silent)

**Features:**
- Calculates root mean square (RMS) energy
- Converts to dB scale for better interpretability
- Handles silent signals with floor value of -100 dB

**Example:**
```python
intensity = extractor.extract_intensity(audio)
print(f"Intensity: {intensity:.2f} dB")
```

#### 4. `extract_mfccs(audio: np.ndarray) -> np.ndarray`

Extracts Mel-Frequency Cepstral Coefficients.

**Parameters:**
- `audio`: Input audio signal as numpy array

**Returns:**
- Array of n_mfcc MFCC coefficients (zeros if extraction fails)

**Features:**
- Captures spectral envelope of audio signal
- Returns mean MFCC values across all frames
- Configurable number of coefficients (default: 13)

**Example:**
```python
mfccs = extractor.extract_mfccs(audio)
print(f"MFCCs: {mfccs}")
```

#### 5. `extract_duration(audio: np.ndarray) -> float`

Computes duration of the audio signal in seconds.

**Parameters:**
- `audio`: Input audio signal as numpy array

**Returns:**
- Duration in seconds

**Example:**
```python
duration = extractor.extract_duration(audio)
print(f"Duration: {duration:.3f} seconds")
```

#### 6. `extract_all_features(audio: np.ndarray) -> Dict[str, Any]`

**Main method** - Extracts complete feature vector from audio signal.

**Parameters:**
- `audio`: Input audio signal as numpy array

**Returns:**
Dictionary containing all extracted features:
- `pitch` (float): Fundamental frequency in Hz
- `pitch_std` (float): Standard deviation of pitch values
- `intensity` (float): RMS energy in dB
- `intensity_std` (float): Standard deviation of intensity values
- `mfccs` (np.ndarray): Array of 13 MFCC coefficients
- `spectral_centroid` (float): Center of mass of spectrum in Hz
- `spectral_rolloff` (float): Frequency below which 85% of energy is contained
- `zero_crossing_rate` (float): Rate of sign changes (normalized)
- `duration` (float): Duration in seconds
- `frequency_spectrum` (np.ndarray): Power spectral density array

**Example:**
```python
features = extractor.extract_all_features(audio)

print(f"Pitch: {features['pitch']:.2f} Hz")
print(f"Intensity: {features['intensity']:.2f} dB")
print(f"Duration: {features['duration']:.3f} seconds")
print(f"MFCCs: {features['mfccs']}")
```

### Additional Helper Methods

#### `extract_spectral_centroid(audio: np.ndarray) -> float`
Computes the spectral centroid (center of mass of spectrum). Higher values indicate brighter sounds.

#### `extract_spectral_rolloff(audio: np.ndarray) -> float`
Computes the frequency below which 85% of spectral energy is contained.

#### `extract_zero_crossing_rate(audio: np.ndarray) -> float`
Computes the rate at which the signal changes sign (simple frequency measure).

#### `extract_pitch_std(audio: np.ndarray) -> float`
Computes standard deviation of pitch values (measures pitch variation).

#### `extract_intensity_std(audio: np.ndarray) -> float`
Computes standard deviation of intensity values (measures energy variation).

## Usage Example

```python
import numpy as np
from feature_extractor import FeatureExtractor

# Initialize extractor
extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)

# Load or generate audio (example: 1 second of audio)
audio = np.random.randn(16000)  # Replace with actual audio data

# Extract all features
features = extractor.extract_all_features(audio)

# Access individual features
print(f"Pitch: {features['pitch']:.2f} Hz")
print(f"Intensity: {features['intensity']:.2f} dB")
print(f"Duration: {features['duration']:.3f} seconds")
print(f"Number of MFCCs: {len(features['mfccs'])}")
print(f"Spectral centroid: {features['spectral_centroid']:.2f} Hz")
```

## Integration with Preprocessing

The FeatureExtractor is designed to work with preprocessed audio from the AudioPreprocessor:

```python
from audio_preprocessor import AudioPreprocessor
from feature_extractor import FeatureExtractor

# Initialize both modules
preprocessor = AudioPreprocessor(sample_rate=16000)
extractor = FeatureExtractor(sample_rate=16000, n_mfcc=13)

# Process audio
raw_audio = capture_audio()  # Your audio capture function
preprocessed_audio = preprocessor.preprocess(raw_audio)
features = extractor.extract_all_features(preprocessed_audio)
```

## Error Handling

The FeatureExtractor handles various edge cases gracefully:

1. **Empty audio**: Returns default values (0.0 for scalars, zeros for arrays)
2. **Invalid values (NaN, Inf)**: Automatically sanitized using `np.nan_to_num`
3. **Very short audio**: Processes correctly with appropriate window sizes
4. **Silence**: Returns valid features with low intensity values
5. **Extraction failures**: Returns default values and continues processing

## Testing

### Unit Tests

Comprehensive unit tests are provided in `tests/test_feature_extractor.py`:

```bash
pytest tests/test_feature_extractor.py -v
```

### Simple Test Script

A standalone test script is available for quick verification:

```bash
python test_feature_extractor_simple.py
```

This script tests:
- Basic functionality of all extraction methods
- Edge cases (empty audio, silence, short audio, invalid values)
- Requirements validation
- Feature completeness

## Performance Considerations

- **Pitch extraction**: Most computationally expensive operation (~50-100ms for 1s audio)
- **MFCC extraction**: Moderate cost (~20-50ms for 1s audio)
- **Other features**: Fast (<10ms each for 1s audio)
- **Total extraction time**: Typically <200ms for 1s audio segment

## Dependencies

- `numpy`: Array operations and numerical computing
- `librosa`: Audio feature extraction (pitch, MFCCs, spectral features)
- `scipy`: Signal processing (used by librosa)

## Notes

1. **Pitch detection range**: Optimized for infant cries (200-600 Hz)
2. **MFCC coefficients**: Default 13 coefficients, configurable
3. **Sample rate**: Default 16kHz, should match audio capture rate
4. **Feature normalization**: Some features (spectrum) are normalized, others are in natural units
5. **Robustness**: All methods handle edge cases and invalid inputs gracefully

## Future Enhancements

Potential improvements for future versions:

1. Add formant frequency extraction
2. Implement jitter and shimmer measurements
3. Add temporal feature extraction (onset detection, rhythm)
4. Support batch processing for multiple audio segments
5. Add feature caching for repeated extractions
6. Implement GPU acceleration for large-scale processing

## Task Completion

This module completes **Task 3.1** from the implementation plan:

✅ Implement pitch extraction using autocorrelation/librosa  
✅ Implement frequency spectrum analysis  
✅ Implement intensity (RMS energy) calculation  
✅ Implement MFCC extraction (13 coefficients)  
✅ Implement duration calculation  
✅ Implement `extract_all_features()` returning complete feature dictionary  
✅ Validates Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
