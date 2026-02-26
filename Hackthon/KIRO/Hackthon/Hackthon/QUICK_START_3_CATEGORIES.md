# Quick Start: 3-Category Cry Detection

## What's New?

Your cry detection system now classifies baby cries into **3 simple categories**:

| Category | Icon | Color | Meaning | Priority |
|----------|------|-------|---------|----------|
| **Hunger** | 🍼 | Orange | Baby needs feeding | Medium |
| **Sleep** | 😴 | Blue | Baby is tired | Medium |
| **Discomfort** | ⚠️ | Red | Baby is in distress/pain | High |

## How It Works

The system analyzes audio features to determine cry type:

### Hunger Detection
- **Sound**: Rhythmic, steady crying
- **Pitch**: Moderate (300-450 Hz)
- **Pattern**: Sustained, persistent
- **Action**: Feed the baby

### Sleep Detection
- **Sound**: Fussy, variable crying
- **Pitch**: Lower, irregular
- **Pattern**: Longer duration with breaks
- **Action**: Help baby sleep

### Discomfort Detection
- **Sound**: Loud, urgent crying
- **Pitch**: High (>450 Hz)
- **Pattern**: Irregular, harsh
- **Action**: Check diaper, temperature, pain

## Using the System

### 1. Basic Usage

```python
from cry_classifier import CryClassifier
from feature_extractor import FeatureExtractor
from alert_manager import AlertManager

# Initialize
classifier = CryClassifier()
feature_extractor = FeatureExtractor()
alert_manager = AlertManager()

# Process audio
audio = # ... your audio data (numpy array)
features = feature_extractor.extract_all_features(audio)
result = classifier.predict(audio, features)

# Generate alert
alert = alert_manager.generate_alert(
    result['cry_type'],
    result['confidence']
)

print(f"Detected: {alert['message']}")
print(f"Confidence: {result['confidence']:.1f}%")
```

### 2. Understanding Results

```python
result = {
    'is_crying': True,           # Whether crying was detected
    'cry_type': 'hunger',        # One of: hunger, sleep, discomfort
    'confidence': 75.5,          # Confidence score (0-100)
    'detection_confidence': 85.0 # Cry detection confidence
}
```

### 3. Alert Structure

```python
alert = {
    'message': 'Baby may be hungry 🍼',
    'cry_type': 'hunger',
    'confidence': 75.5,
    'color': '#f59e0b',          # Orange for hunger
    'icon': '🍼',
    'severity': 'medium',
    'timestamp': 1234567890.0
}
```

## Testing

### Run the Test Script

```bash
cd Hackthon/Hackthon
.\venv312\Scripts\python.exe test_3_category_classifier.py
```

This will test all 3 categories and verify the system works correctly.

### Expected Output

```
============================================================
Testing 3-Category Cry Classifier
Categories: Hunger, Sleep, Discomfort
============================================================

Test 1: Hunger Pattern
----------------------------------------
Detected: hunger
Confidence: 80.8%
Alert: Baby may be hungry 🍼
Color: #f59e0b, Icon: 🍼, Severity: medium

Test 2: Sleep/Tiredness Pattern
----------------------------------------
Detected: sleep
Confidence: 76.0%
Alert: Baby is tired and needs sleep 😴
Color: #3b82f6, Icon: 😴, Severity: medium

Test 3: Discomfort/Distress Pattern
----------------------------------------
Detected: discomfort
Confidence: 85.2%
Alert: Baby is uncomfortable or in distress ⚠️
Color: #ef4444, Icon: ⚠️, Severity: high

✓ All tests completed successfully!
```

## API Integration

### Available External APIs

#### Hugging Face Model (Recommended)
- **Model**: foduucom/baby-cry-classification
- **Type**: Local inference (no API calls)
- **Accuracy**: ~38% baseline, 70-80% with retraining
- **Cost**: Free
- **Setup**:
  ```bash
  pip install joblib librosa
  # Download model files from Hugging Face
  ```

#### Google Cloud Vertex AI
- **Status**: No pre-trained baby cry model
- **Option**: Custom training with AutoML
- **Cost**: Pay per use
- **Not recommended** for this use case

### Using Hugging Face Model (Optional)

If you want to use the Hugging Face model instead of rule-based classification:

1. Download model files:
   - `model.joblib` - Trained classifier
   - `label.joblib` - Label encoder

2. Update `cry_classifier.py`:
   ```python
   def load_cry_type_model(self):
       import joblib
       self.cry_type_model = joblib.load('model.joblib')
       self.label_encoder = joblib.load('label.joblib')
   ```

3. Map 5 categories to 3:
   ```python
   category_mapping = {
       'hunger': 'hunger',
       'tiredness': 'sleep',
       'belly_pain': 'discomfort',
       'burping': 'discomfort',
       'discomfort': 'discomfort'
   }
   ```

## Customization

### Adjust Classification Thresholds

Edit `cry_classifier.py` to tune the classification rules:

```python
# Make hunger detection more sensitive
if 300 <= pitch <= 450:
    scores['hunger'] += 40  # Increase from 35

# Make discomfort detection stricter
if pitch > 500:  # Increase from 450
    scores['discomfort'] += 40
```

### Change Alert Messages

Edit `alert_manager.py`:

```python
CRY_MESSAGES = {
    "hunger": "Time to feed! 🍼",
    "sleep": "Sleepy baby 😴",
    "discomfort": "Check on baby! ⚠️"
}
```

### Modify Colors

```python
CRY_COLORS = {
    "hunger": "#ff9800",     # Different orange
    "sleep": "#2196f3",      # Different blue
    "discomfort": "#f44336"  # Different red
}
```

## Troubleshooting

### Low Confidence Scores
- **Cause**: Audio quality issues or ambiguous cry
- **Solution**: Improve microphone placement, reduce background noise

### Wrong Category Detected
- **Cause**: Classification rules need tuning
- **Solution**: Adjust thresholds in `cry_classifier.py` or collect training data

### No Cry Detected
- **Cause**: Audio too quiet or not a cry
- **Solution**: Check microphone volume, verify audio input

## Next Steps

1. **Test with real audio**: Record baby cries and test classification
2. **Collect feedback**: Use the feedback system to improve accuracy
3. **Train custom model**: Use `train_cry_classifier.py` with labeled data
4. **Deploy**: Integrate with your application or dashboard

## Support

For questions or issues:
- Check `3_CATEGORY_CLASSIFICATION_UPDATE.md` for detailed information
- Review test results in `test_3_category_classifier.py`
- Examine feature extraction in `feature_extractor.py`

---

**Ready to use!** The 3-category system is simpler, faster, and easier to understand than the previous 5-category version. 🎉
