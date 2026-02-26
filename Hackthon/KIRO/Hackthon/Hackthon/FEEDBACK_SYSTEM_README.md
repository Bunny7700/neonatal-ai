# FeedbackSystem Module

## Overview

The `FeedbackSystem` class provides functionality for collecting and storing caregiver feedback to improve the neonatal cry detection model over time. It implements privacy-preserving feedback collection by storing only feature vectors and labels, never raw audio data.

## Requirements

- **Requirement 6.3**: Store feedback with associated audio features and original prediction
- **Requirement 6.4**: Make feedback data available for model retraining
- **Requirement 8.3**: Store only feature vectors and labels, not raw audio recordings

## Features

### Core Functionality

1. **Feedback Recording** (`record_feedback`)
   - Stores caregiver corrections along with extracted audio features
   - Saves each feedback entry as a separate JSON file
   - Includes timestamp, predicted type, actual type, confidence, and features
   - **Privacy**: Never stores raw audio data

2. **Feedback Retrieval** (`get_feedback_data`)
   - Retrieves all feedback entries from storage
   - Returns entries sorted by timestamp (oldest first)
   - Deserializes features back to appropriate types

3. **Feedback Export** (`export_feedback`)
   - Consolidates all feedback entries into a single JSON file
   - Suitable for batch model retraining
   - Includes metadata (export timestamp, total entries)

4. **Feedback Count** (`get_feedback_count`)
   - Returns the total number of stored feedback entries
   - Useful for monitoring feedback collection progress

5. **Feedback Summary** (`get_feedback_summary`)
   - Provides statistics about stored feedback
   - Shows distribution by predicted and actual types
   - Calculates correction rate (percentage of incorrect predictions)

6. **Feedback Clearing** (`clear_feedback`)
   - Removes all stored feedback entries
   - Use with caution - permanently deletes data

## Usage

### Basic Usage

```python
from feedback_system import FeedbackSystem

# Initialize with storage path
fs = FeedbackSystem(storage_path="./feedback_data")

# Record feedback
features = {
    'pitch': 350.5,
    'intensity': -22.5,
    'mfccs': [1.2, 3.4, 5.6, ...],  # Can be list or numpy array
    'duration': 1.5
}

success = fs.record_feedback(
    features=features,
    predicted_type='hunger',
    actual_type='pain_distress',  # Caregiver's correction
    confidence=65.5
)

# Retrieve all feedback
feedback_data = fs.get_feedback_data()
print(f"Total feedback entries: {len(feedback_data)}")

# Export for model retraining
fs.export_feedback("feedback_export.json")

# Get summary statistics
summary = fs.get_feedback_summary()
print(f"Correction rate: {summary['correction_rate']:.1f}%")
```

### Integration with Cry Detection System

```python
from cry_classifier import CryClassifier
from feature_extractor import FeatureExtractor
from feedback_system import FeedbackSystem

# Initialize components
classifier = CryClassifier()
extractor = FeatureExtractor()
feedback_system = FeedbackSystem()

# Process audio and get prediction
features = extractor.extract_all_features(audio)
result = classifier.predict(audio, features)

# Display prediction to caregiver
print(f"Predicted: {result['cry_type']} (confidence: {result['confidence']:.1f}%)")

# Caregiver provides correction
actual_type = get_caregiver_input()  # e.g., from UI

# Record feedback
feedback_system.record_feedback(
    features=features,
    predicted_type=result['cry_type'],
    actual_type=actual_type,
    confidence=result['confidence']
)
```

## Data Structure

### Feedback Entry Format

Each feedback entry is stored as a JSON file with the following structure:

```json
{
  "timestamp": 1234567890.0,
  "datetime": "2009-02-13T23:31:30",
  "predicted_type": "hunger",
  "actual_type": "pain_distress",
  "confidence": 65.5,
  "features": {
    "pitch": 350.5,
    "pitch_std": 25.3,
    "intensity": -22.5,
    "intensity_std": 5.2,
    "mfccs": [1.2, 3.4, 5.6, ...],
    "spectral_centroid": 450.0,
    "spectral_rolloff": 800.0,
    "zero_crossing_rate": 0.15,
    "duration": 1.5,
    "frequency_spectrum": [0.1, 0.2, ...]
  }
}
```

### Export Format

The export file consolidates all feedback entries:

```json
{
  "export_timestamp": 1234567890.0,
  "export_datetime": "2009-02-13T23:31:30",
  "total_entries": 100,
  "feedback_entries": [
    { /* feedback entry 1 */ },
    { /* feedback entry 2 */ },
    ...
  ]
}
```

## Privacy Considerations

The FeedbackSystem is designed with privacy as a core principle:

1. **No Raw Audio Storage**: Only feature vectors are stored, never raw audio waveforms
2. **Local Storage**: All feedback is stored locally on the device
3. **Minimal Data**: Only essential features and labels are stored
4. **User Control**: Caregivers can skip providing feedback without blocking system operation

### Forbidden Fields

The following fields are **never** stored in feedback data:
- `audio`
- `raw_audio`
- `waveform`
- `samples`
- `signal`

Any attempt to include these fields will be filtered out during serialization.

## Storage

### File Organization

```
feedback_data/
├── feedback_1234567890000.json
├── feedback_1234567891000.json
├── feedback_1234567892000.json
└── ...
```

Each feedback entry is stored as a separate JSON file with a timestamp-based filename. This approach:
- Prevents data loss if one file is corrupted
- Allows incremental feedback collection
- Simplifies concurrent access

### Storage Location

By default, feedback is stored in `./feedback_data/` directory. You can specify a custom location:

```python
fs = FeedbackSystem(storage_path="/path/to/custom/location")
```

## Error Handling

The FeedbackSystem handles errors gracefully:

- **Storage Directory Creation**: Automatically creates the storage directory if it doesn't exist
- **File I/O Errors**: Logs errors and returns False on failure
- **Corrupted Files**: Skips corrupted files during retrieval and continues processing
- **Missing Storage**: Returns empty results if storage directory doesn't exist

## Testing

### Unit Tests

Run the unit tests with pytest:

```bash
pytest tests/test_feedback_system.py -v
```

### Test Coverage

The test suite covers:
- Feedback recording with various data types
- Feedback retrieval and sorting
- Feedback export functionality
- Privacy verification (no raw audio storage)
- Feedback count and summary statistics
- Error handling and edge cases

## API Reference

### `__init__(storage_path: str = "./feedback_data")`

Initialize the FeedbackSystem.

**Parameters:**
- `storage_path`: Directory path for storing feedback data

### `record_feedback(features, predicted_type, actual_type, confidence, timestamp=None) -> bool`

Store a feedback entry.

**Parameters:**
- `features`: Dictionary of extracted audio features
- `predicted_type`: Model's original prediction
- `actual_type`: Caregiver's correction
- `confidence`: Original confidence score (0-100)
- `timestamp`: Feedback submission time (defaults to current time)

**Returns:** True if successful, False otherwise

### `get_feedback_data() -> List[Dict[str, Any]]`

Retrieve all feedback entries.

**Returns:** List of feedback entry dictionaries, sorted by timestamp

### `export_feedback(output_path: str) -> bool`

Export all feedback data to a single file.

**Parameters:**
- `output_path`: File path for the exported data

**Returns:** True if successful, False otherwise

### `get_feedback_count() -> int`

Get the total number of feedback entries.

**Returns:** Number of feedback entries

### `get_feedback_summary() -> Dict[str, Any]`

Get summary statistics about stored feedback.

**Returns:** Dictionary containing:
- `total_entries`: Total number of entries
- `by_predicted_type`: Count by predicted type
- `by_actual_type`: Count by actual type
- `correction_rate`: Percentage of corrected predictions

### `clear_feedback() -> bool`

Clear all stored feedback data.

**Warning:** This permanently deletes all feedback entries.

**Returns:** True if successful, False otherwise

## Future Enhancements

Potential improvements for future versions:

1. **Database Backend**: Support for SQLite or other databases for better querying
2. **Feedback Filtering**: Filter feedback by date range, cry type, or confidence
3. **Feedback Validation**: Validate feedback entries before storage
4. **Compression**: Compress old feedback files to save space
5. **Cloud Sync**: Optional cloud backup for feedback data
6. **Feedback Analytics**: More detailed analytics and visualizations
7. **Batch Operations**: Bulk import/export of feedback data

## Related Modules

- `feature_extractor.py`: Extracts audio features for feedback storage
- `cry_classifier.py`: Generates predictions that can be corrected via feedback
- `alert_manager.py`: Displays predictions to caregivers for feedback collection

## License

This module is part of the Neonatal Cry Detection System.
