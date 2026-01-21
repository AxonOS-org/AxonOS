#!/usr/bin/env python3
"""
Real-time Streaming Example
Demonstrates continuous data acquisition and processing
"""

import sys
from pathlib import Path
import asyncio
import time
from datetime import datetime
from typing import Optional, Callable

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from axonos.core.ml import InferenceEngine, InferenceConfig
from axonos.core.ml.inference import SignalType, RealtimeProcessor
from axonos.core.signal import SignalPreprocessor
from axonos.protocol.events import EventFactory, EventType
from axonos.protocol.schemas import NeuralPacket
import numpy as np
import threading
from queue import Queue, Empty


class MockBCIDevice:
    """Mock BCI device for demonstration"""
    
    def __init__(self, num_channels: int = 8, sampling_rate: int = 250):
        self.num_channels = num_channels
        self.sampling_rate = sampling_rate
        self.streaming = False
        self.callbacks: List[Callable] = []
        
    def start_streaming(self):
        """Start generating mock data"""
        self.streaming = True
        print(f"🔄 Mock BCI device started ({self.num_channels} channels, {self.sampling_rate} Hz)")
        
    def stop_streaming(self):
        """Stop streaming"""
        self.streaming = False
        print("⏹️  Mock BCI device stopped")
        
    def register_callback(self, callback: Callable):
        """Register callback for new data"""
        self.callbacks.append(callback)
        
    def generate_data(self, duration_seconds: float = 1.0) -> np.ndarray:
        """Generate mock EEG data"""
        if not self.streaming:
            return np.array([])
            
        num_samples = int(self.sampling_rate * duration_seconds)
        t = np.linspace(0, duration_seconds, num_samples)
        
        # Generate synthetic EEG-like data
        data = np.random.randn(num_samples, self.num_channels) * 0.1
        
        # Add some alpha rhythm (10 Hz)
        for ch in range(self.num_channels):
            alpha_amplitude = 0.3 if ch in [3, 4] else 0.1  # Higher in central channels
            alpha = alpha_amplitude * np.sin(2 * np.pi * 10 * t)
            data[:, ch] += alpha
        
        return data


class RealtimeBCIPipeline:
    """Real-time BCI processing pipeline"""
    
    def __init__(self, num_channels: int = 8, sampling_rate: int = 250):
        self.num_channels = num_channels
        self.sampling_rate = sampling_rate
        
        # Components
        self.device = MockBCIDevice(num_channels, sampling_rate)
        self.preprocessor = SignalPreprocessor(sampling_rate=sampling_rate)
        self.config = InferenceConfig(
            signal_type=SignalType.MOTOR_IMAGERY,
            return_confidence=True,
            return_attention=True,
            latency_target_ms=10.0
        )
        self.processor: Optional[RealtimeProcessor] = None
        
        # State
        self.is_running = False
        self.data_queue = Queue(maxsize=100)
        self.results_queue = Queue(maxsize=100)
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'total_inferences': 0,
            'avg_latency': 0.0,
            'min_latency': float('inf'),
            'max_latency': 0.0
        }
    
    def start(self):
        """Start the real-time pipeline"""
        print("🚀 Starting real-time BCI pipeline...")
        
        # Start device
        self.device.start_streaming()
        
        # Start data acquisition thread
        self.acquisition_thread = threading.Thread(
            target=self._acquisition_loop,
            daemon=True
        )
        self.acquisition_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        
        self.is_running = True
        print("✅ Pipeline started successfully!")
    
    def stop(self):
        """Stop the pipeline"""
        print("⏹️  Stopping real-time pipeline...")
        self.is_running = False
        
        # Stop device
        self.device.stop_streaming()
        
        # Wait for threads
        if hasattr(self, 'acquisition_thread'):
            self.acquisition_thread.join(timeout=1.0)
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=1.0)
        
        print("✅ Pipeline stopped!")
    
    def _acquisition_loop(self):
        """Continuous data acquisition loop"""
        print("📡 Data acquisition thread started")
        
        chunk_duration = 0.5  # 500ms chunks
        chunk_samples = int(self.sampling_rate * chunk_duration)
        
        while self.is_running:
            try:
                # Generate mock data
                data = self.device.generate_data(chunk_duration)
                
                if len(data) > 0:
                    # Create timestamp
                    timestamp = datetime.now()
                    
                    # Add to queue
                    packet = {
                        'data': data,
                        'timestamp': timestamp,
                        'chunk_id': f"chunk_{int(timestamp.timestamp() * 1000)}"
                    }
                    
                    try:
                        self.data_queue.put_nowait(packet)
                    except:
                        # Queue full, drop oldest
                        try:
                            self.data_queue.get_nowait()
                            self.data_queue.put_nowait(packet)
                        except:
                            pass
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
            except Exception as e:
                print(f"⚠️  Acquisition error: {e}")
                time.sleep(0.1)
    
    def _processing_loop(self):
        """Continuous processing loop"""
        print("⚙️  Processing thread started")
        
        # Create inference engine
        factory = ModelFactory()
        model = factory.create_lstm_model(
            input_size=self.num_channels,
            hidden_size=128,
            num_classes=3
        )
        
        engine = InferenceEngine(self.config, model)
        processor = RealtimeProcessor(self.config)
        
        # Add callback for results
        def result_callback(result: InferenceResult):
            self._handle_result(result)
        
        processor.add_callback(result_callback)
        processor.start()
        
        while self.is_running:
            try:
                # Get data from queue
                packet = self.data_queue.get(timeout=0.1)
                
                # Process data
                signal = packet['data']
                
                # Preprocess
                processed = self.preprocessor.preprocess(signal)
                
                # Feed to processor
                processor.feed(processed)
                
                # Update stats
                self.stats['total_packets'] += 1
                
            except Empty:
                continue
            except Exception as e:
                print(f"⚠️  Processing error: {e}")
    
    def _handle_result(self, result: InferenceResult):
        """Handle inference results"""
        self.stats['total_inferences'] += 1
        self.stats['avg_latency'] = (
            (self.stats['avg_latency'] * (self.stats['total_inferences'] - 1) + result.processing_time_ms) 
            / self.stats['total_inferences']
        )
        self.stats['min_latency'] = min(self.stats['min_latency'], result.processing_time_ms)
        self.stats['max_latency'] = max(self.stats['max_latency'], result.processing_time_ms)
        
        # Create event
        event_type = [EventType.LEFT_HAND_IMAGERY, EventType.RIGHT_HAND_IMAGERY, EventType.REST][result.prediction]
        
        event = EventFactory.create_motor_imagery_event(
            laterality=["left", "right", "bilateral"][result.prediction],
            body_part="hand",
            device_id="realtime_pipeline",
            confidence=result.confidence,
            processing_time_ms=result.processing_time_ms
        )
        
        # Print result
        print(f"\r🎯 {event.event_type.value.upper()} "
              f"(conf: {result.confidence:.2f}) "
              f"(lat: {result.processing_time_ms:.2f}ms) "
              f"(avg: {self.stats['avg_latency']:.2f}ms)", 
              end='', flush=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return self.stats.copy()
    
    def print_statistics(self):
        """Print detailed statistics"""
        print(f"\n\n📊 Pipeline Statistics:")
        print(f"   Total packets: {self.stats['total_packets']}")
        print(f"   Total inferences: {self.stats['total_inferences']}")
        print(f"   Average latency: {self.stats['avg_latency']:.2f}ms")
        print(f"   Min latency: {self.stats['min_latency']:.2f}ms")
        print(f"   Max latency: {self.stats['max_latency']:.2f}ms")
        print(f"   Data queue size: {self.data_queue.qsize()}")
        print(f"   Results queue size: {self.results_queue.qsize()}")


def simulate_user_feedback(pipeline: RealtimeBCIPipeline):
    """Simulate user providing feedback for calibration"""
    print("\n🎮 User Feedback Simulation")
    print("-" * 30)
    
    feedback_commands = [
        {"time": 5, "command": "start_left_imagery", "duration": 10},
        {"time": 20, "command": "start_right_imagery", "duration": 10},
        {"time": 35, "command": "start_rest", "duration": 10},
    ]
    
    start_time = time.time()
    
    for cmd in feedback_commands:
        while time.time() - start_time < cmd["time"]:
            time.sleep(0.1)
        
        print(f"🧠 User: {cmd['command']} for {cmd['duration']} seconds")
        
        # In a real system, this would trigger calibration
        # pipeline.calibrate_from_feedback(cmd['command'])


def main():
    print("🚀 Real-time Streaming Example")
    print("=" * 50)
    
    # Create pipeline
    pipeline = RealtimeBCIPipeline(num_channels=8, sampling_rate=250)
    
    # Start pipeline
    pipeline.start()
    
    # Start user feedback simulation in separate thread
    feedback_thread = threading.Thread(
        target=simulate_user_feedback,
        args=(pipeline,),
        daemon=True
    )
    feedback_thread.start()
    
    try:
        # Run for specified duration
        runtime_seconds = 45
        print(f"\n⏱️  Running for {runtime_seconds} seconds...")
        print("   Watch for real-time predictions!")
        print("   Press Ctrl+C to stop early\n")
        
        for i in range(runtime_seconds):
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                print(f"\n⏳ Running... {i}/{runtime_seconds} seconds")
        
        print("\n⏹️  Runtime completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    
    finally:
        # Stop pipeline
        pipeline.stop()
        
        # Print final statistics
        pipeline.print_statistics()
        
        print("\n✅ Real-time streaming example completed!")
        print("\n🔮 Next steps:")
        print("  - Connect real BCI device instead of mock")
        print("  - Add visualization of results")
        print("  - Implement online learning")
        print("  - Add more sophisticated event handling")


if __name__ == "__main__":
    import torch
    main()