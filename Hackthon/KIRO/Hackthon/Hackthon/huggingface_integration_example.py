"""
Example: Integrating Hugging Face Baby Cry Classification Model

This script shows how to integrate the foduucom/baby-cry-classification model
from Hugging Face with our 3-category system.

Model: https://huggingface.co/foduucom/baby-cry-classification
Categories (original): belly_pain, burping, discomfort, hunger, tiredness
Categories (mapped to 3): hunger, sleep, discomfort
"""

import numpy as np
import librosa
import joblib
from typing import Dict, Any, Tuple

class HuggingFaceCryClassifier:
    """
    Cry classifier using Hugging Face pre-trained model.
    Maps 5 categories to our 3-category system.
    """
    
    # Map Hugging Face categories to our 3 categories
    CATEGORY_MAPPING = {
        'hunger': 'hunger',
        'tiredness': 'sleep',
        'belly_pain': 'discomfort',
        'burping': 'discomfort',
        'discomfort': 'discomfort'
    }
    
    def __init__(self, model_path: str = 'model.joblib', label_path: str = 'label.joblib'):
        """
        Initialize with Hugging Face model files.
        
        Args:
            model_path: Path to model.joblib file
            label_path: Path to label.joblib file
            
        Note: Download these files from:
        https://huggingface.co/foduucom/baby-cry-classification
        """
        try:
            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(label_path)
            self.model_loaded = True
            print("✓ Hugging Face model loaded successfully")
        except FileNotFoundError:
            print("⚠ Model files not found. Using fallback rule-based classifier.")
            print("  Download from: https://huggingface.co/foduucom/baby-cry-classification")
            self.model_loaded = False
    
    def extract_features(self, audio: np.ndarray, sr: int = 16000) -> np.ndarray:
        """
        Extract features using Hugging Face model's feature extraction method.
        
        Features extracted:
        - MFCC (40 coefficients)
        - Mel-spectrogram (128 bands)
        - Chroma (12 bins)
        - Spectral contrast (7 bands)
        - Tonnetz (6 features)
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (default 16000 Hz)
            
        Returns:
            Feature vector as numpy array
        """
        # Parameters from Hugging Face model
        n_fft = 2048
        hop_length = 512
        win_length = 2048
        window = 'hann'
        n_mels = 128
        n_bands = 6
        fmin = 200.0
        
        try:
            # MFCC features (40 coefficients)
            mfcc = np.mean(
                librosa.feature.mfcc(
                    y=audio, sr=sr, n_mfcc=40,
                    n_fft=n_fft, hop_length=hop_length,
                    win_length=win_length, window=window
                ).T, axis=0
            )
            
            # Mel-spectrogram features
            mel = np.mean(
                librosa.feature.melspectrogram(
                    y=audio, sr=sr,
                    n_fft=n_fft, hop_length=hop_length,
                    win_length=win_length, window=window,
                    n_mels=n_mels
                ).T, axis=0
            )
            
            # STFT for chroma and contrast
            stft = np.abs(librosa.stft(audio))
            
            # Chroma features (12 bins)
            chroma = np.mean(
                librosa.feature.chroma_stft(
                    S=stft, y=audio, sr=sr
                ).T, axis=0
            )
            
            # Spectral contrast (7 bands)
            contrast = np.mean(
                librosa.feature.spectral_contrast(
                    S=stft, y=audio, sr=sr,
                    n_fft=n_fft, hop_length=hop_length,
                    win_length=win_length,
                    n_bands=n_bands, fmin=fmin
                ).T, axis=0
            )
            
            # Tonnetz features (6 features)
            tonnetz = np.mean(
                librosa.feature.tonnetz(y=audio, sr=sr).T, axis=0
            )
            
            # Concatenate all features
            features = np.concatenate((mfcc, chroma, mel, contrast, tonnetz))
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def predict(self, audio: np.ndarray) -> Tuple[str, float]:
        """
        Predict cry type using Hugging Face model.
        
        Args:
            audio: Audio signal as numpy array
            
        Returns:
            Tuple of (cry_type, confidence)
            - cry_type: One of 'hunger', 'sleep', 'discomfort'
            - confidence: Confidence score (0-100)
        """
        if not self.model_loaded:
            return 'discomfort', 0.0
        
        # Extract features
        features = self.extract_features(audio)
        
        if features is None:
            return 'discomfort', 0.0
        
        # Reshape for model input
        features = features.reshape(1, -1)
        
        # Make prediction
        prediction = self.model.predict(features)
        
        # Get confidence scores if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            confidence = float(np.max(probabilities) * 100)
        else:
            confidence = 75.0  # Default confidence
        
        # Convert prediction to label
        predicted_label = self.label_encoder.inverse_transform(prediction)[0]
        
        # Map to our 3 categories
        cry_type = self.CATEGORY_MAPPING.get(predicted_label, 'discomfort')
        
        return cry_type, confidence


def test_huggingface_integration():
    """Test the Hugging Face model integration."""
    
    print("=" * 60)
    print("Hugging Face Model Integration Test")
    print("=" * 60)
    print()
    
    # Initialize classifier
    classifier = HuggingFaceCryClassifier()
    
    if not classifier.model_loaded:
        print("\n⚠ Cannot test without model files.")
        print("Download model files from:")
        print("https://huggingface.co/foduucom/baby-cry-classification")
        print("\nFiles needed:")
        print("  - model.joblib")
        print("  - label.joblib")
        return
    
    # Test with synthetic audio
    print("Testing with synthetic audio...")
    print()
    
    # Test 1: Hunger pattern
    print("Test 1: Hunger Pattern")
    print("-" * 40)
    hunger_audio = np.sin(2 * np.pi * 350 * np.linspace(0, 1.5, 24000))
    hunger_audio = hunger_audio * 0.3
    
    cry_type, confidence = classifier.predict(hunger_audio)
    print(f"Predicted: {cry_type}")
    print(f"Confidence: {confidence:.1f}%")
    print()
    
    # Test 2: Sleep pattern
    print("Test 2: Sleep Pattern")
    print("-" * 40)
    t = np.linspace(0, 2.0, 32000)
    sleep_audio = np.sin(2 * np.pi * (300 + 50 * np.sin(2 * np.pi * 2 * t)) * t)
    sleep_audio = sleep_audio * 0.15
    
    cry_type, confidence = classifier.predict(sleep_audio)
    print(f"Predicted: {cry_type}")
    print(f"Confidence: {confidence:.1f}%")
    print()
    
    # Test 3: Discomfort pattern
    print("Test 3: Discomfort Pattern")
    print("-" * 40)
    t = np.linspace(0, 1.0, 16000)
    discomfort_audio = np.sin(2 * np.pi * (500 + 100 * np.sin(2 * np.pi * 5 * t)) * t)
    discomfort_audio = discomfort_audio * 0.6
    
    cry_type, confidence = classifier.predict(discomfort_audio)
    print(f"Predicted: {cry_type}")
    print(f"Confidence: {confidence:.1f}%")
    print()
    
    print("=" * 60)
    print("✓ Integration test completed")
    print("=" * 60)


def compare_classifiers():
    """
    Compare Hugging Face model with rule-based classifier.
    """
    from cry_classifier import CryClassifier
    from feature_extractor import FeatureExtractor
    
    print("=" * 60)
    print("Classifier Comparison: Hugging Face vs Rule-Based")
    print("=" * 60)
    print()
    
    # Initialize both classifiers
    hf_classifier = HuggingFaceCryClassifier()
    rule_classifier = CryClassifier()
    feature_extractor = FeatureExtractor()
    
    if not hf_classifier.model_loaded:
        print("⚠ Hugging Face model not available for comparison")
        return
    
    # Test audio samples
    test_cases = [
        ("Hunger", np.sin(2 * np.pi * 350 * np.linspace(0, 1.5, 24000)) * 0.3),
        ("Sleep", np.sin(2 * np.pi * 300 * np.linspace(0, 2.0, 32000)) * 0.15),
        ("Discomfort", np.sin(2 * np.pi * 500 * np.linspace(0, 1.0, 16000)) * 0.6)
    ]
    
    for name, audio in test_cases:
        print(f"Test Case: {name}")
        print("-" * 40)
        
        # Hugging Face prediction
        hf_type, hf_conf = hf_classifier.predict(audio)
        print(f"Hugging Face: {hf_type} ({hf_conf:.1f}%)")
        
        # Rule-based prediction
        features = feature_extractor.extract_all_features(audio)
        rule_result = rule_classifier.predict(audio, features)
        print(f"Rule-Based:   {rule_result['cry_type']} ({rule_result['confidence']:.1f}%)")
        
        # Agreement
        agreement = "✓ Agree" if hf_type == rule_result['cry_type'] else "✗ Disagree"
        print(f"Agreement: {agreement}")
        print()
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Hugging Face Baby Cry Classification Integration")
    print("=" * 60)
    print()
    print("This script demonstrates how to use the Hugging Face model")
    print("with our 3-category cry detection system.")
    print()
    print("Model: foduucom/baby-cry-classification")
    print("URL: https://huggingface.co/foduucom/baby-cry-classification")
    print()
    
    # Run tests
    test_huggingface_integration()
    print()
    
    # Compare classifiers if model is available
    # compare_classifiers()
