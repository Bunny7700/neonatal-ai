#!/usr/bin/env python3
"""
Training Data Verification Script

This script verifies the quality and completeness of prepared training data.

Usage:
    python verify_training_data.py --data data/processed
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List
import numpy as np
import librosa
import soundfile as sf

# Categories
CATEGORIES = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']

# Quality thresholds
MIN_SAMPLES_PER_CATEGORY = 20
MIN_TOTAL_SAMPLES = 100
MIN_DURATION = 0.5  # seconds
MAX_DURATION = 5.0  # seconds
TARGET_SAMPLE_RATE = 16000


class DataVerifier:
    """Verifies training data quality and completeness"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.issues = []
        self.warnings = []
        self.stats = {}
        
    def verify_all(self) -> bool:
        """
        Run all verification checks
        
        Returns:
            True if all checks pass, False otherwise
        """
        print("=" * 60)
        print("Training Data Verification")
        print("=" * 60)
        print(f"Data directory: {self.data_dir}")
        print()
        
        # Check directory structure
        print("Check 1: Directory structure...")
        if not self._check_directory_structure():
            return False
        print("  ✓ Directory structure is valid")
        print()
        
        # Check sample counts
        print("Check 2: Sample counts...")
        if not self._check_sample_counts():
            return False
        print("  ✓ Sample counts are sufficient")
        print()
        
        # Check audio quality
        print("Check 3: Audio quality...")
        if not self._check_audio_quality():
            return False
        print("  ✓ Audio quality is acceptable")
        print()
        
        # Check label distribution
        print("Check 4: Label distribution...")
        self._check_label_distribution()
        print()
        
        # Print summary
        self._print_summary()
        
        return len(self.issues) == 0
    
    def _check_directory_structure(self) -> bool:
        """Check if directory structure is correct"""
        required_splits = ['train', 'validation', 'test']
        
        for split in required_splits:
            split_dir = self.data_dir / split
            if not split_dir.exists():
                self.issues.append(f"Missing {split} directory")
                return False
            
            for category in CATEGORIES:
                category_dir = split_dir / category
                if not category_dir.exists():
                    self.issues.append(f"Missing {split}/{category} directory")
                    return False
        
        return True
    
    def _check_sample_counts(self) -> bool:
        """Check if there are enough samples"""
        self.stats['counts'] = {}
        
        for split in ['train', 'validation', 'test']:
            split_counts = {}
            total_count = 0
            
            for category in CATEGORIES:
                category_dir = self.data_dir / split / category
                audio_files = list(category_dir.glob('*.wav'))
                count = len(audio_files)
                split_counts[category] = count
                total_count += count
                
                if split == 'train' and count < MIN_SAMPLES_PER_CATEGORY:
                    self.issues.append(
                        f"Insufficient samples in train/{category}: "
                        f"{count} < {MIN_SAMPLES_PER_CATEGORY}"
                    )
            
            split_counts['total'] = total_count
            self.stats['counts'][split] = split_counts
            
            if split == 'train' and total_count < MIN_TOTAL_SAMPLES:
                self.issues.append(
                    f"Insufficient total training samples: "
                    f"{total_count} < {MIN_TOTAL_SAMPLES}"
                )
        
        return len(self.issues) == 0
    
    def _check_audio_quality(self) -> bool:
        """Check audio file quality"""
        issues_found = 0
        files_checked = 0
        max_files_per_category = 10  # Sample check
        
        for split in ['train', 'validation', 'test']:
            for category in CATEGORIES:
                category_dir = self.data_dir / split / category
                audio_files = list(category_dir.glob('*.wav'))[:max_files_per_category]
                
                for audio_file in audio_files:
                    try:
                        # Load audio
                        audio, sr = librosa.load(audio_file, sr=None, mono=True)
                        files_checked += 1
                        
                        # Check sample rate
                        if sr != TARGET_SAMPLE_RATE:
                            self.warnings.append(
                                f"{audio_file.name}: Sample rate {sr} != {TARGET_SAMPLE_RATE}"
                            )
                        
                        # Check duration
                        duration = len(audio) / sr
                        if duration < MIN_DURATION:
                            self.warnings.append(
                                f"{audio_file.name}: Duration {duration:.2f}s < {MIN_DURATION}s"
                            )
                        elif duration > MAX_DURATION:
                            self.warnings.append(
                                f"{audio_file.name}: Duration {duration:.2f}s > {MAX_DURATION}s"
                            )
                        
                        # Check for invalid values
                        if np.isnan(audio).any():
                            self.issues.append(f"{audio_file.name}: Contains NaN values")
                            issues_found += 1
                        
                        if np.isinf(audio).any():
                            self.issues.append(f"{audio_file.name}: Contains Inf values")
                            issues_found += 1
                        
                        # Check amplitude range
                        max_amp = np.abs(audio).max()
                        if max_amp > 1.0:
                            self.warnings.append(
                                f"{audio_file.name}: Amplitude {max_amp:.2f} > 1.0 (not normalized)"
                            )
                        
                    except Exception as e:
                        self.issues.append(f"{audio_file.name}: Failed to load - {e}")
                        issues_found += 1
        
        print(f"  Checked {files_checked} audio files")
        if issues_found > 0:
            print(f"  Found {issues_found} corrupted files")
            return False
        
        if len(self.warnings) > 0:
            print(f"  Found {len(self.warnings)} warnings (non-critical)")
        
        return True
    
    def _check_label_distribution(self):
        """Check if labels are balanced"""
        train_counts = self.stats['counts']['train']
        
        # Calculate balance metrics
        category_counts = [train_counts[cat] for cat in CATEGORIES]
        mean_count = np.mean(category_counts)
        std_count = np.std(category_counts)
        
        print(f"  Mean samples per category: {mean_count:.1f}")
        print(f"  Std deviation: {std_count:.1f}")
        
        # Check for severe imbalance
        for category in CATEGORIES:
            count = train_counts[category]
            ratio = count / mean_count if mean_count > 0 else 0
            
            if ratio < 0.5:
                self.warnings.append(
                    f"Category '{category}' is underrepresented: "
                    f"{count} samples ({ratio:.1%} of mean)"
                )
            elif ratio > 2.0:
                self.warnings.append(
                    f"Category '{category}' is overrepresented: "
                    f"{count} samples ({ratio:.1%} of mean)"
                )
        
        if len(self.warnings) == 0:
            print("  ✓ Labels are reasonably balanced")
        else:
            print(f"  ⚠ Found {len(self.warnings)} balance warnings")
    
    def _print_summary(self):
        """Print verification summary"""
        print("=" * 60)
        print("Verification Summary")
        print("=" * 60)
        
        # Print counts
        print("\nSample Counts:")
        print(f"{'Split':<12} {'Total':>8} {'Hunger':>8} {'Sleep':>8} {'Pain':>8} {'Diaper':>8} {'Unknown':>8}")
        print("-" * 72)
        
        for split in ['train', 'validation', 'test']:
            counts = self.stats['counts'][split]
            print(f"{split:<12} {counts['total']:>8} "
                  f"{counts['hunger']:>8} "
                  f"{counts['sleep_discomfort']:>8} "
                  f"{counts['pain_distress']:>8} "
                  f"{counts['diaper_change']:>8} "
                  f"{counts['normal_unknown']:>8}")
        
        # Print issues
        if len(self.issues) > 0:
            print(f"\n❌ Found {len(self.issues)} critical issues:")
            for issue in self.issues[:10]:  # Show first 10
                print(f"  - {issue}")
            if len(self.issues) > 10:
                print(f"  ... and {len(self.issues) - 10} more")
        else:
            print("\n✓ No critical issues found")
        
        # Print warnings
        if len(self.warnings) > 0:
            print(f"\n⚠ Found {len(self.warnings)} warnings:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Verify training data quality')
    parser.add_argument('--data', type=str, required=True,
                       help='Data directory containing train/val/test splits')
    
    args = parser.parse_args()
    
    # Validate data directory
    if not os.path.exists(args.data):
        print(f"Error: Data directory '{args.data}' does not exist")
        return 1
    
    # Run verification
    verifier = DataVerifier(args.data)
    success = verifier.verify_all()
    
    if success:
        print("\n✓ All verification checks passed!")
        return 0
    else:
        print("\n❌ Verification failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    exit(main())
