import os
import glob
import numpy as np
import librosa
import pandas as pd

# Define paths
RAW_DATA_PATH = "data/raw"
PROCESSED_DATA_PATH = "data/processed"
DATASET_SOURCE = "data/raw"

def extract_features(file_name):
    try:
        audio, sample_rate = librosa.load(file_name, sr=16000, mono=True)
        if len(audio) == 0: return None
        
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        mfccs_scaled = np.mean(mfccs.T, axis=0)
        
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
        centroid_scaled = np.mean(spectral_centroid)
        
        zcr = librosa.feature.zero_crossing_rate(y=audio)[0]
        zcr_scaled = np.mean(zcr)
        
        rms = librosa.feature.rms(y=audio)[0]
        rms_scaled = np.mean(rms)
        
        features = np.hstack([mfccs_scaled, centroid_scaled, zcr_scaled, rms_scaled])
        return features
        
    except Exception as e:
        print(f"Error parsing {file_name}: {e}")
        return None

def process_dataset():
    features_list = []
    
    # Label mapping:
    # 0 = Non-Cry (Ambient Noise/Silence)
    # 1 = Hunger (from 'hungry' folder)
    # 2 = Discomfort / Stress (from 'belly_pain' and 'discomfort' folders)
    
    # 1. Process Hunger samples (Label: 1)
    hunger_files = glob.glob(os.path.join(DATASET_SOURCE, "hungry", "*.wav"))[:50]
    print(f"Extracting {len(hunger_files)} Hunger samples...")
    for file in hunger_files:
        feats = extract_features(file)
        if feats is not None:
            features_list.append(np.append(feats, 1))
            
    # 2. Process Discomfort/Stress samples (Label: 2)
    stress_files = glob.glob(os.path.join(DATASET_SOURCE, "discomfort", "*.wav"))[:50]
    print(f"Extracting {len(stress_files)} Discomfort/Stress samples...")
    for file in stress_files:
        feats = extract_features(file)
        if feats is not None:
            features_list.append(np.append(feats, 2))
            
    # 3. Process Non-Cry samples (Label: 0)
    non_cry_files = glob.glob(os.path.join(RAW_DATA_PATH, "non_cry", "*.wav"))[:50]
    print(f"Extracting {len(non_cry_files)} Non-Cry samples...")
    for file in non_cry_files:
        feats = extract_features(file)
        if feats is not None:
            features_list.append(np.append(feats, 0))
            
    # Save as CSV for simple training inspection
    columns = [f"mfcc_{i}" for i in range(1, 14)] + ["centroid", "zcr", "rms", "label"]
    df = pd.DataFrame(features_list, columns=columns)
    
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    df.to_csv(os.path.join(PROCESSED_DATA_PATH, "extracted_features.csv"), index=False)
    print(f"Extraction complete! Saved {len(df)} rows to {PROCESSED_DATA_PATH}/extracted_features.csv")

if __name__ == "__main__":
    process_dataset()
