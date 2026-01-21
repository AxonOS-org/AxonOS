#!/usr/bin/env python3
"""
Basic AxonOS Usage Example
Demonstrates fundamental features of the platform
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from axonos.protocol.schemas import NeuralPacket, DeviceInfo, SignalData, SecurityMetadata
from axonos.core.ml import ModelFactory
from axonos.core.signal import SignalPreprocessor
from axonos.security.vault import NeuralDataVault, SecurityConfig
import numpy as np


def main():
    print("🧠 Basic AxonOS Usage Example")
    print("=" * 50)
    
    # 1. Create device information
    print("\n1. Creating device information...")
    device_info = DeviceInfo(
        device_id="openbci_cyton_001",
        device_type="OpenBCI",
        model="Cyton",
        firmware_version="1.0.0",
        num_channels=8,
        sampling_rate=250
    )
    print(f"   Device: {device_info.device_type} {device_info.model}")
    
    # 2. Generate sample signal data
    print("\n2. Generating sample signal data...")
    # Simulated 1 second of EEG data (8 channels, 250 Hz)
    duration_seconds = 1.0
    num_samples = int(device_info.sampling_rate * duration_seconds)
    
    # Generate synthetic EEG-like signal
    t = np.linspace(0, duration_seconds, num_samples)
    signal_data = []
    
    for ch in range(device_info.num_channels):
        # Add some alpha rhythm (10 Hz)
        alpha = 0.5 * np.sin(2 * np.pi * 10 * t)
        # Add some noise
        noise = 0.1 * np.random.randn(num_samples)
        channel_data = alpha + noise
        signal_data.extend(channel_data.tolist())
    
    signal = SignalData(
        data=signal_data,
        channels=[f"Ch{i+1}" for i in range(device_info.num_channels)],
        sampling_rate=device_info.sampling_rate,
        duration_seconds=duration_seconds,
        quality="good"
    )
    print(f"   Generated {len(signal.data)} samples from {len(signal.channels)} channels")
    
    # 3. Apply security
    print("\n3. Applying security...")
    import os
    os.environ['AXONOS_MASTER_KEY'] = 'demo_key_123'
    
    vault = NeuralDataVault(config=SecurityConfig(zero_knowledge_mode=True))
    
    # Encrypt signal data
    encrypted_signal, signal_id = vault.encrypt_neural_data(
        json.dumps(signal.dict()).encode(),
        metadata={"subject": "demo_subject", "session": 1}
    )
    print(f"   Signal encrypted! ID: {signal_id[:8]}...")
    
    # 4. Create security metadata
    print("\n4. Creating security metadata...")
    security_meta = SecurityMetadata(
        security_level="confidential",
        encrypted=True,
        subject_id="demo_subject_hash",
        session_id="session_001"
    )
    print(f"   Security level: {security_meta.security_level}")
    
    # 5. Create neural packet
    print("\n5. Creating neural packet...")
    packet = NeuralPacket(
        packet_id="demo_packet_123456789",
        device_info=device_info,
        signal_data=signal,
        security_metadata=security_meta
    )
    print(f"   Packet created: {packet.packet_id}")
    print(f"   Timestamp: {packet.created_at}")
    
    # 6. Process with ML model
    print("\n6. Processing with ML model...")
    factory = ModelFactory()
    model = factory.create_lstm_model(
        input_size=device_info.num_channels,
        hidden_size=128,
        num_classes=3
    )
    
    # Prepare input (batch_size=1, seq_len, features)
    signal_array = np.array(signal.data).reshape(-1, device_info.num_channels)
    signal_tensor = torch.from_numpy(signal_array).float().unsqueeze(0)
    
    # Forward pass
    with torch.no_grad():
        logits, attention = model(signal_tensor)
        probabilities = torch.softmax(logits, dim=-1)
        prediction = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0, prediction].item()
    
    print(f"   Prediction: {prediction} (confidence: {confidence:.2f})")
    
    # 7. Signal preprocessing
    print("\n7. Applying signal preprocessing...")
    preprocessor = SignalPreprocessor(
        sampling_rate=device_info.sampling_rate,
        bandpass_low=8.0,
        bandpass_high=30.0
    )
    
    processed_signal = preprocessor.preprocess(signal_array)
    quality = preprocessor.estimate_quality(processed_signal)
    
    print(f"   Signal quality: {quality:.2f}")
    print(f"   Processed shape: {processed_signal.shape}")
    
    print("\n✅ Basic example completed successfully!")
    print("\n📚 Next steps:")
    print("  - Check examples/advanced/ for more complex usage")
    print("  - Read docs/guides/ for detailed documentation")
    print("  - Start building your own modules!")


if __name__ == "__main__":
    import json
    import torch
    main()