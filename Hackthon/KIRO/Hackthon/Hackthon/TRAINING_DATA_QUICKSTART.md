# Training Data Quick Start Guide

## For Testing the Pipeline (Synthetic Data)

If you want to test the training pipeline without real data:

```bash
# 1. Generate synthetic test data (small dataset for quick testing)
python generate_synthetic_data.py --output data/synthetic_test --samples 10

# 2. Verify the generated data
python verify_training_data.py --data data/synthetic_test

# 3. Extract features
python extract_training_features.py --input data/synthetic_test --output data/features_test --verify
```

## For Production (Real Data)

### Option 1: Using Baby Chillanto Dataset

```bash
# 1. Download from Kaggle (requires Kaggle account)
pip install kaggle
kaggle datasets download -d warcoder/baby-cry-detection
unzip baby-cry-detection.zip -d data/raw/baby_chillanto

# 2. Prepare the data
python prepare_training_data.py --input data/raw/baby_chillanto --output data/processed

# 3. Verify data quality
python verify_training_data.py --data data/processed

# 4. Extract features for training
python extract_training_features.py --input data/processed --output data/features --verify
```

### Option 2: Using Donate-a-Cry Corpus

```bash
# 1. Clone the repository
git clone https://github.com/gveres/donateacry-corpus.git data/raw/donate_a_cry

# 2. Prepare the data
python prepare_training_data.py --input data/raw/donate_a_cry --output data/processed

# 3. Verify data quality
python verify_training_data.py --data data/processed

# 4. Extract features for training
python extract_training_features.py --input data/processed --output data/features --verify
```

### Option 3: Using Custom Data

If you have your own labeled cry recordings:

```bash
# 1. Organize your data in this structure:
# data/raw/my_dataset/
#   ├── hunger/
#   │   ├── cry001.wav
#   │   └── cry002.wav
#   ├── pain/
#   │   └── cry003.wav
#   └── ... (other categories)

# 2. Prepare the data
python prepare_training_data.py --input data/raw/my_dataset --output data/processed

# 3. Verify data quality
python verify_training_data.py --data data/processed

# 4. Extract features for training
python extract_training_features.py --input data/processed --output data/features --verify
```

## Expected Output

After running the pipeline, you should have:

```
data/
├── processed/
│   ├── train/          # 70% of data
│   ├── validation/     # 15% of data
│   ├── test/           # 15% of data
│   └── metadata/       # CSV files with labels
└── features/
    ├── train_features.npz       # Training features
    ├── validation_features.npz  # Validation features
    ├── test_features.npz        # Test features
    └── *_metadata.json          # Metadata files
```

## Troubleshooting

### "Insufficient samples" error
- You need at least 20 samples per category in the training set
- Use `--samples` parameter with synthetic data generator to create more
- Combine multiple datasets if using real data

### "Sample rate mismatch" warning
- The scripts automatically resample to 16 kHz
- This warning is informational only

### "Label distribution imbalanced" warning
- Some categories have significantly more/fewer samples than others
- Consider data augmentation for minority classes
- Or collect more data for underrepresented categories

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Required: numpy, librosa, soundfile, scikit-learn, tqdm

## Next Steps

Once you have extracted features, proceed to Task 12.2:
```bash
python train_cry_classifier.py --features data/features --output models/cry_classifier.pkl
```

## Quick Reference

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `generate_synthetic_data.py` | Create test data | None | Synthetic audio files |
| `prepare_training_data.py` | Preprocess audio | Raw audio | Organized, normalized audio |
| `verify_training_data.py` | Check quality | Processed audio | Quality report |
| `extract_training_features.py` | Extract features | Processed audio | Feature arrays (.npz) |

## Minimum Requirements

For successful model training, you need:
- ✅ At least 100 total samples (20 per category minimum)
- ✅ All audio at 16 kHz sample rate
- ✅ Duration between 0.5-5 seconds per sample
- ✅ Balanced distribution across categories (within 50-200% of mean)
- ✅ No corrupted or invalid audio files

Check these with: `python verify_training_data.py --data data/processed`
