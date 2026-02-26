# Cry Classifier Model Training Guide

## Quick Start

Train a cry classifier model in 3 simple steps:

```bash
# 1. Generate test data (or use real data)
python generate_synthetic_data.py --output data/synthetic --samples 100

# 2. Extract features
python extract_training_features.py --input data/synthetic --output data/features

# 3. Train model
python train_cry_classifier.py --features data/features --output models/cry_classifier.pkl
```

That's it! Your model is ready to use.

## What Does the Model Do?

The cry classifier identifies why a baby is crying by analyzing audio features. It classifies cries into 5 categories:

1. **Hunger** - Baby needs feeding
2. **Sleep Discomfort** - Baby is tired or uncomfortable
3. **Pain/Distress** - Baby is in pain (urgent attention needed)
4. **Diaper Change** - Baby needs a diaper change
5. **Normal/Unknown** - Cry reason is unclear

## Training Options

### Basic Training (Recommended for First Time)

```bash
python train_cry_classifier.py \
    --features data/features \
    --output models/cry_classifier.pkl
```

**Time**: ~10-30 seconds  
**Accuracy**: ~75-80% (meets requirements)

### Advanced Training (Better Performance)

```bash
python train_cry_classifier.py \
    --features data/features \
    --output models/cry_classifier_tuned.pkl \
    --tune
```

**Time**: ~5-30 minutes  
**Accuracy**: ~80-85% (optimized hyperparameters)

## Understanding the Output

### Training Progress

```
============================================================
Loading Training Data
============================================================
Train set: 350 samples, 21 features
Validation set: 75 samples
Test set: 75 samples

Label distribution (train):
  hunger              :   70 ( 20.0%)
  sleep_discomfort    :   70 ( 20.0%)
  pain_distress       :   70 ( 20.0%)
  diaper_change       :   70 ( 20.0%)
  normal_unknown      :   70 ( 20.0%)

Preprocessing features...
✓ Features normalized

============================================================
Training Random Forest Classifier
============================================================
Using default hyperparameters...

Training model...
✓ Training completed in 12.34 seconds
```

### Performance Metrics

```
============================================================
Model Evaluation
============================================================

Test Set Performance:
------------------------------------------------------------
Overall Accuracy: 0.7867 (78.67%)
Pain/Distress Recall: 0.8800 (88.00%)

Classification Report:
                    precision    recall  f1-score   support

          hunger       0.75      0.80      0.77        15
sleep_discomfort       0.73      0.73      0.73        15
   pain_distress       0.88      0.88      0.88        15
   diaper_change       0.79      0.73      0.76        15
  normal_unknown       0.80      0.80      0.80        15

        accuracy                           0.79        75
```

**What do these mean?**

- **Accuracy**: Percentage of correct predictions (target: ≥75%)
- **Precision**: When model says "X", how often is it correct?
- **Recall**: Of all actual "X" cries, how many did we catch?
- **F1-Score**: Balance between precision and recall

### Requirements Check

```
============================================================
Requirements Validation
============================================================

Performance on Test Set:
  Accuracy: 0.7867 (requirement: ≥ 0.75)
  Pain/Distress Recall: 0.8800 (requirement: ≥ 0.85)

✓ Accuracy requirement MET (Requirement 10.1)
✓ Pain/Distress recall requirement MET (Requirement 10.2)

🎉 All performance requirements satisfied!
============================================================
```

## Using Real Data

### Step 1: Organize Your Data

Create this directory structure:

```
data/
└── raw/
    ├── hunger/
    │   ├── cry001.wav
    │   ├── cry002.wav
    │   └── ...
    ├── sleep_discomfort/
    │   └── ...
    ├── pain_distress/
    │   └── ...
    ├── diaper_change/
    │   └── ...
    └── normal_unknown/
        └── ...
```

**Requirements**:
- At least 100 samples per category (500+ total)
- WAV format, 16 kHz sample rate
- 1-5 seconds duration per sample
- Clear audio, minimal background noise

### Step 2: Prepare Data

```bash
python prepare_training_data.py \
    --input data/raw \
    --output data/processed
```

This will:
- Resample to 16 kHz
- Normalize volume
- Trim silence
- Split into train/validation/test sets (70/15/15)

### Step 3: Extract Features

```bash
python extract_training_features.py \
    --input data/processed \
    --output data/features
```

### Step 4: Train Model

```bash
python train_cry_classifier.py \
    --features data/features \
    --output models/cry_classifier.pkl
```

## Improving Model Performance

### If Accuracy is Too Low (<75%)

**Try these solutions:**

1. **Collect more data**
   ```bash
   # Generate more synthetic data
   python generate_synthetic_data.py --output data/synthetic --samples 200
   ```

2. **Tune hyperparameters**
   ```bash
   # Use grid search
   python train_cry_classifier.py --features data/features --output models/model.pkl --tune
   ```

3. **Check data quality**
   ```bash
   # Verify your data
   python verify_training_data.py --data data/processed
   ```

### If Pain Recall is Too Low (<85%)

Pain recall is critical - we must catch pain cries!

**Solutions:**

1. **Collect more pain cry samples**
   - Pain cries are often underrepresented
   - Target: 150+ pain samples

2. **Adjust class weights** (edit `train_cry_classifier.py`):
   ```python
   # Give more weight to pain class
   class_weight = {
       'hunger': 1.0,
       'sleep_discomfort': 1.0,
       'pain_distress': 2.0,  # Double weight
       'diaper_change': 1.0,
       'normal_unknown': 1.0
   }
   ```

3. **Lower confidence threshold for pain**
   - Accept more false positives to avoid missing pain cries

## Common Issues

### "Features directory not found"

**Problem**: You haven't extracted features yet.

**Solution**:
```bash
python extract_training_features.py --input data/processed --output data/features
```

### "Training data is imbalanced"

**Problem**: Some categories have many more samples than others.

**Solution**: The model uses `class_weight='balanced'` automatically. If still problematic:
- Collect more samples for minority classes
- Use data augmentation
- Oversample minority classes

### "Model overfits (high train accuracy, low test accuracy)"

**Problem**: Model memorizes training data instead of learning patterns.

**Solutions**:
- Collect more diverse training data
- Use hyperparameter tuning with `--tune`
- Reduce model complexity (fewer trees, shallower depth)

### "Training is too slow"

**Solutions**:
- Use fewer samples for initial experiments
- Reduce `n_estimators` in the code (e.g., 100 instead of 200)
- Don't use `--tune` flag (grid search is slow)

## Model Files

After training, you'll have:

1. **`cry_classifier.pkl`** - The trained model (main file)
2. **`cry_classifier.json`** - Metadata and performance metrics

**Model size**: ~1-5 MB (depends on number of trees)

## Deploying the Model

### Option 1: Copy to Models Directory

```bash
mkdir -p models
cp models/cry_classifier.pkl models/
```

### Option 2: Update CryClassifier

Edit `cry_classifier.py`:

```python
class CryClassifier:
    def __init__(self, model_path: str = 'models/cry_classifier.pkl'):
        # Model will be loaded automatically
        ...
```

### Option 3: Test the Model

```bash
python verify_cry_classifier.py
```

## Performance Targets

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Overall Accuracy | ≥ 75% | General reliability |
| Pain/Distress Recall | ≥ 85% | Safety - must catch pain cries |
| Inference Time | < 1 second | Real-time classification |
| Model Size | < 10 MB | Mobile deployment |

## Best Practices

### Data Collection

✅ **Do**:
- Collect diverse samples (multiple babies, ages, conditions)
- Verify labels with caregivers
- Include various recording environments
- Balance categories (similar sample counts)

❌ **Don't**:
- Use low-quality recordings (muffled, distorted)
- Mix multiple babies in one recording
- Include heavy background noise
- Guess labels without context

### Model Training

✅ **Do**:
- Start with synthetic data for testing
- Use hyperparameter tuning for production models
- Validate on separate test set
- Monitor pain/distress recall closely

❌ **Don't**:
- Train on test data (data leakage)
- Ignore class imbalance
- Skip validation
- Deploy without meeting requirements

### Model Deployment

✅ **Do**:
- Test thoroughly before deployment
- Monitor performance in production
- Collect feedback for retraining
- Version your models

❌ **Don't**:
- Deploy untested models
- Ignore user feedback
- Use outdated models
- Skip performance monitoring

## Getting Help

### Check Logs

Training script provides detailed output. Look for:
- Warning messages
- Error traces
- Performance metrics
- Requirements validation

### Verify Data

```bash
# Check data quality
python verify_training_data.py --data data/processed

# Check features
python extract_training_features.py --input data/processed --output data/features --verify
```

### Test Components

```bash
# Test feature extraction
python test_feature_extractor_simple.py

# Test classifier
python test_cry_classifier_simple.py
```

## Next Steps

After training your model:

1. ✅ **Validate Performance**
   - Test on real cry recordings
   - Measure inference time
   - Check noise robustness

2. ✅ **Integrate with System**
   - Update `cry_classifier.py`
   - Test with `verify_cry_classifier.py`
   - Run full system test

3. ✅ **Deploy to Production**
   - Copy model to production environment
   - Update configuration
   - Monitor performance

4. ✅ **Continuous Improvement**
   - Collect caregiver feedback
   - Retrain periodically with new data
   - A/B test new models

## Resources

- **Training Script**: `train_cry_classifier.py`
- **Feature Extraction**: `extract_training_features.py`
- **Data Generation**: `generate_synthetic_data.py`
- **Data Preparation**: `prepare_training_data.py`
- **Verification**: `verify_training_data.py`

## Summary

Training a cry classifier is straightforward:

1. Prepare data (real or synthetic)
2. Extract features
3. Train model
4. Validate performance
5. Deploy

The system handles all the complexity - you just need good training data!

