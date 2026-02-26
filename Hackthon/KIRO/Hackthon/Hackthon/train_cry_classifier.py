#!/usr/bin/env python3
"""
Cry Classifier Training Script

This script trains the cry type classifier model using extracted features.
Supports both Random Forest and neural network architectures.

Requirements:
- 4.1: Valid cry classification categories (5 types)
- 10.1: Model accuracy ≥ 75%
- 10.2: Pain/distress recall ≥ 85%

Usage:
    # Train Random Forest (default)
    python train_cry_classifier.py --features data/features --output models/cry_classifier_rf.pkl
    
    # Train neural network
    python train_cry_classifier.py --features data/features --output models/cry_classifier_nn.pkl --model-type nn
    
    # With hyperparameter tuning
    python train_cry_classifier.py --features data/features --output models/cry_classifier_rf.pkl --tune
"""

import argparse
import json
import pickle
import time
from pathlib import Path
from typing import Dict, Tuple, Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, 
    classification_report, 
    confusion_matrix,
    recall_score,
    precision_score,
    f1_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Categories
CATEGORIES = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']

# Performance requirements
MIN_ACCURACY = 0.75  # 75% minimum accuracy
MIN_PAIN_RECALL = 0.85  # 85% minimum recall for pain/distress


class CryClassifierTrainer:
    """Trains and evaluates cry classifier models"""
    
    def __init__(self, features_dir: str, model_type: str = 'random_forest'):
        """
        Initialize trainer
        
        Args:
            features_dir: Directory containing extracted features
            model_type: Type of model ('random_forest' or 'neural_network')
        """
        self.features_dir = Path(features_dir)
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Training data
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        
        # Results
        self.training_history = {}
        self.evaluation_results = {}
        
    def load_data(self):
        """Load training, validation, and test data"""
        print("=" * 60)
        print("Loading Training Data")
        print("=" * 60)
        
        # Load train set
        train_path = self.features_dir / 'train_features.npz'
        if not train_path.exists():
            raise FileNotFoundError(f"Training features not found: {train_path}")
        
        train_data = np.load(train_path)
        self.X_train = train_data['features']
        y_train_labels = train_data['labels']
        
        print(f"Train set: {self.X_train.shape[0]} samples, {self.X_train.shape[1]} features")
        
        # Load validation set
        val_path = self.features_dir / 'validation_features.npz'
        if val_path.exists():
            val_data = np.load(val_path)
            self.X_val = val_data['features']
            y_val_labels = val_data['labels']
            print(f"Validation set: {self.X_val.shape[0]} samples")
        else:
            print("Warning: Validation set not found, will use cross-validation")
            self.X_val = None
            y_val_labels = None
        
        # Load test set
        test_path = self.features_dir / 'test_features.npz'
        if test_path.exists():
            test_data = np.load(test_path)
            self.X_test = test_data['features']
            y_test_labels = test_data['labels']
            print(f"Test set: {self.X_test.shape[0]} samples")
        else:
            print("Warning: Test set not found")
            self.X_test = None
            y_test_labels = None
        
        # Encode labels
        self.label_encoder.fit(CATEGORIES)
        self.y_train = self.label_encoder.transform(y_train_labels)
        
        if y_val_labels is not None:
            self.y_val = self.label_encoder.transform(y_val_labels)
        else:
            self.y_val = None
            
        if y_test_labels is not None:
            self.y_test = self.label_encoder.transform(y_test_labels)
        else:
            self.y_test = None
        
        # Print label distribution
        print("\nLabel distribution (train):")
        unique, counts = np.unique(y_train_labels, return_counts=True)
        for label, count in zip(unique, counts):
            percentage = 100 * count / len(y_train_labels)
            print(f"  {label:20s}: {count:4d} ({percentage:5.1f}%)")
        
        print()
        
    def preprocess_data(self):
        """Normalize features using StandardScaler"""
        print("Preprocessing features...")
        
        # Fit scaler on training data
        self.scaler.fit(self.X_train)
        
        # Transform all sets
        self.X_train = self.scaler.transform(self.X_train)
        
        if self.X_val is not None:
            self.X_val = self.scaler.transform(self.X_val)
        
        if self.X_test is not None:
            self.X_test = self.scaler.transform(self.X_test)
        
        print("✓ Features normalized")
        print()
        
    def train_random_forest(self, tune_hyperparameters: bool = False):
        """
        Train Random Forest classifier
        
        Args:
            tune_hyperparameters: Whether to perform hyperparameter tuning
        """
        print("=" * 60)
        print("Training Random Forest Classifier")
        print("=" * 60)
        
        if tune_hyperparameters:
            print("Performing hyperparameter tuning...")
            self._tune_random_forest()
        else:
            print("Using default hyperparameters...")
            
            # Default hyperparameters optimized for cry classification
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                class_weight='balanced',  # Handle class imbalance
                random_state=42,
                n_jobs=-1,
                verbose=1
            )
        
        # Train model
        print("\nTraining model...")
        start_time = time.time()
        
        self.model.fit(self.X_train, self.y_train)
        
        training_time = time.time() - start_time
        print(f"✓ Training completed in {training_time:.2f} seconds")
        
        # Store training info
        self.training_history = {
            'model_type': 'random_forest',
            'training_time': training_time,
            'n_samples': len(self.X_train),
            'n_features': self.X_train.shape[1],
            'hyperparameters': self.model.get_params()
        }
        
        # Feature importance
        self._print_feature_importance()
        
        print()
        
    def _tune_random_forest(self):
        """Perform hyperparameter tuning for Random Forest"""
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2'],
            'class_weight': ['balanced', None]
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        grid_search = GridSearchCV(
            rf,
            param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            verbose=2
        )
        
        grid_search.fit(self.X_train, self.y_train)
        
        print(f"\nBest parameters: {grid_search.best_params_}")
        print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
        
        self.model = grid_search.best_estimator_
        
    def train_neural_network(self, tune_hyperparameters: bool = False):
        """
        Train neural network classifier
        
        Note: This is a placeholder for neural network training.
        In production, this would use TensorFlow/Keras or PyTorch.
        
        Args:
            tune_hyperparameters: Whether to perform hyperparameter tuning
        """
        print("=" * 60)
        print("Neural Network Training")
        print("=" * 60)
        print("\nNote: Neural network training requires TensorFlow/PyTorch.")
        print("For this implementation, we'll use Random Forest instead.")
        print("To add neural network support, install TensorFlow and implement")
        print("the neural network architecture in this method.")
        print()
        
        # Fall back to Random Forest
        self.model_type = 'random_forest'
        self.train_random_forest(tune_hyperparameters)
        
    def train(self, tune_hyperparameters: bool = False):
        """
        Train the model based on model_type
        
        Args:
            tune_hyperparameters: Whether to perform hyperparameter tuning
        """
        if self.model_type == 'random_forest':
            self.train_random_forest(tune_hyperparameters)
        elif self.model_type == 'neural_network':
            self.train_neural_network(tune_hyperparameters)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def evaluate(self):
        """Evaluate model on validation and test sets"""
        print("=" * 60)
        print("Model Evaluation")
        print("=" * 60)
        
        # Evaluate on validation set
        if self.X_val is not None:
            print("\nValidation Set Performance:")
            print("-" * 60)
            val_results = self._evaluate_on_set(self.X_val, self.y_val, "Validation")
            self.evaluation_results['validation'] = val_results
        
        # Evaluate on test set
        if self.X_test is not None:
            print("\nTest Set Performance:")
            print("-" * 60)
            test_results = self._evaluate_on_set(self.X_test, self.y_test, "Test")
            self.evaluation_results['test'] = test_results
        
        # Check if requirements are met
        self._check_requirements()
        
    def _evaluate_on_set(self, X: np.ndarray, y: np.ndarray, set_name: str) -> Dict[str, Any]:
        """
        Evaluate model on a dataset
        
        Args:
            X: Feature matrix
            y: True labels
            set_name: Name of the dataset
            
        Returns:
            Dictionary of evaluation metrics
        """
        # Make predictions
        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y, y_pred)
        
        # Get label names
        label_names = self.label_encoder.classes_
        
        # Per-class metrics
        precision = precision_score(y, y_pred, average=None, zero_division=0)
        recall = recall_score(y, y_pred, average=None, zero_division=0)
        f1 = f1_score(y, y_pred, average=None, zero_division=0)
        
        # Pain/distress recall (critical metric)
        pain_idx = list(label_names).index('pain_distress')
        pain_recall = recall[pain_idx]
        
        # Print results
        print(f"Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"Pain/Distress Recall: {pain_recall:.4f} ({pain_recall*100:.2f}%)")
        print()
        
        # Classification report
        print("Classification Report:")
        print(classification_report(
            y, y_pred,
            target_names=label_names,
            digits=4,
            zero_division=0
        ))
        
        # Confusion matrix
        print("Confusion Matrix:")
        cm = confusion_matrix(y, y_pred)
        self._print_confusion_matrix(cm, label_names)
        print()
        
        # Store results
        results = {
            'accuracy': float(accuracy),
            'pain_recall': float(pain_recall),
            'precision': {label: float(p) for label, p in zip(label_names, precision)},
            'recall': {label: float(r) for label, r in zip(label_names, recall)},
            'f1_score': {label: float(f) for label, f in zip(label_names, f1)},
            'confusion_matrix': cm.tolist()
        }
        
        return results
    
    def _print_confusion_matrix(self, cm: np.ndarray, labels: np.ndarray):
        """Print confusion matrix in a readable format"""
        # Print header
        print("         ", end="")
        for label in labels:
            print(f"{label[:8]:>8s}", end=" ")
        print()
        
        # Print rows
        for i, label in enumerate(labels):
            print(f"{label[:8]:8s}", end=" ")
            for j in range(len(labels)):
                print(f"{cm[i, j]:8d}", end=" ")
            print()
    
    def _print_feature_importance(self):
        """Print feature importance for Random Forest"""
        if not hasattr(self.model, 'feature_importances_'):
            return
        
        importances = self.model.feature_importances_
        
        # Feature names
        feature_names = [
            'pitch', 'pitch_std', 'intensity', 'intensity_std',
            'spectral_centroid', 'spectral_rolloff', 'zero_crossing_rate', 'duration'
        ] + [f'mfcc_{i}' for i in range(13)]
        
        # Sort by importance
        indices = np.argsort(importances)[::-1]
        
        print("\nTop 10 Most Important Features:")
        for i in range(min(10, len(indices))):
            idx = indices[i]
            print(f"  {i+1}. {feature_names[idx]:20s}: {importances[idx]:.4f}")
    
    def _check_requirements(self):
        """Check if model meets performance requirements"""
        print("\n" + "=" * 60)
        print("Requirements Validation")
        print("=" * 60)
        
        # Use test set if available, otherwise validation set
        if 'test' in self.evaluation_results:
            results = self.evaluation_results['test']
            set_name = "Test"
        elif 'validation' in self.evaluation_results:
            results = self.evaluation_results['validation']
            set_name = "Validation"
        else:
            print("No evaluation results available")
            return
        
        accuracy = results['accuracy']
        pain_recall = results['pain_recall']
        
        print(f"\nPerformance on {set_name} Set:")
        print(f"  Accuracy: {accuracy:.4f} (requirement: ≥ {MIN_ACCURACY:.2f})")
        print(f"  Pain/Distress Recall: {pain_recall:.4f} (requirement: ≥ {MIN_PAIN_RECALL:.2f})")
        print()
        
        # Check requirements
        accuracy_met = accuracy >= MIN_ACCURACY
        pain_recall_met = pain_recall >= MIN_PAIN_RECALL
        
        if accuracy_met:
            print("✓ Accuracy requirement MET (Requirement 10.1)")
        else:
            print("✗ Accuracy requirement NOT MET (Requirement 10.1)")
            print(f"  Need to improve by {(MIN_ACCURACY - accuracy)*100:.2f}%")
        
        if pain_recall_met:
            print("✓ Pain/Distress recall requirement MET (Requirement 10.2)")
        else:
            print("✗ Pain/Distress recall requirement NOT MET (Requirement 10.2)")
            print(f"  Need to improve by {(MIN_PAIN_RECALL - pain_recall)*100:.2f}%")
        
        print()
        
        if accuracy_met and pain_recall_met:
            print("🎉 All performance requirements satisfied!")
        else:
            print("⚠️  Model does not meet all requirements.")
            print("   Consider:")
            print("   - Collecting more training data")
            print("   - Performing hyperparameter tuning (--tune flag)")
            print("   - Trying different model architectures")
            print("   - Applying data augmentation")
        
        print("=" * 60)
        print()
    
    def save_model(self, output_path: str):
        """
        Save trained model to disk
        
        Args:
            output_path: Path to save the model
        """
        print(f"Saving model to {output_path}...")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Package model with scaler and label encoder
        model_package = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'model_type': self.model_type,
            'training_history': self.training_history,
            'evaluation_results': self.evaluation_results,
            'feature_names': [
                'pitch', 'pitch_std', 'intensity', 'intensity_std',
                'spectral_centroid', 'spectral_rolloff', 'zero_crossing_rate', 'duration'
            ] + [f'mfcc_{i}' for i in range(13)]
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(model_package, f)
        
        print(f"✓ Model saved successfully")
        
        # Save metadata as JSON
        metadata_path = output_path.with_suffix('.json')
        metadata = {
            'model_type': self.model_type,
            'training_history': self.training_history,
            'evaluation_results': self.evaluation_results
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved to {metadata_path}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Train cry classifier model')
    parser.add_argument('--features', type=str, required=True,
                       help='Directory containing extracted features')
    parser.add_argument('--output', type=str, required=True,
                       help='Output path for trained model')
    parser.add_argument('--model-type', type=str, default='random_forest',
                       choices=['random_forest', 'neural_network'],
                       help='Type of model to train (default: random_forest)')
    parser.add_argument('--tune', action='store_true',
                       help='Perform hyperparameter tuning (slower but better results)')
    
    args = parser.parse_args()
    
    # Validate features directory
    if not Path(args.features).exists():
        print(f"Error: Features directory '{args.features}' does not exist")
        print("\nPlease run feature extraction first:")
        print("  python extract_training_features.py --input data/processed --output data/features")
        return 1
    
    # Create trainer
    trainer = CryClassifierTrainer(args.features, args.model_type)
    
    try:
        # Load data
        trainer.load_data()
        
        # Preprocess
        trainer.preprocess_data()
        
        # Train
        trainer.train(tune_hyperparameters=args.tune)
        
        # Evaluate
        trainer.evaluate()
        
        # Save model
        trainer.save_model(args.output)
        
        print("=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"\nTrained model saved to: {args.output}")
        print("\nTo use the model in the cry classifier:")
        print(f"  1. Copy {args.output} to Hackthon/Hackthon/models/")
        print("  2. Update cry_classifier.py to load this model")
        print("  3. Test with: python verify_cry_classifier.py")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
