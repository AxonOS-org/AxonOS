"""
Signal Processing Utilities for AxonOS
Basic EEG/EMG signal preprocessing and filtering
"""

import numpy as np
from typing import Tuple, Optional
from scipy import signal
from scipy.signal import butter, filtfilt


def butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """Create Butterworth bandpass filter"""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: float, order: int = 5) -> np.ndarray:
    """Apply bandpass filter to signal"""
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data, axis=-1)
    return y


def notch_filter(data: np.ndarray, freq: float, fs: float, Q: float = 35.0) -> np.ndarray:
    """Apply notch filter (e.g., for power line interference)"""
    b, a = signal.iirnotch(freq, Q, fs)
    y = signal.filtfilt(b, a, data, axis=-1)
    return y


def compute_psd(data: np.ndarray, fs: float, nperseg: int = 256) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Power Spectral Density using Welch's method"""
    f, psd = signal.welch(data, fs, nperseg=nperseg, axis=-1)
    return f, psd


def extract_band_power(psd: np.ndarray, freqs: np.ndarray, band: Tuple[float, float]) -> float:
    """Extract power in specific frequency band"""
    mask = (freqs >= band[0]) & (freqs <= band[1])
    return np.mean(psd[..., mask], axis=-1)


def preprocess_eeg(data: np.ndarray, fs: float, 
                   lowcut: float = 1.0, highcut: float = 50.0,
                   notch_freq: Optional[float] = 50.0) -> np.ndarray:
    """
    Standard EEG preprocessing pipeline
    
    Args:
        data: Input EEG data (channels x time)
        fs: Sampling frequency
        lowcut: Low frequency cutoff for bandpass
        highcut: High frequency cutoff for bandpass
        notch_freq: Notch filter frequency (None to skip)
    
    Returns:
        Preprocessed EEG data
    """
    # Apply notch filter if specified
    if notch_freq is not None:
        data = notch_filter(data, notch_freq, fs)
    
    # Apply bandpass filter
    data = bandpass_filter(data, lowcut, highcut, fs)
    
    # Remove DC offset
    data = data - np.mean(data, axis=-1, keepdims=True)
    
    return data


class SignalPreprocessor:
    """Configurable signal preprocessing pipeline"""
    
    def __init__(self, fs: float, 
                 bandpass: Tuple[float, float] = (1.0, 50.0),
                 notch_freq: Optional[float] = 50.0):
        self.fs = fs
        self.bandpass = bandpass
        self.notch_freq = notch_freq
    
    def process(self, data: np.ndarray) -> np.ndarray:
        """Process signal through pipeline"""
        return preprocess_eeg(data, self.fs, 
                            lowcut=self.bandpass[0], 
                            highcut=self.bandpass[1],
                            notch_freq=self.notch_freq)


# Common frequency bands
FREQUENCY_BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 50)
}