#!/usr/bin/env python3
"""
Advanced Encryption Module
Sophisticated encryption methods for neural data
"""

import os
import base64
import hashlib
import secrets
from typing import Tuple, Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AdvancedEncryption:
    """
    Advanced encryption methods for neural data
    Supports multiple encryption schemes and key management
    """
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.environ.get('AXONOS_MASTER_KEY', '')
        if not self.master_key:
            raise ValueError("Master key is required for encryption")
        
        # Derive base key
        self.base_key = self._derive_key(self.master_key, b'axonos_base_salt')
    
    def _derive_key(self, password: str, salt: bytes, iterations: int = 200000) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def encrypt_aes_256_cbc(self, plaintext: bytes, iv: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypt with AES-256-CBC
        
        Args:
            plaintext: Data to encrypt
            iv: Initialization vector (generated if None)
            
        Returns:
            Tuple of (encrypted_data, iv)
        """
        if iv is None:
            iv = os.urandom(16)
        
        cipher = Cipher(
            algorithms.AES(self.base_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad plaintext to block size
        pad_length = 16 - (len(plaintext) % 16)
        padded_plaintext = plaintext + bytes([pad_length] * pad_length)
        
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return ciphertext, iv
    
    def decrypt_aes_256_cbc(self, ciphertext: bytes, iv: bytes) -> bytes:
        """
        Decrypt with AES-256-CBC
        
        Args:
            ciphertext: Encrypted data
            iv: Initialization vector
            
        Returns:
            Decrypted plaintext
        """
        cipher = Cipher(
            algorithms.AES(self.base_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        pad_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-pad_length]
        
        return plaintext
    
    def encrypt_fernet(self, plaintext: bytes) -> bytes:
        """Encrypt with Fernet (AES-128-CBC with HMAC)"""
        key = base64.urlsafe_b64encode(self.base_key[:32])
        f = Fernet(key)
        return f.encrypt(plaintext)
    
    def decrypt_fernet(self, ciphertext: bytes) -> bytes:
        """Decrypt with Fernet"""
        key = base64.urlsafe_b64encode(self.base_key[:32])
        f = Fernet(key)
        return f.decrypt(ciphertext)
    
    def generate_key_pair(self) -> Tuple[str, str]:
        """Generate public/private key pair"""
        private_key = secrets.token_urlsafe(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        return private_key, public_key
    
    def sign_data(self, data: bytes, private_key: str) -> str:
        """Sign data with private key"""
        signature = hashlib.sha256(data + private_key.encode()).hexdigest()
        return signature
    
    def verify_signature(self, data: bytes, signature: str, public_key: str) -> bool:
        """Verify data signature"""
        expected = hashlib.sha256(data + public_key.encode()).hexdigest()
        return signature == expected
    
    def create_secure_session(self) -> Dict[str, Any]:
        """Create secure session parameters"""
        session_key = secrets.token_urlsafe(32)
        session_iv = os.urandom(16)
        
        return {
            "session_key": session_key,
            "session_iv": base64.b64encode(session_iv).decode(),
            "created_at": os.urandom(8).hex(),  # Random timestamp
        }