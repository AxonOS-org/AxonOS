"""
Signal Processing Module - EEG signal processing and preprocessing utilities
"""

from .processing import (
    butter_bandpass,
    bandpass_filter,
    notch_filter,
    compute_psd,
    extract_band_power,
    preprocess_eeg,
    SignalPreprocessor,
    FREQUENCY_BANDS
)

__all__ = [
    'butter_bandpass',
    'bandpass_filter',
    'notch_filter',
    'compute_psd',
    'extract_band_power',
    'preprocess_eeg',
    'SignalPreprocessor',
    'FREQUENCY_BANDS'
]