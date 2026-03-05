import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.metrics import accuracy_score, classification_report
import os

PROCESSED_DATA_PATH = "data/processed/extracted_features.csv"
MODEL_SAVE_PATH = "models"

def train_edge_model():
    print("Loading Extracted Features for 3-Class Prediction (0: Non-Cry, 1: Hunger, 2: Discomfort)...")
    if not os.path.exists(PROCESSED_DATA_PATH):
        print("Data not found! Run 01_extract_features.py first.")
        return
        
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # Check if we have enough data
    if len(df) < 10:
        print("Not enough dataset points. Add .wav files to your raw folders.")
        return
        
    X = df.drop("label", axis=1)
    y = df["label"]
    
    # Normalizing features is critical for small edge-device models
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"Dataset Shape: {X_scaled.shape}")
    print("Splitting strictly 80/20 train/test...")
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    print("Training Lightweight Random Forest Classifier...")
    # 50 trees, max depth of 10 to prevent overfitting on such a small dataset
    model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"\n✅ EDGE MODEL ACCURACY: {acc * 100:.2f}%\n")
    print(classification_report(y_test, predictions, target_names=["Non-Cry", "Hunger", "Discomfort/Stress"], zero_division=0))
    
    # Save the artifacts for the Raspberry Pi inference code
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_SAVE_PATH, "cry_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_SAVE_PATH, "feature_scaler.joblib"))
    print(f"Lightweight model compiled to {MODEL_SAVE_PATH}/cry_model.joblib.")
    print("Ready for deployment to the 1GB Raspberry Pi.")

if __name__ == "__main__":
    train_edge_model()
