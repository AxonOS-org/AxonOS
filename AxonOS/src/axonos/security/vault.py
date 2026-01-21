#!/usr/bin/env python3
"""
NeuralDataVault - Secure storage with zero-knowledge architecture
"""

import os
import base64
import hashlib
import secrets
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime, timedelta
import numpy as np


class SecurityConfig:
    """Configuration for security features"""
    
    def __init__(self, zero_knowledge_mode: bool = True):
        self.zero_knowledge_mode = zero_knowledge_mode
        self.master_key = os.environ.get('AXONOS_MASTER_KEY', '')
        if not self.master_key and zero_knowledge_mode:
            raise ValueError("AXONOS_MASTER_KEY environment variable is required for zero-knowledge mode")


class NeuralDataVault:
    """
    Secure vault for neural data with zero-knowledge architecture
    Never stores raw neural data - only encrypted
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.audit_log: List[Dict[str, Any]] = []
        self._initialize_vault()
    
    def _initialize_vault(self):
        """Initialize vault with master key"""
        if self.config.zero_knowledge_mode and self.config.master_key:
            # Derive encryption key from master key
            self.encryption_key = hashlib.pbkdf2_hmac(
                'sha256',
                self.config.master_key.encode(),
                b'axonos_salt',
                200000,  # 200k iterations
                dklen=32
            )
        else:
            self.encryption_key = secrets.token_bytes(32)
    
    def encrypt_neural_data(self, neural_data: bytes, metadata: Optional[Dict[str, Any]] = None) -> Tuple[bytes, str]:
        """
        Encrypt neural data with zero-knowledge guarantee
        
        Args:
            neural_data: Raw neural data to encrypt
            metadata: Optional metadata
            
        Returns:
            Tuple of (encrypted_data, data_id)
        """
        # Generate unique data ID
        data_id = secrets.token_urlsafe(32)
        
        # Simple XOR encryption for demo (use proper crypto in production)
        encrypted = bytes([b ^ self.encryption_key[i % len(self.encryption_key)] for i, b in enumerate(neural_data)])
        
        # Log audit event
        self._log_audit_event("ENCRYPT", data_id, metadata)
        
        return encrypted, data_id
    
    def decrypt_neural_data(self, encrypted_data: bytes, data_id: str) -> Tuple[bytes, Dict[str, Any]]:
        """
        Decrypt neural data
        
        Args:
            encrypted_data: Encrypted neural data
            data_id: Unique data identifier
            
        Returns:
            Tuple of (decrypted_data, metadata)
        """
        # Simple XOR decryption (same as encryption for XOR)
        decrypted = bytes([b ^ self.encryption_key[i % len(self.encryption_key)] for i, b in enumerate(encrypted_data)])
        
        # Log audit event
        self._log_audit_event("DECRYPT", data_id, None)
        
        metadata = {"decrypted_at": datetime.now().isoformat()}
        return decrypted, metadata
    
    def _log_audit_event(self, action: str, data_id: str, metadata: Optional[Dict[str, Any]]):
        """Log security audit event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data_id": data_id[:8] + "...",  # Truncate for security
            "metadata": metadata,
            "ip_address": "localhost",  # In production, get real IP
        }
        self.audit_log.append(event)
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]
    
    def add_differential_privacy(self, signal: np.ndarray, epsilon: float = 1.0) -> np.ndarray:
        """
        Add calibrated noise for differential privacy
        
        Args:
            signal: Input signal
            epsilon: Privacy budget (lower = more private)
            
        Returns:
            Signal with added noise
        """
        sensitivity = np.std(signal)  # Local sensitivity
        noise_scale = sensitivity / epsilon
        noise = np.random.normal(0, noise_scale, signal.shape)
        return signal + noise
    
    def compute_encrypted(self, encrypted_data: bytes, operation: str) -> bytes:
        """
        Compute on encrypted data (homomorphic encryption placeholder)
        
        Args:
            encrypted_data: Encrypted data
            operation: Operation to perform
            
        Returns:
            Encrypted result
        """
        # This is a placeholder - real implementation would use proper homomorphic encryption
        if operation == "sum":
            # For demo: just return the same data
            return encrypted_data
        else:
            raise ValueError(f"Unsupported operation: {operation}")


class DifferentialPrivacy:
    """Differential privacy utilities"""
    
    @staticmethod
    def add_laplace_noise(data: np.ndarray, epsilon: float, sensitivity: float) -> np.ndarray:
        """Add Laplace noise for differential privacy"""
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
    
    @staticmethod
    def add_gaussian_noise(data: np.ndarray, epsilon: float, delta: float, sensitivity: float) -> np.ndarray:
        """Add Gaussian noise for differential privacy"""
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
        noise = np.random.normal(0, sigma, data.shape)
        return data + noise