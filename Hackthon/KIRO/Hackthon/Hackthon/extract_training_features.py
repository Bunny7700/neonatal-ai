#!/usr/bin/env python3
"""
Training Feature Extraction Script

This script extracts acoustic features from preprocessed training data
and saves them in a format suitable for model training.

Usage:
    python extract_training_features.py --input data/processed --output data/features
"""

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import librosa
from tqdm import tqdm

# Import our feature extractor
from feature_extractor import FeatureExtractor

# Categories
CATEGORIES = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']


class TrainingFeatureExtractor:
    """Extracts features from training data for model training"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.feature_extractor = FeatureExtractor()
        self.stats = {
            'total_files': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'category_counts': {cat: 0 for cat in CATEGORIES}
        }
        
    def extract_all(self):
        """Extract features from all splits (train, validation, test)"""
        print("=" * 60)
        print("Training Feature Extraction")
        print("=" * 60)
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each split
        for split in ['train', 'validation', 'test']:
            split_dir = self.input_dir / split
            if not split_dir.exists():
                print(f"Warning: {split} directory not found, skipping...")
                continue
            
            print(f"\nProcessing {split} set...")
            print("-" * 60)
            
            features, labels, metadata = self._extract_split_features(split_dir, split)
            
            # Save features
            self._save_features(split, features, labels, metadata)
            
            print(f"Extracted {len(features)} feature vectors from {split} set")
        
        # Print overall statistics
        self._print_statistics()
        
        # Save statistics
        self._save_statistics()
        
        print("\n" + "=" * 60)
        print("Feature extraction complete!")
        print("=" * 60)
        
    def _extract_split_features(self, split_dir: Path, split_name: str) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
        """
        Extract features from all audio files in a split
        
        Args:
            split_dir: Directory containing category subdirectories
            split_name: Name of the split (train/validation/test)
            
        Returns:
            Tuple of (features array, labels array, metadata list)
        """
        all_features = []
        all_labels = []
        all_metadata = []
        
        # Process each category
        for category in CATEGORIES:
            category_dir = split_dir / category
            if not category_dir.exists():
                print(f"Warning: Category '{category}' not found in {split_name}, skipping...")
                continue
            
            # Get all audio files
            audio_files = list(category_dir.glob('*.wav'))
            print(f"  {category}: {len(audio_files)} files")
            
            # Extract features from each file
            for audio_file in tqdm(audio_files, desc=f"  Extracting {category}", leave=False):
                try:
                    # Load audio
                    audio, sr = librosa.load(audio_file, sr=16000, mono=True)
                    
                    # Extract features
                    features = self.feature_extractor.extract_all_features(audio)
                    
                    # Convert to feature vector
                    feature_vector = self._features_to_vector(features)
                    
                    # Store
                    all_features.append(feature_vector)
                    all_labels.append(category)
                    all_metadata.append({
                        'filename': audio_file.name,
                        'category': category,
                        'split': split_name,
                        'duration': features['duration']
                    })
                    
                    self.stats['total_files'] += 1
                    self.stats['successful_extractions'] += 1
                    self.stats['category_counts'][category] += 1
                    
                except Exception as e:
                    print(f"Error extracting features from {audio_file.name}: {e}")
                    self.stats['failed_extractions'] += 1
                    continue
        
        # Convert to numpy arrays
        features_array = np.array(all_features, dtype=np.float32)
        labels_array = np.array(all_labels)
        
        return features_array, labels_array, all_metadata
    
    def _features_to_vector(self, features: Dict) -> np.ndarray:
        """
        Convert feature dictionary to flat numpy array
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Flat feature vector
        """
        # Collect all features in consistent order
        feature_list = [
            features['pitch'],
            features['pitch_std'],
            features['intensity'],
            features['intensity_std'],
            features['spectral_centroid'],
            features['spectral_rolloff'],
            features['zero_crossing_rate'],
            features['duration']
        ]
        
        # Add MFCCs (13 coefficients)
        feature_list.extend(features['mfccs'])
        
        return np.array(feature_list, dtype=np.float32)
    
    def _save_features(self, split_name: str, features: np.ndarray, 
                      labels: np.ndarray, metadata: List[Dict]):
        """
        Save features, labels, and metadata
        
        Args:
            split_name: Name of the split
            features: Feature array
            labels: Label array
            metadata: Metadata list
        """
        # Save features and labels as compressed numpy archive
        npz_path = self.output_dir / f'{split_name}_features.npz'
        np.savez_compressed(npz_path, features=features, labels=labels)
        print(f"  Saved features to {npz_path}")
        
        # Save metadata as JSON
        metadata_path = self.output_dir / f'{split_name}_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  Saved metadata to {metadata_path}")
        
        # Save labels as CSV for easy inspection
        csv_path = self.output_dir / f'{split_name}_labels.csv'
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['index', 'filename', 'label', 'duration'])
            for i, (meta, label) in enumerate(zip(metadata, labels)):
                writer.writerow([i, meta['filename'], label, f"{meta['duration']:.3f}"])
        print(f"  Saved labels to {csv_path}")
    
    def _save_statistics(self):
        """Save extraction statistics"""
        stats_path = self.output_dir / 'extraction_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"\nSaved statistics to {stats_path}")
    
    def _print_statistics(self):
        """Print extraction statistics"""
        print("\n" + "=" * 60)
        print("Feature Extraction Statistics")
        print("=" * 60)
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"Successful extractions: {self.stats['successful_extractions']}")
        print(f"Failed extractions: {self.stats['failed_extractions']}")
        print()
        print("Category distribution:")
        for category, count in self.stats['category_counts'].items():
            print(f"  {category:20s}: {count:4d} samples")
        print()


def verify_features(features_dir: str):
    """
    Verify extracted features are valid
    
    Args:
        features_dir: Directory containing extracted features
    """
    print("\n" + "=" * 60)
    print("Feature Verification")
    print("=" * 60)
    
    features_path = Path(features_dir)
    
    for split in ['train', 'validation', 'test']:
        npz_file = features_path / f'{split}_features.npz'
        
        if not npz_file.exists():
            print(f"Warning: {split} features not found")
            continue
        
        # Load features
        data = np.load(npz_file)
        features = data['features']
        labels = data['labels']
        
        print(f"\n{split.capitalize()} Set:")
        print(f"  Feature shape: {features.shape}")
        print(f"  Number of samples: {len(labels)}")
        print(f"  Feature dimension: {features.shape[1]}")
        
        # Check for invalid values
        has_nan = np.isnan(features).any()
        has_inf = np.isinf(features).any()
        
        if has_nan:
            print(f"  WARNING: Contains NaN values!")
        if has_inf:
            print(f"  WARNING: Contains Inf values!")
        
        if not has_nan and not has_inf:
            print(f"  ✓ All values are valid")
        
        # Feature statistics
        print(f"  Feature range: [{features.min():.3f}, {features.max():.3f}]")
        print(f"  Feature mean: {features.mean():.3f}")
        print(f"  Feature std: {features.std():.3f}")
        
        # Label distribution
        unique_labels, counts = np.unique(labels, return_counts=True)
        print(f"  Label distribution:")
        for label, count in zip(unique_labels, counts):
            percentage = 100 * count / len(labels)
            print(f"    {label:20s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Extract features from training data')
    parser.add_argument('--input', type=str, required=True,
                       help='Input directory containing processed audio (train/val/test splits)')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for extracted features')
    parser.add_argument('--verify', action='store_true',
                       help='Verify extracted features after extraction')
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1
    
    # Extract features
    extractor = TrainingFeatureExtractor(args.input, args.output)
    extractor.extract_all()
    
    # Verify if requested
    if args.verify:
        verify_features(args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
