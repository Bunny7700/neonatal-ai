#!/usr/bin/env python3
"""
Simple test script for model training

This script tests the complete training pipeline with synthetic data.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"\n✓ {description} - SUCCESS")
        return True
    else:
        print(f"\n✗ {description} - FAILED")
        return False


def main():
    print("=" * 60)
    print("Model Training Pipeline Test")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Generate synthetic training data")
    print("2. Extract features")
    print("3. Train a model")
    print("4. Verify the trained model")
    print()
    
    # Setup paths
    test_data_dir = Path("data/test_training")
    test_features_dir = Path("data/test_features")
    test_model_path = Path("models/test_cry_classifier.pkl")
    
    # Clean up previous test data
    if test_data_dir.exists():
        print(f"Cleaning up previous test data: {test_data_dir}")
        shutil.rmtree(test_data_dir)
    
    if test_features_dir.exists():
        print(f"Cleaning up previous test features: {test_features_dir}")
        shutil.rmtree(test_features_dir)
    
    if test_model_path.exists():
        print(f"Cleaning up previous test model: {test_model_path}")
        test_model_path.unlink()
        if test_model_path.with_suffix('.json').exists():
            test_model_path.with_suffix('.json').unlink()
    
    print()
    
    # Step 1: Generate synthetic data
    success = run_command(
        [
            sys.executable,
            "generate_synthetic_data.py",
            "--output", str(test_data_dir),
            "--samples", "20"  # Small dataset for quick testing
        ],
        "Step 1: Generate Synthetic Data"
    )
    
    if not success:
        print("\n❌ Test failed at data generation")
        return 1
    
    # Step 2: Extract features
    success = run_command(
        [
            sys.executable,
            "extract_training_features.py",
            "--input", str(test_data_dir),
            "--output", str(test_features_dir),
            "--verify"
        ],
        "Step 2: Extract Features"
    )
    
    if not success:
        print("\n❌ Test failed at feature extraction")
        return 1
    
    # Step 3: Train model
    success = run_command(
        [
            sys.executable,
            "train_cry_classifier.py",
            "--features", str(test_features_dir),
            "--output", str(test_model_path)
        ],
        "Step 3: Train Model"
    )
    
    if not success:
        print("\n❌ Test failed at model training")
        return 1
    
    # Step 4: Verify model file exists
    print(f"\n{'='*60}")
    print("Step 4: Verify Model Files")
    print(f"{'='*60}")
    
    if test_model_path.exists():
        size_mb = test_model_path.stat().st_size / (1024 * 1024)
        print(f"✓ Model file exists: {test_model_path}")
        print(f"  Size: {size_mb:.2f} MB")
    else:
        print(f"✗ Model file not found: {test_model_path}")
        return 1
    
    if test_model_path.with_suffix('.json').exists():
        print(f"✓ Metadata file exists: {test_model_path.with_suffix('.json')}")
    else:
        print(f"✗ Metadata file not found: {test_model_path.with_suffix('.json')}")
        return 1
    
    # Step 5: Test loading the model
    print(f"\n{'='*60}")
    print("Step 5: Test Loading Model")
    print(f"{'='*60}")
    
    try:
        import pickle
        import json
        
        # Load model
        with open(test_model_path, 'rb') as f:
            model_package = pickle.load(f)
        
        print("✓ Model loaded successfully")
        print(f"  Model type: {model_package['model_type']}")
        print(f"  Features: {model_package['training_history']['n_features']}")
        print(f"  Training samples: {model_package['training_history']['n_samples']}")
        
        # Load metadata
        with open(test_model_path.with_suffix('.json'), 'r') as f:
            metadata = json.load(f)
        
        print("✓ Metadata loaded successfully")
        
        # Check performance
        if 'evaluation_results' in metadata:
            if 'test' in metadata['evaluation_results']:
                results = metadata['evaluation_results']['test']
                accuracy = results['accuracy']
                pain_recall = results['pain_recall']
                
                print(f"\nModel Performance:")
                print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
                print(f"  Pain Recall: {pain_recall:.4f} ({pain_recall*100:.2f}%)")
                
                # Note: With small synthetic dataset, performance may not meet requirements
                print("\nNote: This is a test with minimal synthetic data.")
                print("Real models require larger, real-world datasets.")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Success!
    print(f"\n{'='*60}")
    print("✅ All Tests Passed!")
    print(f"{'='*60}")
    print("\nThe training pipeline is working correctly.")
    print("\nTest artifacts created:")
    print(f"  Data: {test_data_dir}")
    print(f"  Features: {test_features_dir}")
    print(f"  Model: {test_model_path}")
    print("\nTo clean up test files:")
    print(f"  rm -rf {test_data_dir} {test_features_dir} {test_model_path}*")
    print(f"{'='*60}")
    
    return 0


if __name__ == '__main__':
    exit(main())
