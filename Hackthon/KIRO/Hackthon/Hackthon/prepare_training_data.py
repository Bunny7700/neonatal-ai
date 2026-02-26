#!/usr/bin/env python3
"""
Training Data Preparation Script

This script prepares infant cry audio data for training the cry classifier.
It handles:
- Audio resampling to 16 kHz
- Amplitude normalization
- Silence trimming
- Label mapping from various datasets
- Train/validation/test splitting
- File organization

Usage:
    python prepare_training_data.py --input data/raw --output data/processed
    python prepare_training_data.py --input data/raw --output data/processed --augment
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import librosa
import soundfile as sf
from sklearn.model_selection import train_test_split


# Label mapping from various datasets to our 5 categories
LABEL_MAPPINGS = {
    # Baby Chillanto / Donate-a-Cry mappings
    'hungry': 'hunger',
    'hunger': 'hunger',
    'tired': 'sleep_discomfort',
    'sleepy': 'sleep_discomfort',
    'uncomfortable': 'sleep_discomfort',
    'discomfort': 'sleep_discomfort',
    'pain': 'pain_distress',
    'belly_pain': 'pain_distress',
    'distress': 'pain_distress',
    'burping': 'diaper_change',
    'dirty_diaper': 'diaper_change',
    'diaper': 'diaper_change',
    'unknown': 'normal_unknown',
    'other': 'normal_unknown',
    'normal': 'normal_unknown',
}

# Target categories
CATEGORIES = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']

# Audio parameters
TARGET_SAMPLE_RATE = 16000
MIN_DURATION = 0.5  # seconds
MAX_DURATION = 5.0  # seconds
SILENCE_THRESHOLD = 0.02  # amplitude threshold for silence detection


class DataPreparer:
    """Prepares training data for cry classification"""
    
    def __init__(self, input_dir: str, output_dir: str, target_sr: int = TARGET_SAMPLE_RATE):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.target_sr = target_sr
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'category_counts': {cat: 0 for cat in CATEGORIES}
        }
        
    def prepare_all(self, test_size: float = 0.15, val_size: float = 0.15, random_seed: int = 42):
        """
        Prepare all data: preprocess, split, and organize
        
        Args:
            test_size: Fraction of data for test set
            val_size: Fraction of data for validation set
            random_seed: Random seed for reproducibility
        """
        print("=" * 60)
        print("Training Data Preparation")
        print("=" * 60)
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Target sample rate: {self.target_sr} Hz")
        print(f"Split: {1-test_size-val_size:.0%} train, {val_size:.0%} val, {test_size:.0%} test")
        print()
        
        # Create output directories
        self._create_output_dirs()
        
        # Discover and process audio files
        print("Step 1: Discovering audio files...")
        audio_files = self._discover_audio_files()
        print(f"Found {len(audio_files)} audio files")
        print()
        
        # Process audio files
        print("Step 2: Processing audio files...")
        processed_data = self._process_audio_files(audio_files)
        print(f"Successfully processed {len(processed_data)} files")
        print()
        
        # Split data
        print("Step 3: Splitting into train/val/test sets...")
        splits = self._split_data(processed_data, test_size, val_size, random_seed)
        print(f"Train: {len(splits['train'])} samples")
        print(f"Validation: {len(splits['validation'])} samples")
        print(f"Test: {len(splits['test'])} samples")
        print()
        
        # Save organized data
        print("Step 4: Saving organized data...")
        self._save_splits(splits)
        print()
        
        # Print statistics
        self._print_statistics()
        
        # Save metadata
        self._save_metadata(splits)
        
        print("\n" + "=" * 60)
        print("Data preparation complete!")
        print("=" * 60)
        
    def _create_output_dirs(self):
        """Create output directory structure"""
        for split in ['train', 'validation', 'test']:
            for category in CATEGORIES:
                dir_path = self.output_dir / split / category
                dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata directory
        (self.output_dir / 'metadata').mkdir(parents=True, exist_ok=True)
        
    def _discover_audio_files(self) -> List[Tuple[Path, str]]:
        """
        Discover audio files and infer labels from directory structure or filenames
        
        Returns:
            List of (file_path, label) tuples
        """
        audio_files = []
        audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        
        for file_path in self.input_dir.rglob('*'):
            if file_path.suffix.lower() in audio_extensions:
                # Try to infer label from parent directory name
                label = self._infer_label(file_path)
                if label:
                    audio_files.append((file_path, label))
                    self.stats['total_files'] += 1
                    
        return audio_files
    
    def _infer_label(self, file_path: Path) -> str:
        """
        Infer label from file path or filename
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Mapped category label or None if cannot infer
        """
        # Check parent directory name
        parent_name = file_path.parent.name.lower()
        if parent_name in LABEL_MAPPINGS:
            return LABEL_MAPPINGS[parent_name]
        
        # Check filename
        filename = file_path.stem.lower()
        for original_label, mapped_label in LABEL_MAPPINGS.items():
            if original_label in filename:
                return mapped_label
                
        # Check grandparent directory (some datasets have nested structure)
        grandparent_name = file_path.parent.parent.name.lower()
        if grandparent_name in LABEL_MAPPINGS:
            return LABEL_MAPPINGS[grandparent_name]
        
        return None
    
    def _process_audio_files(self, audio_files: List[Tuple[Path, str]]) -> List[Dict]:
        """
        Process audio files: resample, normalize, trim silence
        
        Args:
            audio_files: List of (file_path, label) tuples
            
        Returns:
            List of processed audio data dictionaries
        """
        processed_data = []
        
        for i, (file_path, label) in enumerate(audio_files):
            try:
                # Load audio
                audio, sr = librosa.load(file_path, sr=self.target_sr, mono=True)
                
                # Trim silence
                audio = self._trim_silence(audio)
                
                # Check duration
                duration = len(audio) / self.target_sr
                if duration < MIN_DURATION:
                    print(f"Skipping {file_path.name}: too short ({duration:.2f}s)")
                    self.stats['skipped_files'] += 1
                    continue
                
                # Split if too long
                if duration > MAX_DURATION:
                    segments = self._split_audio(audio, MAX_DURATION)
                    for j, segment in enumerate(segments):
                        processed_data.append({
                            'audio': segment,
                            'label': label,
                            'original_file': str(file_path),
                            'segment_index': j,
                            'duration': len(segment) / self.target_sr
                        })
                else:
                    # Normalize
                    audio = self._normalize_audio(audio)
                    
                    processed_data.append({
                        'audio': audio,
                        'label': label,
                        'original_file': str(file_path),
                        'segment_index': 0,
                        'duration': duration
                    })
                
                self.stats['processed_files'] += 1
                self.stats['category_counts'][label] += 1
                
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(audio_files)} files...")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                self.stats['skipped_files'] += 1
                continue
        
        return processed_data
    
    def _trim_silence(self, audio: np.ndarray) -> np.ndarray:
        """
        Trim silence from beginning and end of audio
        
        Args:
            audio: Audio signal
            
        Returns:
            Trimmed audio
        """
        # Use librosa's trim function
        trimmed, _ = librosa.effects.trim(audio, top_db=20)
        return trimmed
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio amplitude to [-1, 1] range
        
        Args:
            audio: Audio signal
            
        Returns:
            Normalized audio
        """
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
        return audio
    
    def _split_audio(self, audio: np.ndarray, max_duration: float) -> List[np.ndarray]:
        """
        Split long audio into segments
        
        Args:
            audio: Audio signal
            max_duration: Maximum duration per segment in seconds
            
        Returns:
            List of audio segments
        """
        segment_length = int(max_duration * self.target_sr)
        segments = []
        
        for i in range(0, len(audio), segment_length):
            segment = audio[i:i + segment_length]
            if len(segment) >= int(MIN_DURATION * self.target_sr):
                segment = self._normalize_audio(segment)
                segments.append(segment)
        
        return segments
    
    def _split_data(self, processed_data: List[Dict], test_size: float, 
                    val_size: float, random_seed: int) -> Dict[str, List[Dict]]:
        """
        Split data into train/validation/test sets with stratification
        
        Args:
            processed_data: List of processed audio data
            test_size: Fraction for test set
            val_size: Fraction for validation set
            random_seed: Random seed
            
        Returns:
            Dictionary with 'train', 'validation', 'test' keys
        """
        # Extract labels for stratification
        labels = [item['label'] for item in processed_data]
        
        # First split: train+val vs test
        train_val_data, test_data = train_test_split(
            processed_data, 
            test_size=test_size,
            stratify=labels,
            random_state=random_seed
        )
        
        # Second split: train vs val
        train_val_labels = [item['label'] for item in train_val_data]
        val_size_adjusted = val_size / (1 - test_size)  # Adjust for remaining data
        
        train_data, val_data = train_test_split(
            train_val_data,
            test_size=val_size_adjusted,
            stratify=train_val_labels,
            random_state=random_seed
        )
        
        return {
            'train': train_data,
            'validation': val_data,
            'test': test_data
        }
    
    def _save_splits(self, splits: Dict[str, List[Dict]]):
        """
        Save split data to organized directory structure
        
        Args:
            splits: Dictionary with train/validation/test data
        """
        for split_name, split_data in splits.items():
            print(f"Saving {split_name} set...")
            
            for i, item in enumerate(split_data):
                # Generate filename
                original_name = Path(item['original_file']).stem
                segment_idx = item['segment_index']
                filename = f"{original_name}_seg{segment_idx}_{i:04d}.wav"
                
                # Save audio file
                output_path = self.output_dir / split_name / item['label'] / filename
                sf.write(output_path, item['audio'], self.target_sr)
    
    def _save_metadata(self, splits: Dict[str, List[Dict]]):
        """
        Save metadata CSV files for each split
        
        Args:
            splits: Dictionary with train/validation/test data
        """
        import csv
        
        for split_name, split_data in splits.items():
            csv_path = self.output_dir / 'metadata' / f'{split_name}_labels.csv'
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['filename', 'label', 'duration', 'original_file'])
                
                for i, item in enumerate(split_data):
                    original_name = Path(item['original_file']).stem
                    segment_idx = item['segment_index']
                    filename = f"{original_name}_seg{segment_idx}_{i:04d}.wav"
                    
                    writer.writerow([
                        filename,
                        item['label'],
                        f"{item['duration']:.3f}",
                        item['original_file']
                    ])
        
        # Save overall statistics
        stats_path = self.output_dir / 'metadata' / 'preparation_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def _print_statistics(self):
        """Print data preparation statistics"""
        print("=" * 60)
        print("Data Preparation Statistics")
        print("=" * 60)
        print(f"Total files discovered: {self.stats['total_files']}")
        print(f"Successfully processed: {self.stats['processed_files']}")
        print(f"Skipped files: {self.stats['skipped_files']}")
        print()
        print("Category distribution:")
        for category, count in self.stats['category_counts'].items():
            print(f"  {category:20s}: {count:4d} samples")
        print()


def main():
    parser = argparse.ArgumentParser(description='Prepare training data for cry classification')
    parser.add_argument('--input', type=str, required=True,
                       help='Input directory containing raw audio files')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for processed data')
    parser.add_argument('--sample-rate', type=int, default=TARGET_SAMPLE_RATE,
                       help='Target sample rate (default: 16000 Hz)')
    parser.add_argument('--test-size', type=float, default=0.15,
                       help='Fraction of data for test set (default: 0.15)')
    parser.add_argument('--val-size', type=float, default=0.15,
                       help='Fraction of data for validation set (default: 0.15)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1
    
    if args.test_size + args.val_size >= 1.0:
        print("Error: test_size + val_size must be < 1.0")
        return 1
    
    # Prepare data
    preparer = DataPreparer(args.input, args.output, args.sample_rate)
    preparer.prepare_all(args.test_size, args.val_size, args.seed)
    
    return 0


if __name__ == '__main__':
    exit(main())
