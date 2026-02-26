#!/usr/bin/env python3
"""
Synthetic Training Data Generator

This script generates synthetic infant cry audio for testing the training pipeline.
The synthetic data mimics real cry characteristics but is not suitable for
production model training.

Usage:
    python generate_synthetic_data.py --output data/synthetic --samples 100
"""

import argparse
import os
from pathlib import Path
import numpy as np
import soundfile as sf

# Categories
CATEGORIES = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']

# Audio parameters
SAMPLE_RATE = 16000
MIN_DURATION = 1.0  # seconds
MAX_DURATION = 3.0  # seconds

# Cry characteristics (based on infant cry research)
CRY_CHARACTERISTICS = {
    'hunger': {
        'base_freq': 400,  # Hz - rhythmic, moderate pitch
        'freq_variation': 50,
        'intensity': 0.6,
        'intensity_variation': 0.1,
        'rhythm_period': 0.5,  # seconds - regular rhythm
    },
    'sleep_discomfort': {
        'base_freq': 350,  # Hz - lower pitch, whiny
        'freq_variation': 30,
        'intensity': 0.4,
        'intensity_variation': 0.15,
        'rhythm_period': 0.8,  # slower, irregular
    },
    'pain_distress': {
        'base_freq': 500,  # Hz - high pitch, sudden onset
        'freq_variation': 100,
        'intensity': 0.8,
        'intensity_variation': 0.05,
        'rhythm_period': 0.3,  # fast, urgent
    },
    'diaper_change': {
        'base_freq': 380,  # Hz - moderate, fussy
        'freq_variation': 40,
        'intensity': 0.5,
        'intensity_variation': 0.12,
        'rhythm_period': 0.6,
    },
    'normal_unknown': {
        'base_freq': 370,  # Hz - variable
        'freq_variation': 60,
        'intensity': 0.5,
        'intensity_variation': 0.2,
        'rhythm_period': 0.7,
    }
}


class SyntheticDataGenerator:
    """Generates synthetic infant cry audio"""
    
    def __init__(self, output_dir: str, sample_rate: int = SAMPLE_RATE):
        self.output_dir = Path(output_dir)
        self.sample_rate = sample_rate
        
    def generate_dataset(self, samples_per_category: int, test_size: float = 0.15, 
                        val_size: float = 0.15, random_seed: int = 42):
        """
        Generate complete synthetic dataset with train/val/test splits
        
        Args:
            samples_per_category: Number of samples to generate per category
            test_size: Fraction for test set
            val_size: Fraction for validation set
            random_seed: Random seed for reproducibility
        """
        np.random.seed(random_seed)
        
        print("=" * 60)
        print("Synthetic Data Generation")
        print("=" * 60)
        print(f"Output directory: {self.output_dir}")
        print(f"Samples per category: {samples_per_category}")
        print(f"Sample rate: {self.sample_rate} Hz")
        print()
        
        # Calculate split sizes
        n_test = int(samples_per_category * test_size)
        n_val = int(samples_per_category * val_size)
        n_train = samples_per_category - n_test - n_val
        
        splits = {
            'train': n_train,
            'validation': n_val,
            'test': n_test
        }
        
        print(f"Split sizes: train={n_train}, val={n_val}, test={n_test}")
        print()
        
        # Create directory structure
        self._create_directories()
        
        # Generate data for each split and category
        total_generated = 0
        for split, n_samples in splits.items():
            print(f"Generating {split} set...")
            
            for category in CATEGORIES:
                print(f"  {category}: {n_samples} samples")
                
                for i in range(n_samples):
                    # Generate synthetic cry
                    audio = self._generate_cry(category)
                    
                    # Save audio file
                    filename = f"{category}_{split}_{i:04d}.wav"
                    output_path = self.output_dir / split / category / filename
                    sf.write(output_path, audio, self.sample_rate)
                    
                    total_generated += 1
            
            print()
        
        print("=" * 60)
        print(f"Generated {total_generated} synthetic audio files")
        print("=" * 60)
        print("\nNOTE: This synthetic data is for testing the training pipeline only.")
        print("For production models, use real infant cry datasets.")
        print("=" * 60)
    
    def _create_directories(self):
        """Create output directory structure"""
        for split in ['train', 'validation', 'test']:
            for category in CATEGORIES:
                dir_path = self.output_dir / split / category
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_cry(self, category: str) -> np.ndarray:
        """
        Generate synthetic cry audio for a category
        
        Args:
            category: Cry category
            
        Returns:
            Audio signal as numpy array
        """
        # Get characteristics for this category
        char = CRY_CHARACTERISTICS[category]
        
        # Random duration
        duration = np.random.uniform(MIN_DURATION, MAX_DURATION)
        n_samples = int(duration * self.sample_rate)
        
        # Time array
        t = np.linspace(0, duration, n_samples)
        
        # Generate base frequency modulation (crying rhythm)
        rhythm_freq = 1.0 / char['rhythm_period']
        freq_modulation = char['base_freq'] + char['freq_variation'] * np.sin(2 * np.pi * rhythm_freq * t)
        
        # Add random frequency variations (natural cry variations)
        freq_noise = np.random.randn(n_samples) * char['freq_variation'] * 0.1
        freq_modulation += freq_noise
        
        # Generate phase for frequency modulation
        phase = np.cumsum(2 * np.pi * freq_modulation / self.sample_rate)
        
        # Generate base signal (fundamental frequency)
        signal = np.sin(phase)
        
        # Add harmonics (typical of infant cries)
        signal += 0.3 * np.sin(2 * phase)  # 2nd harmonic
        signal += 0.15 * np.sin(3 * phase)  # 3rd harmonic
        signal += 0.08 * np.sin(4 * phase)  # 4th harmonic
        
        # Generate amplitude envelope (crying pattern)
        envelope = self._generate_envelope(t, char)
        
        # Apply envelope
        signal *= envelope
        
        # Add noise (breath sounds, etc.)
        noise = np.random.randn(n_samples) * 0.05
        signal += noise
        
        # Normalize
        signal = signal / np.abs(signal).max() * char['intensity']
        
        # Add random intensity variations
        intensity_mod = 1.0 + np.random.randn(n_samples) * char['intensity_variation']
        intensity_mod = np.clip(intensity_mod, 0.5, 1.5)
        signal *= intensity_mod
        
        # Final normalization
        signal = signal / np.abs(signal).max() * 0.95
        
        return signal.astype(np.float32)
    
    def _generate_envelope(self, t: np.ndarray, char: dict) -> np.ndarray:
        """
        Generate amplitude envelope for cry
        
        Args:
            t: Time array
            char: Cry characteristics
            
        Returns:
            Envelope array
        """
        duration = t[-1]
        
        # Attack (cry onset)
        attack_time = 0.05
        attack_samples = int(attack_time * self.sample_rate)
        attack = np.linspace(0, 1, attack_samples)
        
        # Sustain (main cry)
        sustain_time = duration - attack_time - 0.1
        sustain_samples = int(sustain_time * self.sample_rate)
        
        # Add rhythmic modulation to sustain
        rhythm_freq = 1.0 / char['rhythm_period']
        t_sustain = np.linspace(0, sustain_time, sustain_samples)
        sustain = 0.8 + 0.2 * np.sin(2 * np.pi * rhythm_freq * t_sustain)
        
        # Release (cry ending)
        release_samples = len(t) - attack_samples - sustain_samples
        release = np.linspace(1, 0, release_samples)
        
        # Concatenate
        envelope = np.concatenate([attack, sustain, release])
        
        # Ensure same length as time array
        if len(envelope) < len(t):
            envelope = np.pad(envelope, (0, len(t) - len(envelope)), mode='edge')
        elif len(envelope) > len(t):
            envelope = envelope[:len(t)]
        
        return envelope


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic training data')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for synthetic data')
    parser.add_argument('--samples', type=int, default=50,
                       help='Number of samples per category (default: 50)')
    parser.add_argument('--sample-rate', type=int, default=SAMPLE_RATE,
                       help='Sample rate in Hz (default: 16000)')
    parser.add_argument('--test-size', type=float, default=0.15,
                       help='Fraction for test set (default: 0.15)')
    parser.add_argument('--val-size', type=float, default=0.15,
                       help='Fraction for validation set (default: 0.15)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.test_size + args.val_size >= 1.0:
        print("Error: test_size + val_size must be < 1.0")
        return 1
    
    # Generate data
    generator = SyntheticDataGenerator(args.output, args.sample_rate)
    generator.generate_dataset(
        args.samples,
        args.test_size,
        args.val_size,
        args.seed
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
