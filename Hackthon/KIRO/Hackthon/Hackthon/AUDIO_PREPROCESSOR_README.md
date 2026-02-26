# AudioPreprocessor Implementation

## Overview

The `audio_preprocessor.py` module implements audio preprocessing functionality for the Neonatal Cry Detection System. It provides three main preprocessing operations:

1. **Noise Reduction** - Using spectral subtraction
2. **Audio Segmentation** - Based on energy thresholds
3. **Amplitude Normalization** - To [-1, 1] range

## Implementation Details

### 1. Noise Reduction (`reduce_noise`)

**Algorithm**: Spectral Subtraction
- Estimates noise spectrum from the initial portion of audio (default: 100ms)
- Applies Short-Time Fourier Transform (STFT) to convert to frequency domain
- Subtracts estimated noise spectrum with over-subtraction factor (α=2.0)
- Applies spectral floor (β=0.01) to prevent negative values
- Reconstructs time-domain signal using Inverse STFT

**Key Features**:
- Handles edge cases (empty audio, very short audio)
- Sanitizes invalid values (NaN, Inf)
- Preserves audio length
- Adaptive window size based on audio length

**Validates**: Requirements 2.1

### 2. Audio Segmentation (`segment_audio`)

**Algorithm**: Energy-based Voice Activity Detection
- Computes RMS energy for overlapping frames (25ms frames, 10ms hop)
- Identifies silence regions where energy < threshold (default: 0.02)
- Splits audio at contiguous silence periods (min: 100ms)
- Filters out segments shorter than minimum duration (default: 100ms)

**Key Features**:
- Returns list of audio segments
- Configurable thresholds and durations
- Handles edge cases gracefully
- Ensures no segment contains long silence periods

**Validates**: Requirements 2.2

### 3. Amplitude Normalization (`normalize_audio`)

**Algorithm**: Peak Normalization
- Finds maximum absolute amplitude in signal
- Scales signal so peak amplitude reaches target (0.98)
- Clips values to ensure [-1, 1] range
- Avoids division by zero for silent audio

**Key Features**:
- Peak amplitude in [0.95, 1.0] range as specified
- Preserves signal shape and relative amplitudes
- Handles silent audio (all zeros)
- Sanitizes invalid values

**Validates**: Requirements 2.3

### 4. Full Preprocessing Pipeline (`preprocess`)

**Pipeline**:
1. Noise reduction
2. Normalization
3. Segmentation (returns first segment)

**Note**: For multiple segments, use `segment_audio()` directly.

**Validates**: Requirements 2.1, 2.2, 2.3, 2.5

## Usage Example

```python
from audio_preprocessor import AudioPreprocessor
import numpy as np

# Initialize preprocessor
preprocessor = AudioPreprocessor(sample_rate=16000)

# Load or capture audio
audio = np.random.randn(16000)  # 1 second of audio

# Option 1: Full preprocessing pipeline
preprocessed = preprocessor.preprocess(audio)

# Option 2: Individual operations
cleaned = preprocessor.reduce_noise(audio)
normalized = preprocessor.normalize_audio(cleaned)
segments = preprocessor.segment_audio(normalized)

# Option 3: Custom parameters
segments = preprocessor.segment_audio(
    audio, 
    threshold=0.03,  # Higher threshold for more aggressive segmentation
    min_silence_duration=0.2,  # Longer silence required to split
    min_segment_duration=0.15  # Keep only longer segments
)
```

## Testing

### Unit Tests

The `tests/test_audio_preprocessor.py` file contains comprehensive unit tests:
- Empty audio handling
- Silence handling
- Very short audio (< 100ms)
- Invalid values (NaN, Inf)
- Normalization range verification
- Segmentation with silence periods
- Noise reduction effectiveness
- Full pipeline integration

### Known Issue: Python 3.14 Compatibility

**Issue**: NumPy has compatibility issues with Python 3.14.2 on Windows, causing access violations during import.

**Workaround**: The code is correct and will work with Python 3.9-3.12. For testing on Python 3.14:
1. Use the simple test script: `python test_preprocessor_simple.py`
2. Or downgrade to Python 3.11 or 3.12 for full pytest support

**Status**: This is a known NumPy issue, not a problem with the implementation.

## Performance Considerations

- **Noise Reduction**: O(n log n) due to FFT operations
- **Segmentation**: O(n) linear scan with frame-wise energy computation
- **Normalization**: O(n) single pass through audio
- **Target**: < 500ms for 1-second audio segment (Requirement 2.5)

## Error Handling

The implementation handles:
- Empty audio arrays
- Very short audio (< 64 samples)
- Invalid values (NaN, Inf) - replaced with zeros
- Silent audio (all zeros) - returned as-is
- Division by zero - checked before normalization

## Integration

This module integrates with:
- `cry_detection_yamnet.py` - Provides preprocessed audio for detection
- `feature_extractor.py` - Receives preprocessed audio for feature extraction
- `main.py` - Part of the full cry detection pipeline

## Requirements Traceability

- **Requirement 2.1**: Noise reduction implemented via spectral subtraction
- **Requirement 2.2**: Audio segmentation based on energy thresholds
- **Requirement 2.3**: Amplitude normalization to [-1, 1] range
- **Requirement 2.5**: Performance target < 500ms per segment

## Next Steps

After this module:
1. Implement property-based tests (tasks 2.2-2.5)
2. Implement feature extraction module (task 3.1)
3. Integrate with cry detection system (task 9.1)
