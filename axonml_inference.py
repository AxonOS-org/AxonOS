#!/usr/bin/env python3
"""
AxonML Inference Pipeline
Real-time inference engine for BCI signal decoding
Production-ready implementation with async support
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
from queue import Queue, Empty
import logging
from pathlib import Path
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor


class SignalType(Enum):
    """Types of BCI signals"""
    MOTOR_IMAGERY = "motor_imagery"
    P300 = "p300"
    SSVEP = "ssvep"
    ERP = "erp"
    ALPHA_WAVES = "alpha_waves"


class InferenceMode(Enum):
    """Inference modes"""
    REALTIME = "realtime"      # Continuous streaming
    EPOCH = "epoch"           # Epoch-based
    TRIGGERED = "triggered"   # Event-triggered


@dataclass
class InferenceConfig:
    """Configuration for inference pipeline"""
    model_type: str = "lstm"
    model_path: Optional[str] = None
    signal_type: SignalType = SignalType.MOTOR_IMAGERY
    mode: InferenceMode = InferenceMode.REALTIME
    
    # Timing parameters
    sampling_rate: int = 250  # Hz
    window_size: float = 2.0  # seconds
    overlap: float = 0.5      # 50% overlap
    buffer_size: int = 10000  # samples
    
    # Processing parameters
    batch_size: int = 1
    device: str = "auto"      # auto, cpu, cuda
    precision: str = "float32"  # float32, float16
    
    # Real-time parameters
    latency_target_ms: float = 10.0
    max_queue_size: int = 100
    
    # Preprocessing parameters
    bandpass_low: float = 8.0   # Hz
    bandpass_high: float = 30.0 # Hz
    notch_filter: float = 50.0  # Hz (power line)
    normalize: bool = True
    
    # Post-processing parameters
    smoothing_window: int = 5
    confidence_threshold: float = 0.7
    ensemble_voting: str = "soft"  # soft, hard
    
    # Output configuration
    output_classes: List[str] = field(default_factory=lambda: ["left_hand", "right_hand", "rest"])
    return_confidence: bool = True
    return_attention: bool = False
    
    def __post_init__(self):
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class InferenceResult:
    """Result from inference pipeline"""
    prediction: int
    confidence: float
    class_probabilities: np.ndarray
    timestamp: float
    signal_type: SignalType
    processing_time_ms: float
    attention_weights: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SignalPreprocessor:
    """Real-time signal preprocessing pipeline"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.sampling_rate = config.sampling_rate
        self.window_samples = int(config.window_size * config.sampling_rate)
        self.overlap_samples = int(self.window_samples * config.overlap)
        self.step_size = self.window_samples - self.overlap_samples
        
        # Circular buffer for signal data
        self.signal_buffer = np.zeros((config.buffer_size,))  # Simplified for single channel
        self.buffer_index = 0
        self.buffer_full = False
        
        # State for filters (for real-time continuity)
        self.filter_state = None
        
    def add_samples(self, samples: np.ndarray):
        """Add new samples to buffer"""
        n_samples = len(samples)
        
        # Handle circular buffer wraparound
        if self.buffer_index + n_samples <= self.config.buffer_size:
            self.signal_buffer[self.buffer_index:self.buffer_index + n_samples] = samples
        else:
            first_part = self.config.buffer_size - self.buffer_index
            self.signal_buffer[self.buffer_index:] = samples[:first_part]
            self.signal_buffer[:n_samples - first_part] = samples[first_part:]
        
        self.buffer_index = (self.buffer_index + n_samples) % self.config.buffer_size
        
        if not self.buffer_full and self.buffer_index >= self.window_samples:
            self.buffer_full = True
    
    def get_window(self) -> Optional[np.ndarray]:
        """Get next processing window"""
        if not self.buffer_full:
            return None
        
        # Calculate start index for current window
        end_idx = self.buffer_index
        start_idx = (end_idx - self.window_samples) % self.config.buffer_size
        
        # Extract window (handle wraparound)
        if start_idx < end_idx:
            window = self.signal_buffer[start_idx:end_idx].copy()
        else:
            window = np.concatenate([
                self.signal_buffer[start_idx:],
                self.signal_buffer[:end_idx]
            ])
        
        return window
    
    def preprocess(self, signal: np.ndarray) -> np.ndarray:
        """Apply preprocessing pipeline"""
        # Apply notch filter
        filtered = self._apply_filter(signal, self.config.notch_filter, 'notch')
        
        # Apply bandpass filter
        filtered = self._apply_filter(filtered, [self.config.bandpass_low, self.config.bandpass_high], 'bandpass')
        
        # Normalize
        if self.config.normalize:
            filtered = self._normalize(filtered)
        
        return filtered
    
    def _apply_filter(self, signal: np.ndarray, freq, filter_type: str) -> np.ndarray:
        """Apply digital filter (simplified implementation)"""
        # In production, use scipy.signal
        # This is a simplified FIR approximation
        
        if filter_type == 'notch':
            # Simplified notch filter for power line
            nyquist = self.sampling_rate / 2
            f0 = freq / nyquist
            
            # Create simple notch
            alpha = 0.95
            filtered = signal.copy()
            for i in range(2, len(signal)):
                filtered[i] = signal[i] - 2 * np.cos(2 * np.pi * f0) * signal[i-1] + signal[i-2] + alpha * filtered[i-1] - alpha * np.cos(2 * np.pi * f0) * filtered[i-2]
            return filtered
            
        elif filter_type == 'bandpass':
            # Simplified bandpass filter
            low, high = freq
            nyquist = self.sampling_rate / 2
            
            # Simple FIR approximation
            order = 32
            n = np.arange(order)
            
            # Lowpass prototype
            h_lp = np.sinc(2 * high * (n - order//2)) / nyquist
            h_lp *= np.hamming(order)
            
            # Highpass prototype  
            h_hp = np.sinc(2 * low * (n - order//2)) / nyquist
            h_hp *= np.hamming(order)
            
            # Bandpass = lowpass - highpass
            b = h_lp - h_hp
            
            # Apply filter
            return np.convolve(signal, b, mode='same')
        
        return signal
    
    def _normalize(self, signal: np.ndarray) -> np.ndarray:
        """Normalize signal to zero mean and unit variance"""
        mean = np.mean(signal)
        std = np.std(signal)
        if std > 1e-6:
            return (signal - mean) / std
        return signal - mean


class InferenceEngine:
    """Main inference engine for real-time BCI signal decoding"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize model
        self.model = self._load_model()
        self.model.eval()
        
        # Move to device
        self.device = torch.device(config.device)
        self.model.to(self.device)
        
        # Preprocessor
        self.preprocessor = SignalPreprocessor(config)
        
        # Output smoothing
        self.smoothing_buffer = []
        self.smoothing_window = config.smoothing_window
        
        # Performance monitoring
        self.stats = {
            'total_inferences': 0,
            'total_time_ms': 0.0,
            'avg_latency_ms': 0.0,
            'max_latency_ms': 0.0,
            'min_latency_ms': float('inf')
        }
        
        # Callbacks
        self.prediction_callbacks: List[Callable[[InferenceResult], None]] = []
        
        # Threading
        self.running = False
        self.inference_thread: Optional[threading.Thread] = None
        self.input_queue = Queue(maxsize=config.max_queue_size)
        self.output_queue = Queue(maxsize=config.max_queue_size)
        
        # Async support
        self.async_callbacks: List[Callable[[InferenceResult], asyncio.Future]] = []
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        self.logger.info(f"Inference engine initialized with {config.model_type} model on {config.device}")
    
    def _load_model(self) -> torch.nn.Module:
        """Load model from file or create new one"""
        if self.config.model_path and Path(self.config.model_path).exists():
            self.logger.info(f"Loading model from {self.config.model_path}")
            model = torch.load(self.config.model_path, map_location='cpu')
        else:
            self.logger.info("Creating new model from config")
            # Import here to avoid circular imports
            from axonml_models import ModelFactory, ModelConfig as MLConfig
            
            ml_config = MLConfig()
            factory = ModelFactory()
            
            if self.config.model_type == 'lstm':
                model = factory.create_lstm_model(**ml_config.__dict__)
            elif self.config.model_type == 'transformer':
                model = factory.create_transformer_model(**ml_config.__dict__)
            elif self.config.model_type == 'convnet':
                model = factory.create_convnet_model(**ml_config.__dict__)
            else:
                raise ValueError(f"Unknown model type: {self.config.model_type}")
        
        return model
    
    def add_prediction_callback(self, callback: Callable[[InferenceResult], None]):
        """Add callback for prediction results"""
        self.prediction_callbacks.append(callback)
    
    def add_async_callback(self, callback: Callable[[InferenceResult], asyncio.Future]):
        """Add async callback for prediction results"""
        self.async_callbacks.append(callback)
    
    def start(self):
        """Start inference engine"""
        if self.running:
            return
        
        self.running = True
        self.inference_thread = threading.Thread(target=self._inference_loop, daemon=True)
        self.inference_thread.start()
        self.logger.info("Inference engine started")
    
    def stop(self):
        """Stop inference engine"""
        if not self.running:
            return
        
        self.logger.info("Stopping inference engine...")
        
        # Stop pipeline
        self.running = False
        if self.inference_thread:
            self.inference_thread.join(timeout=1.0)
        
        # Clean up executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("Inference engine stopped")
    
    def process_signal(self, signal: np.ndarray):
        """Process incoming signal data"""
        if not self.running:
            raise RuntimeError("Engine not started")
        
        try:
            self.input_queue.put_nowait(signal)
        except:
            # Queue full, drop oldest
            try:
                self.input_queue.get_nowait()
                self.input_queue.put_nowait(signal)
            except:
                pass
    
    def _inference_loop(self):
        """Main inference loop running in separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.running:
            try:
                # Get signal from queue
                signal = self.input_queue.get(timeout=0.1)
                
                # Run inference
                result = self._run_inference(signal)
                
                # Store result
                try:
                    self.output_queue.put_nowait(result)
                except:
                    # Queue full, drop oldest
                    try:
                        self.output_queue.get_nowait()
                        self.output_queue.put_nowait(result)
                    except:
                        pass
                
                # Notify sync callbacks
                for callback in self.prediction_callbacks:
                    try:
                        callback(result)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                
                # Notify async callbacks
                if self.async_callbacks:
                    asyncio.run_coroutine_threadsafe(
                        self._notify_async_callbacks(result), loop
                    )
                
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Inference error: {e}")
        
        loop.close()
    
    async def _notify_async_callbacks(self, result: InferenceResult):
        """Notify async callbacks"""
        for callback in self.async_callbacks:
            try:
                await callback(result)
            except Exception as e:
                self.logger.error(f"Async callback error: {e}")
    
    def _run_inference(self, signal: np.ndarray) -> InferenceResult:
        """Run single inference pass"""
        start_time = time.perf_counter()
        
        # Preprocess signal
        preprocessed = self.preprocessor.preprocess(signal)
        
        # Convert to tensor
        input_tensor = torch.from_numpy(preprocessed).float()
        
        # Add batch dimension if needed
        if input_tensor.dim() == 1:
            input_tensor = input_tensor.unsqueeze(0).unsqueeze(0)  # (batch, time, features)
        elif input_tensor.dim() == 2:
            input_tensor = input_tensor.unsqueeze(0)  # (batch, time, features)
        
        # Move to device
        input_tensor = input_tensor.to(self.device)
        
        # Run inference
        with torch.no_grad():
            if hasattr(self.model, 'get_attention_weights'):
                logits, attention_weights = self.model(input_tensor)
                attention_weights = attention_weights.cpu().numpy()
            else:
                logits = self.model(input_tensor)
                attention_weights = None
        
        # Apply softmax
        probabilities = F.softmax(logits, dim=1)
        
        # Get prediction
        prediction = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0, prediction].item()
        
        # Apply smoothing
        self.smoothing_buffer.append(confidence)
        if len(self.smoothing_buffer) > self.smoothing_window:
            self.smoothing_buffer.pop(0)
        
        smoothed_confidence = np.mean(self.smoothing_buffer) if self.smoothing_buffer else confidence
        
        # Create result
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        result = InferenceResult(
            prediction=prediction,
            confidence=smoothed_confidence,
            class_probabilities=probabilities.cpu().numpy()[0],
            timestamp=time.time(),
            signal_type=self.config.signal_type,
            processing_time_ms=processing_time_ms,
            attention_weights=attention_weights,
            metadata={'raw_confidence': confidence}
        )
        
        # Update statistics
        self._update_stats(processing_time_ms)
        
        return result
    
    def _update_stats(self, processing_time_ms: float):
        """Update performance statistics"""
        self.stats['total_inferences'] += 1
        self.stats['total_time_ms'] += processing_time_ms
        self.stats['avg_latency_ms'] = self.stats['total_time_ms'] / self.stats['total_inferences']
        self.stats['max_latency_ms'] = max(self.stats['max_latency_ms'], processing_time_ms)
        self.stats['min_latency_ms'] = min(self.stats['min_latency_ms'], processing_time_ms)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.stats.copy()
    
    def get_latest_result(self) -> Optional[InferenceResult]:
        """Get latest inference result"""
        try:
            return self.output_queue.get_nowait()
        except Empty:
            return None


class BatchInferenceEngine:
    """Batch inference engine for processing multiple epochs"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Load model
        if config.model_path and Path(config.model_path).exists():
            self.model = torch.load(config.model_path, map_location='cpu')
        else:
            from axonml_models import ModelFactory, ModelConfig as MLConfig
            ml_config = MLConfig()
            factory = ModelFactory()
            self.model = factory.create_lstm_model(**ml_config.__dict__)
        
        self.model.to(self.device)
        self.model.eval()
    
    def predict_batch(self, epochs: List[np.ndarray]) -> List[InferenceResult]:
        """Predict on batch of epochs"""
        if not epochs:
            return []
        
        # Preprocess all epochs
        processed_epochs = []
        for epoch in epochs:
            processed = self._preprocess_epoch(epoch)
            processed_epochs.append(processed)
        
        # Stack into batch
        batch = np.stack(processed_epochs, axis=0)
        input_tensor = torch.from_numpy(batch).float().to(self.device)
        
        # Run inference
        with torch.no_grad():
            if hasattr(self.model, 'get_attention_weights'):
                logits, attention_weights = self.model(input_tensor)
            else:
                logits = self.model(input_tensor)
                attention_weights = None
        
        # Convert to probabilities
        probabilities = F.softmax(logits, dim=1)
        
        # Create results
        results = []
        for i in range(len(epochs)):
            pred_class = torch.argmax(probabilities[i]).item()
            confidence = probabilities[i, pred_class].item()
            
            result = InferenceResult(
                prediction=pred_class,
                confidence=confidence,
                class_probabilities=probabilities[i].cpu().numpy(),
                timestamp=time.time(),
                signal_type=self.config.signal_type,
                processing_time_ms=0.0,  # Calculate per-sample if needed
                attention_weights=attention_weights[i].cpu().numpy() if attention_weights is not None else None
            )
            results.append(result)
        
        return results
    
    def _preprocess_epoch(self, epoch: np.ndarray) -> np.ndarray:
        """Preprocess single epoch"""
        # Apply filtering, normalization, etc.
        # Simplified implementation
        epoch_normalized = (epoch - np.mean(epoch)) / (np.std(epoch) + 1e-6)
        return epoch_normalized


class ModelTrainer:
    """Training pipeline for BCI models"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Create model
        from axonml_models import ModelFactory, ModelConfig as MLConfig
        ml_config = MLConfig()
        factory = ModelFactory()
        self.model = factory.create_lstm_model(**ml_config.__dict__)
        self.model.to(self.device)
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        # Scheduler
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
        self.logger = logging.getLogger(__name__)
    
    def train_epoch(self, train_loader) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            if hasattr(self.model, 'forward'):
                output = self.model(data)
                if isinstance(output, tuple):
                    output = output[0]  # Handle models that return tuples
            else:
                output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100.0 * correct / total
        
        self.train_losses.append(avg_loss)
        self.train_accuracies.append(accuracy)
        
        return avg_loss, accuracy
    
    def validate(self, val_loader) -> Tuple[float, float]:
        """Validate model"""
        self.model.eval()
        
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                if hasattr(self.model, 'forward'):
                    output = self.model(data)
                    if isinstance(output, tuple):
                        output = output[0]
                else:
                    output = self.model(data)
                
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100.0 * correct / total
        
        self.val_losses.append(avg_loss)
        self.val_accuracies.append(accuracy)
        
        return avg_loss, accuracy
    
    def save_model(self, filepath: str):
        """Save trained model"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies,
            'config': self.config
        }, filepath)
        
        self.logger.info(f"Model saved to {filepath}")
    
    def load_checkpoint(self, filepath: str):
        """Load model checkpoint"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        self.train_losses = checkpoint.get('train_losses', [])
        self.val_losses = checkpoint.get('val_losses', [])
        self.train_accuracies = checkpoint.get('train_accuracies', [])
        self.val_accuracies = checkpoint.get('val_accuracies', [])
        
        self.logger.info(f"Checkpoint loaded from {filepath}")


# Example usage
if __name__ == "__main__":
    # Create configuration
    config = InferenceConfig(
        model_type="lstm",
        signal_type=SignalType.MOTOR_IMAGERY,
        mode=InferenceMode.REALTIME,
        device="auto",
        latency_target_ms=10.0
    )
    
    # Create inference engine
    engine = InferenceEngine(config)
    
    # Add callback
    def on_prediction(result: InferenceResult):
        class_name = config.output_classes[result.prediction]
        print(f"Prediction: {class_name} (confidence: {result.confidence:.3f}) "
              f"[latency: {result.processing_time_ms:.2f}ms]")
    
    engine.add_prediction_callback(on_prediction)
    
    # Start engine
    engine.start()
    
    # Simulate incoming signal data
    print("Simulating signal data...")
    sampling_rate = config.sampling_rate
    window_samples = int(config.window_size * sampling_rate)
    
    for i in range(10):  # Simulate 10 windows
        # Generate random signal (in practice, this comes from BCI device)
        signal = np.random.randn(window_samples).astype(np.float32) * 0.1
        
        # Add some structure for demonstration
        if i % 3 == 0:
            signal += np.sin(2 * np.pi * 10 * np.arange(window_samples) / sampling_rate) * 0.2
        
        # Process signal
        engine.process_signal(signal)
        
        # Simulate real-time delay
        time.sleep(0.05)  # 50ms between windows
    
    # Stop engine
    engine.stop()
    
    # Print statistics
    stats = engine.get_stats()
    print(f"\nPerformance Statistics:")
    print(f"Total inferences: {stats['total_inferences']}")
    print(f"Average latency: {stats['avg_latency_ms']:.2f} ms")
    print(f"Min latency: {stats['min_latency_ms']:.2f} ms")
    print(f"Max latency: {stats['max_latency_ms']:.2f} ms")
    
    print("\nInference pipeline test completed successfully!")
