# feature_extractor.py
"""
Feature Extractor Module for Neonatal Cry Detection System

This module provides comprehensive audio feature extraction functionality including:
- Pitch extraction using autocorrelation
- Frequency spectrum analysis
- Intensity (RMS energy) calculation
- MFCC extraction (13 coefficients)
- Duration calculation
- Additional spectral features (centroid, rolloff, zero-crossing rate)

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional


class FeatureExtractor:
    """
    Extracts acoustic features from preprocessed audio signals.
    
    Computes a comprehensive set of features including pitch, intensity,
    MFCCs, and spectral characteristics for cry classification.
    """
    
    def __init__(self, sample_rate: int = 16000, n_mfcc: int = 13):
        """
        Initialize feature extractor with parameters.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
            n_mfcc: Number of MFCC coefficients to extract (default: 13)
        """
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        
    def extract_pitch(self, audio: np.ndarray) -> float:
        """
        Extract fundamental frequency (F0) using autocorrelation.
        
        Uses librosa's piptrack for pitch detection, which is based on
        instantaneous frequency estimation. Returns the median pitch
        across all frames.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Fundamental frequency in Hz (0.0 if pitch cannot be detected)
            
        Validates: Requirements 3.1
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            # Use librosa's piptrack for pitch detection
            # fmin and fmax set to typical infant cry range (200-600 Hz)
            pitches, magnitudes = librosa.piptrack(
                y=audio,
                sr=self.sample_rate,
                fmin=200,
                fmax=600,
                threshold=0.1
            )
            
            # Extract pitch values where magnitude is highest
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            # Return median pitch (more robust than mean)
            if len(pitch_values) > 0:
                return float(np.median(pitch_values))
            else:
                return 0.0
                
        except Exception as e:
            # If pitch detection fails, return 0.0
            return 0.0
    
    def extract_frequency_spectrum(self, audio: np.ndarray) -> np.ndarray:
        """
        Compute power spectral density.
        
        Uses FFT to compute the frequency spectrum, focusing on the
        frequency range relevant for infant cries (0-2000 Hz).
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Power spectral density as numpy array
            
        Validates: Requirements 3.2
        """
        if len(audio) == 0:
            return np.array([])
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            # Compute FFT
            n_fft = min(2048, len(audio))
            fft = np.fft.rfft(audio, n=n_fft)
            
            # Compute power spectral density
            psd = np.abs(fft) ** 2
            
            # Normalize
            psd = psd / np.sum(psd) if np.sum(psd) > 0 else psd
            
            return psd
            
        except Exception as e:
            return np.array([])
    
    def extract_intensity(self, audio: np.ndarray) -> float:
        """
        Compute RMS energy of signal.
        
        Calculates the root mean square (RMS) energy and converts to
        decibel scale for better interpretability.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            RMS energy in dB (0.0 if audio is silent)
            
        Validates: Requirements 3.3
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            # Compute RMS energy
            rms = np.sqrt(np.mean(audio ** 2))
            
            # Convert to dB scale (with floor to avoid log(0))
            if rms > 1e-10:
                rms_db = 20 * np.log10(rms)
            else:
                rms_db = -100.0  # Very quiet signal
            
            return float(rms_db)
            
        except Exception as e:
            return 0.0
    
    def extract_mfccs(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract Mel-Frequency Cepstral Coefficients.
        
        Computes MFCCs which capture the spectral envelope of the audio
        signal. Returns the mean MFCC values across all frames.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Array of n_mfcc MFCC coefficients (zeros if extraction fails)
            
        Validates: Requirements 3.4
        """
        if len(audio) == 0:
            return np.zeros(self.n_mfcc)
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            # Extract MFCCs using librosa
            mfccs = librosa.feature.mfcc(
                y=audio,
                sr=self.sample_rate,
                n_mfcc=self.n_mfcc
            )
            
            # Return mean across time frames
            mfcc_mean = np.mean(mfccs, axis=1)
            
            return mfcc_mean
            
        except Exception as e:
            return np.zeros(self.n_mfcc)
    
    def extract_duration(self, audio: np.ndarray) -> float:
        """
        Compute duration of cry episode in seconds.
        
        Calculates the duration based on the number of samples and
        sample rate.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Duration in seconds
            
        Validates: Requirements 3.5
        """
        if len(audio) == 0:
            return 0.0
        
        try:
            duration = len(audio) / self.sample_rate
            return float(duration)
        except Exception as e:
            return 0.0
    
    def extract_spectral_centroid(self, audio: np.ndarray) -> float:
        """
        Compute spectral centroid (center of mass of spectrum).
        
        The spectral centroid indicates where the "center of mass" of
        the spectrum is located. Higher values indicate brighter sounds.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Spectral centroid in Hz
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            centroid = librosa.feature.spectral_centroid(
                y=audio,
                sr=self.sample_rate
            )
            return float(np.mean(centroid))
        except Exception as e:
            return 0.0
    
    def extract_spectral_rolloff(self, audio: np.ndarray) -> float:
        """
        Compute spectral rolloff frequency.
        
        The spectral rolloff is the frequency below which 85% of the
        spectral energy is contained.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Spectral rolloff frequency in Hz
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            rolloff = librosa.feature.spectral_rolloff(
                y=audio,
                sr=self.sample_rate,
                roll_percent=0.85
            )
            return float(np.mean(rolloff))
        except Exception as e:
            return 0.0
    
    def extract_zero_crossing_rate(self, audio: np.ndarray) -> float:
        """
        Compute zero-crossing rate.
        
        The zero-crossing rate is the rate at which the signal changes
        sign. It's a simple measure of the frequency content.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Zero-crossing rate (normalized)
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            zcr = librosa.feature.zero_crossing_rate(audio)
            return float(np.mean(zcr))
        except Exception as e:
            return 0.0
    
    def extract_pitch_std(self, audio: np.ndarray) -> float:
        """
        Compute standard deviation of pitch values.
        
        Measures the variation in pitch across the audio signal.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Standard deviation of pitch in Hz
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            pitches, magnitudes = librosa.piptrack(
                y=audio,
                sr=self.sample_rate,
                fmin=200,
                fmax=600,
                threshold=0.1
            )
            
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 1:
                return float(np.std(pitch_values))
            else:
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def extract_intensity_std(self, audio: np.ndarray) -> float:
        """
        Compute standard deviation of intensity values.
        
        Measures the variation in energy across the audio signal.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Standard deviation of intensity in dB
        """
        if len(audio) == 0:
            return 0.0
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        try:
            # Compute frame-wise RMS energy
            frame_length = int(0.025 * self.sample_rate)  # 25ms frames
            hop_length = int(0.010 * self.sample_rate)    # 10ms hop
            
            if frame_length < 1:
                frame_length = 1
            if hop_length < 1:
                hop_length = 1
            
            energy_values = []
            for i in range(0, len(audio) - frame_length + 1, hop_length):
                frame = audio[i:i + frame_length]
                rms = np.sqrt(np.mean(frame ** 2))
                if rms > 1e-10:
                    rms_db = 20 * np.log10(rms)
                    energy_values.append(rms_db)
            
            if len(energy_values) > 1:
                return float(np.std(energy_values))
            else:
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def extract_all_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Extract complete feature vector from audio signal.
        
        Computes all available features and returns them in a dictionary
        format. This is the main method to use for feature extraction.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Dictionary containing all extracted features:
                - pitch: Fundamental frequency (Hz)
                - pitch_std: Pitch variation (Hz)
                - intensity: RMS energy (dB)
                - intensity_std: Energy variation (dB)
                - mfccs: Array of 13 MFCC coefficients
                - spectral_centroid: Center of mass of spectrum (Hz)
                - spectral_rolloff: Frequency below which 85% of energy is contained (Hz)
                - zero_crossing_rate: Rate of sign changes (normalized)
                - duration: Duration of audio (seconds)
                - frequency_spectrum: Power spectral density array
                
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
        """
        features = {
            'pitch': self.extract_pitch(audio),
            'pitch_std': self.extract_pitch_std(audio),
            'intensity': self.extract_intensity(audio),
            'intensity_std': self.extract_intensity_std(audio),
            'mfccs': self.extract_mfccs(audio),
            'spectral_centroid': self.extract_spectral_centroid(audio),
            'spectral_rolloff': self.extract_spectral_rolloff(audio),
            'zero_crossing_rate': self.extract_zero_crossing_rate(audio),
            'duration': self.extract_duration(audio),
            'frequency_spectrum': self.extract_frequency_spectrum(audio)
        }
        
        return features
