#!/usr/bin/env python3
"""
Test script to verify AxonOS v2.1 package structure and imports
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing AxonOS v2.1 package imports...")
    
    try:
        # Test main package import
        import axonos
        print("✓ axonos package imported successfully")
        
        # Test core modules
        from axonos.core.ml import axonml_models
        print("✓ axonos.core.ml.axonml_models imported")
        
        from axonos.core.pipeline import axonml_inference
        print("✓ axonos.core.pipeline.axonml_inference imported")
        
        from axonos.core.signal import processing
        print("✓ axonos.core.signal.processing imported")
        
        # Test security modules
        from axonos.security import vault, encryption
        print("✓ axonos.security modules imported")
        
        # Test protocol and hardware
        from axonos.protocol import schemas
        print("✓ axonos.protocol.schemas imported")
        
        from axonos.hardware import interfaces
        print("✓ axonos.hardware.interfaces imported")
        
        from axonos.api import routes
        print("✓ axonos.api.routes imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_instantiation():
    """Test that models can be instantiated"""
    print("\nTesting model instantiation...")
    
    try:
        from axonos.core.ml.axonml_models import LSTMBCI, TransformerBCI, ModelConfig
        
        config = ModelConfig(input_size=64, hidden_size=128, num_classes=3)
        
        # Test LSTM model
        lstm_model = LSTMBCI(config)
        print("✓ LSTM model instantiated")
        
        # Test Transformer model
        transformer_model = TransformerBCI(config)
        print("✓ Transformer model instantiated")
        
        print("\n🎉 Model instantiation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Model instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_processing():
    """Test signal processing utilities"""
    print("\nTesting signal processing...")
    
    try:
        from axonos.core.signal.processing import preprocess_eeg, SignalPreprocessor
        import numpy as np
        
        # Create test data
        test_data = np.random.randn(8, 1000)  # 8 channels, 1000 samples
        fs = 250  # 250 Hz sampling rate
        
        # Test preprocessing
        preprocessed = preprocess_eeg(test_data, fs)
        print(f"✓ EEG preprocessing successful, output shape: {preprocessed.shape}")
        
        # Test preprocessor class
        preprocessor = SignalPreprocessor(fs)
        processed = preprocessor.process(test_data)
        print(f"✓ SignalPreprocessor successful, output shape: {processed.shape}")
        
        print("\n🎉 Signal processing tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Signal processing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_security_features():
    """Test security features"""
    print("\nTesting security features...")
    
    try:
        from axonos.security.vault import NeuralDataVault
        from axonos.security.encryption import encrypt_neural_data, decrypt_neural_data
        import numpy as np
        
        # Create test data
        test_data = np.random.randn(64).astype(np.float32)
        
        # Test encryption/decryption
        encrypted = encrypt_neural_data(test_data)
        decrypted = decrypt_neural_data(encrypted)
        
        # Verify decryption
        if np.allclose(test_data, decrypted, rtol=1e-5):
            print("✓ Encryption/decryption successful")
        else:
            print("❌ Encryption/decryption failed - data mismatch")
            return False
        
        # Test vault
        vault = NeuralDataVault()
        print("✓ NeuralDataVault instantiated")
        
        print("\n🎉 Security tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Security error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AxonOS v2.1 Package Structure Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Model Instantiation", test_model_instantiation),
        ("Signal Processing", test_signal_processing),
        ("Security Features", test_security_features),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 40}")
        print(f"Running: {test_name}")
        print('=' * 40)
        results.append(test_func())
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AxonOS v2.1 is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())