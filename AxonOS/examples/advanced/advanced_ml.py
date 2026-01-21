#!/usr/bin/env python3
"""
Advanced Machine Learning Example
Demonstrates ensemble models, custom preprocessing, and evaluation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from axonos.core.ml import ModelFactory, EnsembleModel, InferenceEngine, InferenceConfig
from axonos.core.ml.inference import SignalType, InferenceResult
from axonos.core.signal import SignalPreprocessor
from axonos.protocol.schemas import ClassificationResult
import numpy as np
import torch
from typing import List, Dict, Any


class AdvancedMLPipeline:
    """Advanced ML pipeline with ensemble models and custom evaluation"""
    
    def __init__(self):
        self.models: Dict[str, torch.nn.Module] = {}
        self.ensemble: EnsembleModel = None
        self.preprocessor = SignalPreprocessor(sampling_rate=250)
        self.config = InferenceConfig(
            signal_type=SignalType.MOTOR_IMAGERY,
            return_confidence=True,
            return_attention=True
        )
    
    def build_ensemble(self, input_size: int = 64, num_classes: int = 3) -> EnsembleModel:
        """Build ensemble of different model architectures"""
        print("🏗️ Building ensemble model...")
        
        # Create different models
        models = []
        weights = []
        
        # LSTM model
        lstm_model = ModelFactory.create_lstm_model(
            input_size=input_size,
            hidden_size=128,
            num_layers=2,
            num_classes=num_classes,
            dropout=0.3,
            bidirectional=True
        )
        models.append(lstm_model)
        weights.append(0.4)  # LSTM gets highest weight
        
        # Transformer model
        transformer_model = ModelFactory.create_transformer_model(
            input_size=input_size,
            d_model=128,
            nhead=8,
            num_layers=2,
            num_classes=num_classes,
            dropout=0.3
        )
        models.append(transformer_model)
        weights.append(0.35)
        
        # ConvNet model
        convnet_model = ModelFactory.create_convnet_model(
            input_size=input_size,
            num_classes=num_classes,
            dropout=0.3
        )
        models.append(convnet_model)
        weights.append(0.25)
        
        # Create ensemble
        self.ensemble = ModelFactory.create_ensemble(models, weights)
        print(f"   Ensemble created with {len(models)} models")
        
        return self.ensemble
    
    def custom_preprocessing(self, signal: np.ndarray) -> np.ndarray:
        """Custom preprocessing pipeline"""
        print("🔧 Applying custom preprocessing...")
        
        # Step 1: Bandpass filter
        filtered = self.preprocessor._apply_bandpass_filter(signal)
        
        # Step 2: Remove artifacts
        cleaned, artifact_mask = self.preprocessor.remove_artifacts(
            filtered, threshold=5.0
        )
        print(f"   Removed {np.sum(artifact_mask)} artifact samples")
        
        # Step 3: Normalize
        normalized = self.preprocessor._normalize(cleaned)
        
        # Step 4: Extract features
        features = self.preprocessor.extract_features(normalized)
        print(f"   Extracted {len(features)} features")
        
        return normalized
    
    def evaluate_model(self, model: torch.nn.Module, 
                      test_signals: List[np.ndarray], 
                      true_labels: List[int]) -> Dict[str, float]:
        """Comprehensive model evaluation"""
        print("📊 Evaluating model...")
        
        model.eval()
        predictions = []
        confidences = []
        processing_times = []
        
        with torch.no_grad():
            for i, (signal, true_label) in enumerate(zip(test_signals, true_labels)):
                start_time = torch.cuda.Event(enable_timing=True)
                end_time = torch.cuda.Event(enable_timing=True)
                
                # Prepare input
                signal_tensor = torch.from_numpy(signal).float().unsqueeze(0)
                
                # Forward pass
                start_time.record()
                logits, attention = model(signal_tensor)
                end_time.record()
                
                # Get results
                probabilities = torch.softmax(logits, dim=-1)
                prediction = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0, prediction].item()
                
                # Timing
                torch.cuda.synchronize()
                processing_time = start_time.elapsed_time(end_time)
                
                predictions.append(prediction)
                confidences.append(confidence)
                processing_times.append(processing_time)
                
                if i % 10 == 0:
                    print(f"   Processed {i}/{len(test_signals)} samples")
        
        # Calculate metrics
        accuracy = np.mean(np.array(predictions) == np.array(true_labels))
        avg_confidence = np.mean(confidences)
        avg_processing_time = np.mean(processing_times)
        
        results = {
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "avg_processing_time_ms": avg_processing_time,
            "min_confidence": np.min(confidences),
            "max_confidence": np.max(confidences),
            "total_samples": len(test_signals)
        }
        
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   Avg confidence: {avg_confidence:.3f}")
        print(f"   Avg processing time: {avg_processing_time:.2f}ms")
        
        return results
    
    def realtime_inference_loop(self, signal_stream):
        """Real-time inference loop with continuous processing"""
        print("🔄 Starting real-time inference loop...")
        print("   Press Ctrl+C to stop")
        
        engine = InferenceEngine(self.config, self.ensemble)
        
        try:
            for i, signal_chunk in enumerate(signal_stream):
                # Preprocess
                processed = self.custom_preprocessing(signal_chunk)
                
                # Inference
                result = engine.process(processed)
                
                if result:
                    print(f"\r[{i:04d}] Prediction: {result.prediction} "
                          f"(confidence: {result.confidence:.2f}) "
                          f"(latency: {result.processing_time_ms:.2f}ms)", 
                          end='', flush=True)
                
        except KeyboardInterrupt:
            print("\n\n✅ Real-time inference stopped by user")
        
        finally:
            stats = engine.get_stats()
            print(f"\n📊 Statistics:")
            print(f"   Total inferences: {stats['total_inferences']}")
            print(f"   Average latency: {stats.get('average_latency_ms', 0):.2f}ms")


def generate_synthetic_motor_imagery_data(
    num_trials: int = 100,
    samples_per_trial: int = 500,
    num_channels: int = 8
) -> tuple[List[np.ndarray], List[int]]:
    """Generate synthetic motor imagery data for testing"""
    print("🧠 Generating synthetic motor imagery data...")
    
    signals = []
    labels = []
    
    for i in range(num_trials):
        # Random class (0: left, 1: right, 2: rest)
        label = np.random.randint(0, 3)
        
        # Generate base signal
        signal = np.random.randn(samples_per_trial, num_channels) * 0.1
        
        # Add class-specific patterns
        if label == 0:  # Left hand imagery
            # Add mu rhythm (10 Hz) in right hemisphere channels
            t = np.linspace(0, 1, samples_per_trial)
            mu_rhythm = 0.5 * np.sin(2 * np.pi * 10 * t).reshape(-1, 1)
            signal[:, 4:6] += mu_rhythm  # Right hemisphere channels
            
        elif label == 1:  # Right hand imagery
            # Add mu rhythm (10 Hz) in left hemisphere channels
            t = np.linspace(0, 1, samples_per_trial)
            mu_rhythm = 0.5 * np.sin(2 * np.pi * 10 * t).reshape(-1, 1)
            signal[:, 1:3] += mu_rhythm  # Left hemisphere channels
        
        # Add some noise
        signal += 0.1 * np.random.randn(*signal.shape)
        
        signals.append(signal)
        labels.append(label)
    
    print(f"   Generated {len(signals)} trials")
    return signals, labels


def main():
    print("🚀 Advanced Machine Learning Example")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = AdvancedMLPipeline()
    
    # Build ensemble
    ensemble = pipeline.build_ensemble(input_size=8, num_classes=3)
    
    # Generate synthetic data
    signals, labels = generate_synthetic_motor_imagery_data(
        num_trials=50,
        samples_per_trial=500,
        num_channels=8
    )
    
    # Split data
    split_idx = int(0.8 * len(signals))
    train_signals, test_signals = signals[:split_idx], signals[split_idx:]
    train_labels, test_labels = labels[:split_idx], labels[split_idx:]
    
    print(f"\n📊 Dataset split:")
    print(f"   Training: {len(train_signals)} samples")
    print(f"   Testing: {len(test_signals)} samples")
    
    # Evaluate ensemble
    results = pipeline.evaluate_model(
        ensemble, 
        test_signals, 
        test_labels
    )
    
    print(f"\n🎯 Final Results:")
    for key, value in results.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Demo: single inference with attention visualization
    print(f"\n🔍 Attention visualization for sample 0:")
    sample_signal = test_signals[0]
    sample_tensor = torch.from_numpy(sample_signal).float().unsqueeze(0)
    
    with torch.no_grad():
        logits, attention_weights = ensemble(sample_tensor)
    
    print(f"   Attention shape: {attention_weights[0].shape}")
    print(f"   Attention mean: {attention_weights[0].mean():.3f}")
    
    print("\n✅ Advanced ML example completed!")
    print("\n🎓 Key takeaways:")
    print("   - Ensemble models improve robustness")
    print("   - Custom preprocessing enhances signal quality")
    print("   - Real-time inference is achievable")
    print("   - Attention mechanisms provide interpretability")


if __name__ == "__main__":
    import json
    import torch
    main()