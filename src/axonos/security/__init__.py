"""
Security Module - Security layer with zero-knowledge design
"""

from .vault import NeuralDataVault, SecurityConfig
from .encryption import AdvancedEncryption
from .identity import IdentityManager

__all__ = [
    "NeuralDataVault",
    "SecurityConfig",
    "AdvancedEncryption",
    "IdentityManager",
]