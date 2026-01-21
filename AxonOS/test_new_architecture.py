#!/usr/bin/env python3
"""
Test AxonOS v2.1 Architecture
Comprehensive test suite for the modular architecture
"""

import sys
import os
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test imports
try:
    from axonos.protocol.schemas import (
        NeuralPacket, DeviceInfo, SignalData, SecurityMetadata,
        ClassificationResult, EventBatch, CalibrationData
    )
    from axonos.protocol.events import EventType, NeuralEvent, EventFactory
    from axonos.core.ml import ModelFactory, ModelConfig
    from axonos.core.ml.models import LSTMDecoder, TransformerDecoder, ConvNetDecoder
    from axonos.core.ml.inference import (
        InferenceEngine, InferenceConfig, SignalType, InferenceMode,
        SignalPreprocessor, BatchProcessor, RealtimeProcessor
    )
    from axonos.core.signal import SignalPreprocessor as SigPreprocessor
    from axonos.security.vault import NeuralDataVault, SecurityConfig
    from axonos.security.encryption import AdvancedEncryption
    from axonos.security.identity import IdentityManager
    import torch
    import numpy as np
    
    IMPORTS_SUCCESS = True
except Exception as e:
    print(f"❌ Import error: {e}")
    IMPORTS_SUCCESS = False


class TestResult:
    """Test result with status and message"""
    def __init__(self, name: str, success: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.success = success
        self.message = message
        self.duration = duration


def run_test(name: str, test_func):
    """Run a test and return result"""
    start_time = time.time()
    try:
        test_func()
        duration = time.time() - start_time
        return TestResult(name, True, f"✅ Passed in {duration:.2f}s", duration)
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(name, False, f"❌ Failed: {e}", duration)


def test_protocol_schemas():
    """Test protocol schemas and data validation"""
    print("\n🔬 Testing Protocol Schemas...")
    
    # Create device info
    device_info = DeviceInfo(
        device_id="test_device_001",
        device_type="OpenBCI",
        model="Cyton",
        firmware_version="1.0.0",
        num_channels=8,
        sampling_rate=250
    )
    
    # Create signal data
    signal_data = SignalData(
        data=[0.1, 0.2, 0.3] * 100,
        channels=["C3", "C4", "Cz"],
        sampling_rate=250,
        duration_seconds=1.2,
        quality="good"
    )
    
    # Create security metadata
    security_meta = SecurityMetadata(
        security_level="confidential",
        encrypted=True,
        subject_id="test_subject"
    )
    
    # Create neural packet
    packet = NeuralPacket(
        packet_id="test_packet_001_123456789",
        device_info=device_info,
        signal_data=signal_data,
        security_metadata=security_meta
    )
    
    # Validate
    assert packet.packet_id == "test_packet_001_123456789"
    assert packet.device_info.device_type == "OpenBCI"
    assert len(packet.signal_data.data) == 300
    assert packet.security_metadata.security_level == "confidential"
    
    print("   ✅ Protocol schemas working correctly")


def test_ml_models():
    """Test machine learning models"""
    print("\n🤖 Testing ML Models...")
    
    # Create model factory
    factory = ModelFactory()
    
    # Test LSTM model
    lstm_model = factory.create_lstm_model(
        input_size=8,
        hidden_size=64,
        num_classes=3
    )
    
    # Test forward pass
    test_input = torch.randn(1, 100, 8)  # (batch, time, features)
    with torch.no_grad():
        logits, attention = lstm_model(test_input)
    
    assert logits.shape == (1, 3)  # (batch, num_classes)
    assert attention.shape == (1, 100)  # (batch, time)
    
    # Test Transformer model
    transformer_model = factory.create_transformer_model(
        input_size=8,
        d_model=64,
        num_classes=3
    )
    
    with torch.no_grad():
        logits, _ = transformer_model(test_input)
    
    assert logits.shape == (1, 3)
    
    print("   ✅ ML models working correctly")


def test_security_features():
    """Test security features"""
    print("\n🔒 Testing Security Features...")
    
    # Set up environment
    os.environ['AXONOS_MASTER_KEY'] = 'test_key_123'
    
    # Create vault
    vault = NeuralDataVault(config=SecurityConfig(zero_knowledge_mode=True))
    
    # Test encryption
    test_data = b"sensitive_neural_data"
    encrypted, data_id = vault.encrypt_neural_data(test_data)
    
    # Test decryption
    decrypted, metadata = vault.decrypt_neural_data(encrypted, data_id)
    assert decrypted == test_data, "Decryption failed!"
    
    print("   ✅ Security features working correctly")


def test_inference_engine():
    """Test inference engine"""
    print("\n⚡ Testing Inference Engine...")
    
    # Create config
    config = InferenceConfig(
        signal_type=SignalType.MOTOR_IMAGERY,
        return_confidence=True
    )
    
    # Create model
    factory = ModelFactory()
    model = factory.create_lstm_model(input_size=8, num_classes=3)
    
    # Create engine
    engine = InferenceEngine(config, model)
    
    # Test signal
    signal = np.random.randn(250, 8).astype(np.float32)  # 1 second, 8 channels
    
    # Process signal
    result = engine.process(signal)
    
    assert result is not None
    assert 0 <= result.prediction <= 2
    assert 0 <= result.confidence <= 1
    
    print("   ✅ Inference engine working correctly")


def test_signal_preprocessing():
    """Test signal preprocessing"""
    print("\n📡 Testing Signal Preprocessing...")
    
    preprocessor = SigPreprocessor(sampling_rate=250)
    
    # Generate test signal
    signal = np.random.randn(1000, 8)  # 4 seconds, 8 channels
    
    # Preprocess
    processed = preprocessor.preprocess(signal)
    
    assert processed.shape == signal.shape
    
    # Test quality assessment
    quality = preprocessor.estimate_quality(processed)
    assert 0 <= quality <= 1
    
    print("   ✅ Signal preprocessing working correctly")


def test_events():
    """Test event system"""
    print("\n📡 Testing Event System...")
    
    # Create event factory
    factory = EventFactory()
    
    # Create motor imagery event
    event = factory.create_motor_imagery_event(
        laterality="left",
        body_part="hand",
        device_id="test_device",
        confidence=0.95,
        processing_time_ms=10.5
    )
    
    assert event.event_type == EventType.LEFT_HAND_IMAGERY
    assert event.laterality == "left"
    assert event.body_part == "hand"
    
    print("   ✅ Event system working correctly")


def main():
    """Run all tests"""
    print("🧠 Testing AxonOS v2.1 Architecture")
    print("=" * 60)
    
    if not IMPORTS_SUCCESS:
        print("❌ Import failed, cannot run tests")
        return False
    
    # Set up environment
    os.environ['AXONOS_MASTER_KEY'] = 'test_key_for_testing_only'
    
    # Run tests
    tests = [
        ("Protocol Schemas", test_protocol_schemas),
        ("ML Models", test_ml_models),
        ("Security Features", test_security_features),
        ("Inference Engine", test_inference_engine),
        ("Signal Preprocessing", test_signal_preprocessing),
        ("Events", test_events),
    ]
    
    results = []
    total_duration = 0.0
    
    for test_name, test_func in tests:
        result = run_test(test_name, test_func)
        results.append(result)
        total_duration += result.duration
        print(f"   {result.message}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.success)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Total duration: {total_duration:.2f}s")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("✅ AxonOS v2.1 architecture is working correctly!")
        print("🚀 Ready for production deployment!")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)