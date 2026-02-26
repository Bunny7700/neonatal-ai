# audio_preprocessor.py
"""
Audio Preprocessor Module for Neonatal Cry Detection System

This module provides audio preprocessing functionality including:
- Noise reduction using spectral subtraction
- Audio segmentation based on energy thresholds
- Amplitude normalization to [-1, 1] range

Requirements: 2.1, 2.2, 2.3
"""

import numpy as np
from scipy import signal
from typing import List, Tuple


class AudioPreprocessor:
    """
    Preprocesses audio signals for cry detection and classification.
    
    Applies noise reduction, segmentation, and normalization to prepare
    audio for feature extraction and classification.
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize preprocessor with target sample rate.
        
        Args:
            sample_rate: Target sample rate in Hz (default: 16000)
        """
        self.sample_rate = sample_rate
        
    def reduce_noise(self, audio: np.ndarray, noise_profile_duration: float = 0.1) -> np.ndarray:
        """
        Apply spectral subtraction to reduce background noise.
        
        This method estimates the noise spectrum from the initial portion of the audio
        and subtracts it from the entire signal in the frequency domain.
        
        Args:
            audio: Input audio signal as numpy array
            noise_profile_duration: Duration in seconds to use for noise estimation (default: 0.1)
            
        Returns:
            Noise-reduced audio signal
            
        Validates: Requirements 2.1
        """
        if len(audio) == 0:
            return audio
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Estimate noise profile from the first portion of the audio
        noise_samples = int(noise_profile_duration * self.sample_rate)
        noise_samples = min(noise_samples, len(audio) // 4)  # Use at most 25% of audio
        
        if noise_samples < 64:  # Need minimum samples for FFT
            return audio
            
        noise_profile = audio[:noise_samples]
        
        # Compute STFT (Short-Time Fourier Transform)
        nperseg = min(256, len(audio) // 4)
        if nperseg < 16:
            return audio
            
        f, t, Zxx = signal.stft(audio, fs=self.sample_rate, nperseg=nperseg)
        
        # Estimate noise spectrum from noise profile
        _, _, noise_stft = signal.stft(noise_profile, fs=self.sample_rate, nperseg=nperseg)
        noise_magnitude = np.mean(np.abs(noise_stft), axis=1, keepdims=True)
        
        # Spectral subtraction
        signal_magnitude = np.abs(Zxx)
        signal_phase = np.angle(Zxx)
        
        # Subtract noise spectrum with over-subtraction factor
        alpha = 2.0  # Over-subtraction factor
        beta = 0.01  # Spectral floor to prevent negative values
        
        cleaned_magnitude = signal_magnitude - alpha * noise_magnitude
        cleaned_magnitude = np.maximum(cleaned_magnitude, beta * signal_magnitude)
        
        # Reconstruct complex spectrum
        cleaned_stft = cleaned_magnitude * np.exp(1j * signal_phase)
        
        # Inverse STFT
        _, cleaned_audio = signal.istft(cleaned_stft, fs=self.sample_rate, nperseg=nperseg)
        
        # Ensure output length matches input
        if len(cleaned_audio) > len(audio):
            cleaned_audio = cleaned_audio[:len(audio)]
        elif len(cleaned_audio) < len(audio):
            cleaned_audio = np.pad(cleaned_audio, (0, len(audio) - len(cleaned_audio)))
            
        return cleaned_audio
    
    def segment_audio(self, audio: np.ndarray, threshold: float = 0.02, 
                     min_silence_duration: float = 0.1, 
                     min_segment_duration: float = 0.1) -> List[np.ndarray]:
        """
        Segment audio into cry episodes based on energy threshold.
        
        Splits audio at silence periods (low energy regions) to isolate individual
        cry episodes. Silence is defined as regions where RMS energy falls below
        the threshold.
        
        Args:
            audio: Input audio signal as numpy array
            threshold: Energy threshold for silence detection (default: 0.02)
            min_silence_duration: Minimum silence duration in seconds to split (default: 0.1)
            min_segment_duration: Minimum segment duration in seconds to keep (default: 0.1)
            
        Returns:
            List of audio segments (each as numpy array)
            
        Validates: Requirements 2.2
        """
        if len(audio) == 0:
            return [audio]
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Calculate frame-wise energy using sliding window
        frame_length = int(0.025 * self.sample_rate)  # 25ms frames
        hop_length = int(0.010 * self.sample_rate)    # 10ms hop
        
        if frame_length < 1:
            frame_length = 1
        if hop_length < 1:
            hop_length = 1
            
        # Compute RMS energy for each frame
        energy = []
        for i in range(0, len(audio) - frame_length + 1, hop_length):
            frame = audio[i:i + frame_length]
            rms = np.sqrt(np.mean(frame ** 2))
            energy.append(rms)
        
        if len(energy) == 0:
            return [audio]
            
        energy = np.array(energy)
        
        # Identify silence frames (energy below threshold)
        is_silence = energy < threshold
        
        # Find silence regions
        min_silence_frames = int(min_silence_duration * self.sample_rate / hop_length)
        min_segment_frames = int(min_segment_duration * self.sample_rate / hop_length)
        
        # Find contiguous silence regions
        silence_regions = []
        in_silence = False
        silence_start = 0
        
        for i, silent in enumerate(is_silence):
            if silent and not in_silence:
                silence_start = i
                in_silence = True
            elif not silent and in_silence:
                silence_duration = i - silence_start
                if silence_duration >= min_silence_frames:
                    # Convert frame indices to sample indices
                    start_sample = silence_start * hop_length
                    end_sample = i * hop_length
                    silence_regions.append((start_sample, end_sample))
                in_silence = False
        
        # Handle case where audio ends in silence
        if in_silence:
            silence_duration = len(is_silence) - silence_start
            if silence_duration >= min_silence_frames:
                start_sample = silence_start * hop_length
                end_sample = len(audio)
                silence_regions.append((start_sample, end_sample))
        
        # If no silence regions found, return entire audio
        if len(silence_regions) == 0:
            return [audio]
        
        # Split audio at silence regions
        segments = []
        prev_end = 0
        
        for start, end in silence_regions:
            if start > prev_end:
                segment = audio[prev_end:start]
                # Only keep segments longer than minimum duration
                if len(segment) >= min_segment_frames * hop_length:
                    segments.append(segment)
            prev_end = end
        
        # Add final segment after last silence
        if prev_end < len(audio):
            segment = audio[prev_end:]
            if len(segment) >= min_segment_frames * hop_length:
                segments.append(segment)
        
        # If no valid segments found, return entire audio
        if len(segments) == 0:
            return [audio]
            
        return segments
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio amplitude to [-1, 1] range.
        
        Applies peak normalization to scale the audio signal so that the maximum
        absolute value is close to 1.0 (within 0.95-1.0 range).
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Normalized audio signal in [-1, 1] range
            
        Validates: Requirements 2.3
        """
        if len(audio) == 0:
            return audio
            
        # Handle invalid values
        if not np.all(np.isfinite(audio)):
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Find peak amplitude
        peak = np.max(np.abs(audio))
        
        # Avoid division by zero
        if peak < 1e-10:
            return audio
        
        # Normalize to [-1, 1] range with peak at ~0.95-1.0
        normalized = audio / peak
        
        # Apply slight scaling to ensure peak is in [0.95, 1.0] range
        # This prevents clipping while maximizing signal level
        target_peak = 0.98
        normalized = normalized * target_peak
        
        # Ensure values are within [-1, 1]
        normalized = np.clip(normalized, -1.0, 1.0)
        
        return normalized
    
    def preprocess(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply full preprocessing pipeline to audio signal.
        
        Chains all preprocessing operations:
        1. Noise reduction
        2. Normalization
        3. Segmentation (returns first segment if multiple)
        
        Note: For segmentation, this method returns only the first segment.
        Use segment_audio() directly if you need all segments.
        
        Args:
            audio: Input audio signal as numpy array
            
        Returns:
            Preprocessed audio signal
            
        Validates: Requirements 2.1, 2.2, 2.3, 2.5
        """
        if len(audio) == 0:
            return audio
        
        # Step 1: Noise reduction
        audio = self.reduce_noise(audio)
        
        # Step 2: Normalization
        audio = self.normalize_audio(audio)
        
        # Step 3: Segmentation (return first segment for simplicity)
        segments = self.segment_audio(audio)
        if len(segments) > 0:
            audio = segments[0]
        
        return audio
