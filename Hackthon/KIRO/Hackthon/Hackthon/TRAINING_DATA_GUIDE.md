# Training Data Preparation Guide

## Overview

This guide explains how to prepare training data for the neonatal cry classification model. The model classifies infant cries into 5 categories:
- **hunger**: Baby is hungry
- **sleep_discomfort**: Baby is uncomfortable or tired
- **pain_distress**: Baby is in pain or distress (requires immediate attention)
- **diaper_change**: Baby needs a diaper change
- **normal_unknown**: Cry reason is unclear or normal fussiness

## Dataset Requirements

### Minimum Dataset Size
- **Total samples**: 500+ labeled cry recordings
- **Per category**: 100+ samples each
- **Sample rate**: 16 kHz (will be resampled if different)
- **Duration**: 1-5 seconds per sample
- **Format**: WAV, MP3, or FLAC

### Data Split
- **Training**: 70% (350+ samples)
- **Validation**: 15% (75+ samples)
- **Test**: 15% (75+ samples)

## Recommended Public Datasets

### 1. Baby Chillanto Database
- **Source**: Instituto Nacional de Astrofísica, Óptica y Electrónica (INAOE), Mexico
- **URL**: https://www.kaggle.com/datasets/warcoder/baby-cry-detection
- **Size**: ~450 cry samples
- **Categories**: Includes hunger, pain, discomfort labels
- **License**: Research use

**Download Instructions**:
```bash
# Using Kaggle API (requires Kaggle account and API token)
pip install kaggle
kaggle datasets download -d warcoder/baby-cry-detection
unzip baby-cry-detection.zip -d data/raw/baby_chillanto
```

### 2. Donate-a-Cry Corpus
- **Source**: UCLA and National Taiwan University
- **URL**: https://github.com/gveres/donateacry-corpus
- **Size**: ~450 cry samples from 26 babies
- **Categories**: Belly pain, burping, discomfort, hungry, tired
- **License**: Creative Commons

**Download Instructions**:
```bash
git clone https://github.com/gveres/donateacry-corpus.git data/raw/donate_a_cry
```

### 3. ESC-50 Environmental Sound Classification
- **Source**: Karol J. Piczak
- **URL**: https://github.com/karolpiczak/ESC-50
- **Size**: 2000 environmental sounds (includes crying baby category)
- **Use**: Can be used for negative samples and noise augmentation
- **License**: Creative Commons

## Data Directory Structure

Organize your data as follows:

```
Hackthon/Hackthon/data/
├── raw/                          # Original downloaded datasets
│   ├── baby_chillanto/
│   ├── donate_a_cry/
│   └── esc50/
├── processed/                    # Preprocessed and labeled data
│   ├── train/
│   │   ├── hunger/
│   │   ├── sleep_discomfort/
│   │   ├── pain_distress/
│   │   ├── diaper_change/
│   │   └── normal_unknown/
│   ├── validation/
│   │   ├── hunger/
│   │   ├── sleep_discomfort/
│   │   ├── pain_distress/
│   │   ├── diaper_change/
│   │   └── normal_unknown/
│   └── test/
│       ├── hunger/
│       ├── sleep_discomfort/
│       ├── pain_distress/
│       ├── diaper_change/
│       └── normal_unknown/
├── features/                     # Extracted features (cached)
│   ├── train_features.npz
│   ├── validation_features.npz
│   └── test_features.npz
└── metadata/
    ├── train_labels.csv
    ├── validation_labels.csv
    └── test_labels.csv
```

## Data Preparation Steps

### Step 1: Download Datasets

Use the download instructions above to obtain public datasets. Store them in `data/raw/`.

### Step 2: Label Mapping

Map original dataset labels to our 5 categories:

**Baby Chillanto / Donate-a-Cry Mapping**:
- `hungry` → `hunger`
- `tired`, `sleepy`, `uncomfortable` → `sleep_discomfort`
- `pain`, `belly_pain`, `distress` → `pain_distress`
- `burping`, `dirty_diaper` → `diaper_change`
- `unknown`, `other` → `normal_unknown`

### Step 3: Preprocess Audio

Run the preprocessing script:

```bash
python prepare_training_data.py --input data/raw --output data/processed
```

This script will:
1. Resample all audio to 16 kHz
2. Normalize audio amplitude
3. Trim silence from beginning/end
4. Split long recordings into 1-5 second segments
5. Apply label mapping
6. Split into train/validation/test sets
7. Save organized files

### Step 4: Extract Features

Extract acoustic features for training:

```bash
python extract_training_features.py --input data/processed --output data/features
```

This will:
1. Load audio from each category
2. Extract features using FeatureExtractor
3. Save features as compressed numpy arrays
4. Create metadata CSV files with labels

### Step 5: Verify Data Quality

Run data quality checks:

```bash
python verify_training_data.py --data data/processed
```

This checks:
- Minimum samples per category
- Audio quality (no corruption)
- Label distribution balance
- Sample rate consistency
- Duration distribution

## Data Augmentation (Optional)

To increase dataset size and robustness, apply augmentation:

```bash
python augment_training_data.py --input data/processed/train --output data/processed/train_augmented
```

**Augmentation techniques**:
- Add background noise (white noise, pink noise, environmental sounds)
- Time stretching (±10% speed change)
- Pitch shifting (±2 semitones)
- Volume variation (±20%)

**Recommended**: 2-3x augmentation for minority classes to balance dataset.

## Labeling Custom Data

If you have unlabeled cry recordings:

### Manual Labeling
1. Use audio annotation tool (e.g., Audacity, Praat)
2. Listen to each cry sample
3. Consult with caregivers/pediatricians for ground truth
4. Label based on context (feeding time → hunger, diaper check → diaper_change)
5. Save labels in CSV format

### Semi-Automated Labeling
1. Use existing model to generate initial predictions
2. Review and correct predictions manually
3. Focus on high-confidence predictions first
4. Use feedback system to collect corrections

## Data Quality Guidelines

### Good Quality Samples
- Clear cry sound (not muffled)
- Minimal background noise
- Single baby crying (not multiple)
- Consistent recording quality
- Accurate labels verified by caregivers

### Samples to Exclude
- Heavy background noise (TV, music, conversations)
- Multiple babies crying simultaneously
- Muffled or distorted audio
- Ambiguous labels (uncertain cry reason)
- Very short clips (< 0.5 seconds)

## Privacy and Ethics

### Data Collection Ethics
- Obtain informed consent from parents/guardians
- Anonymize all recordings (no identifying information)
- Secure storage with encryption
- Clear data retention and deletion policies
- Comply with COPPA (Children's Online Privacy Protection Act)

### Data Usage
- Use only for research and model training
- Do not share raw audio publicly
- Aggregate statistics only in publications
- Follow institutional review board (IRB) guidelines

## Model Training Requirements

### Minimum Requirements for Training
- **Samples**: 500+ labeled recordings
- **Balance**: Each category should have 80-120% of average count
- **Quality**: 90%+ samples should pass quality checks
- **Diversity**: Multiple babies, recording conditions, ages

### Validation Requirements
- **Accuracy**: ≥ 75% on validation set
- **Pain/Distress Recall**: ≥ 85% (critical for safety)
- **Confusion Matrix**: Check for systematic misclassifications
- **Noise Robustness**: Test with added noise at various SNR levels

## Troubleshooting

### Issue: Insufficient Data
**Solution**: 
- Use data augmentation to increase samples
- Combine multiple public datasets
- Use transfer learning from pre-trained models
- Start with 3-class model (pain vs. discomfort vs. normal)

### Issue: Imbalanced Classes
**Solution**:
- Oversample minority classes
- Undersample majority classes
- Use class weights in training
- Apply SMOTE or similar techniques

### Issue: Poor Model Performance
**Solution**:
- Check label quality (inter-rater agreement)
- Verify feature extraction is working correctly
- Try different model architectures
- Increase dataset size
- Add more diverse samples

### Issue: Overfitting
**Solution**:
- Increase validation set size
- Apply regularization (dropout, L2)
- Use data augmentation
- Reduce model complexity
- Early stopping based on validation loss

## Next Steps

After preparing training data:
1. Run `train_cry_classifier.py` to train the model
2. Evaluate on test set using `evaluate_model.py`
3. Validate performance meets requirements (≥75% accuracy, ≥85% pain recall)
4. Deploy model and collect feedback for continuous improvement

## References

- Baby Chillanto Database: https://www.kaggle.com/datasets/warcoder/baby-cry-detection
- Donate-a-Cry Corpus: https://github.com/gveres/donateacry-corpus
- ESC-50: https://github.com/karolpiczak/ESC-50
- Infant Cry Analysis: Reyes-Galaviz et al. (2004)
- Cry Classification: Lavner et al. (2016)
