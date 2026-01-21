"""
AxonOS - Secure Privacy-First BCI Protocol

A modular, production-ready platform for neurointerfaces with security-first design.
"""

__version__ = "0.1.0"
__author__ = "AxonOS Team"
__email__ = "team@axonos.org"

# Core imports
from .core.ml import ModelFactory, InferenceEngine
from .core.signal import SignalPreprocessor
from .security.vault import NeuralDataVault, SecurityConfig
from .protocol.schemas import NeuralPacket, DeviceInfo, SignalData

__all__ = [
    "ModelFactory",
    "InferenceEngine", 
    "SignalPreprocessor",
    "NeuralDataVault",
    "SecurityConfig",
    "NeuralPacket",
    "DeviceInfo",
    "SignalData",
]