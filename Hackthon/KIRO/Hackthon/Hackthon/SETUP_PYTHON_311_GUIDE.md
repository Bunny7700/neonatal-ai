# Setup Guide: Python 3.11/3.12 for Accurate Cry Detection

This guide will help you set up Python 3.11 or 3.12 to enable real ML-based cry detection with actual audio processing.

## Why Python 3.11/3.12?

Python 3.14 doesn't support the required libraries:
- ❌ numpy (audio processing)
- ❌ librosa (audio feature extraction)
- ❌ scipy (signal processing)
- ❌ tensorflow (ML model inference)

Python 3.11/3.12 supports all of these! ✅

## Step 1: Install Python 3.11 or 3.12

### Option A: Using Python Installer (Recommended)

1. **Download Python 3.12**:
   - Go to: https://www.python.org/downloads/
   - Download Python 3.12.x (latest stable)
   - **Important**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
   ```cmd
   python --version
   ```
   Should show: `Python 3.12.x`

### Option B: Using Chocolatey (Windows Package Manager)

```cmd
choco install python --version=3.12.0
```

### Option C: Keep Both Versions

If you want to keep Python 3.14:
1. Install Python 3.12 to a different directory (e.g., `C:\Python312`)
2. Use `py -3.12` to run Python 3.12 specifically

## Step 2: Create Virtual Environment

```cmd
cd Hackthon\Hackthon

# Create virtual environment with Python 3.12
python -m venv venv312

# Activate it
venv312\Scripts\activate

# Verify you're using Python 3.12
python --version
```

## Step 3: Install Required Libraries

```cmd
# Upgrade pip first
python -m pip install --upgrade pip

# Install audio processing libraries
pip install numpy==1.24.3
pip install librosa==0.10.1
pip install scipy==1.11.4
pip install soundfile==0.12.1

# Install ML libraries (optional, for model training)
pip install tensorflow==2.15.0
pip install scikit-learn==1.3.2

# Install other dependencies
pip install matplotlib==3.8.2
```

## Step 4: Test the Installation

Run this test script:

```cmd
python verify_audio_setup.py
```

You should see:
```
✅ numpy: 1.24.3
✅ librosa: 0.10.1
✅ scipy: 1.11.4
✅ soundfile: 0.12.1
✅ All audio processing libraries installed successfully!
```

## Step 5: Run the Real Cry Detection System

Now you can use the full ML-based system:

```cmd
# Stop the current server (Ctrl+C if running)

# Run the enhanced server with real audio processing
python main_enhanced.py
```

Or use the integrated system:

```cmd
python cry_detection_integrated.py
```

## Step 6: Update Frontend to Use Real Analysis

The frontend is already set up! Just:
1. Make sure the server is running with Python 3.12
2. Refresh your browser (F5)
3. Click "Start Listening"

The system will now use:
- ✅ Real audio feature extraction (MFCC, spectral features)
- ✅ Frequency analysis (pitch, formants)
- ✅ Pattern matching against cry datasets
- ✅ ML-based classification

## What You Get with Python 3.11/3.12

### Real Audio Features:
- **MFCC** (Mel-frequency cepstral coefficients)
- **Spectral Centroid** (brightness of sound)
- **Zero Crossing Rate** (noisiness)
- **Chroma Features** (pitch class)
- **Spectral Rolloff** (frequency distribution)

### Accurate Cry Classification:
- Analyzes actual audio patterns, not just volume
- Matches against known cry characteristics
- Uses trained models (if available)
- Much higher accuracy than volume-based detection

## Troubleshooting

### Issue: "numpy not found"
**Solution**: Make sure you activated the virtual environment:
```cmd
venv312\Scripts\activate
```

### Issue: "librosa installation failed"
**Solution**: Install dependencies first:
```cmd
pip install numba==0.58.1
pip install llvmlite==0.41.1
pip install librosa
```

### Issue: "Module not found" when running server
**Solution**: Install in the correct environment:
```cmd
# Make sure you're in the virtual environment
where python
# Should show: ...\venv312\Scripts\python.exe

pip install -r requirements.txt
```

## Training Your Own Model (Optional)

Once you have Python 3.12 set up, you can train on real cry datasets:

```cmd
# 1. Prepare training data
python prepare_training_data.py

# 2. Extract features
python extract_training_features.py

# 3. Train the model
python train_cry_classifier.py
```

See `MODEL_TRAINING_GUIDE.md` for details.

## Quick Reference

### Activate Environment:
```cmd
cd Hackthon\Hackthon
venv312\Scripts\activate
```

### Run Server:
```cmd
python main_enhanced.py
```

### Deactivate Environment:
```cmd
deactivate
```

## Next Steps

1. ✅ Install Python 3.12
2. ✅ Create virtual environment
3. ✅ Install libraries
4. ✅ Run the server
5. ✅ Test with real audio
6. 🎯 Get accurate cry detection!

## Support

If you encounter issues:
1. Check Python version: `python --version`
2. Check installed packages: `pip list`
3. Verify virtual environment is activated
4. Check the error messages carefully

Good luck with your hackathon! 🚀
