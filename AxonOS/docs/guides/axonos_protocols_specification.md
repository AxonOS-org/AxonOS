# AxonOS™ Protocols & Data Flow Specification
## Technical Architecture Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Signal Bus Protocol](#signal-bus-protocol)
3. [gRPC API Specification](#grpc-api-specification)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Message Formats](#message-formats)
6. [Timing & Synchronization](#timing--synchronization)
7. [Error Handling](#error-handling)

---

## Overview

AxonOS uses a multi-layer protocol stack designed for:
- **Low latency** (< 10ms end-to-end)
- **High throughput** (1000+ channels at 1kHz)
- **Reliability** (99.99% uptime)
- **Security** (end-to-end encryption)
- **Extensibility** (plugin architecture)

### Protocol Stack

```
┌─ Application Layer ──────────────────────────────┐
│  Cognitive Apps, AI Agents, Avatars              │
├─ API Layer ──────────────────────────────────────┤
│  GraphQL, REST, WebSocket, gRPC                  │
├─ Signal Bus Protocol ────────────────────────────┤
│  Real-time streaming, pub/sub, time sync         │
├─ Transport Layer ────────────────────────────────┤
│  gRPC over HTTP/2, WebRTC for P2P                │
├─ Security Layer ─────────────────────────────────┤
│  mTLS, End-to-end encryption, WASM sandbox       │
└─ Hardware Abstraction ───────────────────────────┘
   BCI Device Drivers (OpenBCI, LSL, BrainFlow)
```

---

## Signal Bus Protocol

The Signal Bus is the central nervous system of AxonOS, providing:
- **Unified data streaming** from all BCI devices
- **Time synchronization** across distributed components
- **Publish/subscribe** messaging pattern
- **Quality of Service** (QoS) guarantees

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SIGNAL BUS                           │
├─────────────────────────────────────────────────────────┤
│  Publishers                    Subscribers              │
│  ┌─────────┐                  ┌─────────┐                │
│  │ OpenBCI │───┐             ┌───│  ML     │                │
│  ├─────────┤   │             │   ├─────────┤                │
│  │ BrainF. │   │   ┌─────┐   │   │  Apps   │                │
│  ├─────────┤   └──▶│ Bus │◀──┤   ├─────────┤                │
│  │ Custom  │──────▶│     │◀──┤   │ Storage │                │
│  └─────────┘      └─────┘   │   └─────────┘                │
│                             │                              │
│  ┌─────────┐                │   ┌─────────┐                │
│  │ LSL     │───────────────▶│   │ Security│                │
│  └─────────┘               │   └─────────┘                │
└────────────────────────────┴──────────────────────────────┘
```

### Message Types

```protobuf
// Signal Bus Protocol Buffers
syntax = "proto3";

package axonos.signal.v1;

message SignalPacket {
  string device_id = 1;
  string stream_id = 2;
  int64 timestamp_ns = 3;
  repeated ChannelData channels = 4;
  map<string, string> metadata = 5;
}

message ChannelData {
  uint32 channel_id = 1;
  string channel_name = 2;
  repeated float samples = 3;
  SamplingInfo sampling = 4;
}

message SamplingInfo {
  double rate_hz = 1;
  uint32 resolution_bits = 2;
  double voltage_range_mv = 3;
}

message TimeSync {
  int64 client_timestamp_ns = 1;
  int64 server_timestamp_ns = 2;
  int64 round_trip_ns = 3;
}
```

### Topics & Routing

**Topic Structure**: `axonos.{domain}.{device_type}.{stream_type}.{format}`

Examples:
- `axonos.eeg.openbci.cortex.raw`
- `axonos.eeg.muse.meditation.filtered`
- `axonos.emg.generic.motor_imagery.features`
- `axonos.fnirs.brain_products.oxyhemoglobin.concentration`

**Routing Rules**:
- Wildcards supported: `axonos.eeg.*.raw`
- Quality of Service levels
- Persistent subscriptions
- Message filtering by metadata

### Quality of Service

| QoS Level | Description | Use Case |
|-----------|-------------|----------|
| **QoS 0** | Best effort, no guarantee | Real-time display |
| **QoS 1** | At least once delivery | Critical processing |
| **QoS 2** | Exactly once delivery | Medical applications |
| **QoS 3** | Persistent + replay | Research datasets |

---

## gRPC API Specification

### Service Structure

```protobuf
// Core AxonOS Services
service AxonCore {
  // Signal streaming
  rpc StreamSignals(StreamConfig) returns (stream SignalPacket);
  
  // Device control
  rpc ControlDevice(DeviceCommand) returns (CommandResponse);
  
  // Configuration management
  rpc GetConfig(ConfigRequest) returns (ConfigResponse);
  rpc SetConfig(ConfigUpdate) returns (OperationStatus);
}

service AxonML {
  // Model management
  rpc LoadModel(ModelSpec) returns (ModelStatus);
  rpc UnloadModel(ModelId) returns (OperationStatus);
  
  // Real-time inference
  rpc Predict(stream FeaturePacket) returns (stream Prediction);
  
  // Model training (offline)
  rpc TrainModel(TrainingData) returns (TrainingStatus);
}

service AxonNet {
  // Application management
  rpc RegisterApp(AppInfo) returns (AppRegistration);
  rpc GetApps(AppFilter) returns (stream AppInfo);
  
  // Plugin management
  rpc LoadPlugin(PluginSpec) returns (PluginStatus);
  rpc ExecutePlugin(stream PluginInput) returns (stream PluginOutput);
  
  // Event streaming
  rpc SubscribeEvents(EventFilter) returns (stream Event);
}

service AxonShield {
  // Key management
  rpc GenerateKey(KeySpec) returns (KeyInfo);
  rpc GetPublicKey(KeyId) returns (PublicKey);
  
  // Encryption/Decryption
  rpc Encrypt(Plaintext) returns (Ciphertext);
  rpc Decrypt(Ciphertext) returns (Plaintext);
  
  // Access control
  rpc CheckPermission(PermissionRequest) returns (PermissionResponse);
}
```

### Streaming Configuration

```protobuf
message StreamConfig {
  string device_id = 1;
  repeated string topics = 2;
  SamplingConfig sampling = 3;
  FilterConfig filters = 4;
  QualityOfService qos = 5;
  CompressionType compression = 6;
}

message SamplingConfig {
  double rate_hz = 1;
  uint32 buffer_size = 2;
  bool enable_oversampling = 3;
}

message FilterConfig {
  repeated BandPassFilter bandpass = 1;
  repeated NotchFilter notch = 2;
  SpatialFilter spatial = 3;
  ArtifactFilter artifacts = 4;
}

message BandPassFilter {
  double low_freq_hz = 1;
  double high_freq_hz = 2;
  FilterType type = 3;
}

enum FilterType {
  BUTTERWORTH = 0;
  CHEBYSHEV = 1;
  BESSEL = 2;
}

enum QualityOfService {
  BEST_EFFORT = 0;
  AT_LEAST_ONCE = 1;
  EXACTLY_ONCE = 2;
  PERSISTENT = 3;
}

enum CompressionType {
  NONE = 0;
  GZIP = 1;
  ZSTD = 2;
  CUSTOM = 3;
}
```

### Error Handling

```protobuf
message Error {
  Code code = 1;
  string message = 2;
  map<string, string> details = 3;
  int64 timestamp_ns = 4;
}

enum Code {
  OK = 0;
  CANCELLED = 1;
  UNKNOWN = 2;
  INVALID_ARGUMENT = 3;
  DEADLINE_EXCEEDED = 4;
  NOT_FOUND = 5;
  ALREADY_EXISTS = 6;
  PERMISSION_DENIED = 7;
  RESOURCE_EXHAUSTED = 8;
  FAILED_PRECONDITION = 9;
  ABORTED = 10;
  OUT_OF_RANGE = 11;
  UNIMPLEMENTED = 12;
  INTERNAL = 13;
  UNAVAILABLE = 14;
  DATA_LOSS = 15;
  UNAUTHENTICATED = 16;
}
```

---

## Data Flow Architecture

### Real-time Pipeline

```
┌─ Acquisition ─┐   ┌─ Preprocessing ─┐   ┌─ Feature Extract ─┐   ┌─ Classification ─┐
│               │   │                 │   │                   │   │                  │
│  Raw Signals  │──▶│  Bandpass       │──▶│  CSP / PSD        │──▶│  LDA / CNN        │
│  (1kHz)       │   │  Notch 60Hz     │   │  Wavelet          │   │  Transformer      │
│               │   │  CAR            │   │  Statistical      │   │  RNN / LSTM       │
└───────────────┘   └─────────────────┘   └───────────────────┘   └──────────────────┘
         │                    │                    │                    │
         ▼                    ▼                    ▼                    ▼
┌─ Raw Storage ─┐   ┌─ Filtered Storage ┐   ┌─ Feature Storage ─┐   ┌─ Prediction Bus ─┐
```

### Batch Processing Pipeline

```
┌─ Data Ingestion ─┐   ┌─ Data Cleaning ─┐   ┌─ Feature Engineering ─┐
│                  │   │                 │   │                       │
│  Multiple        │──▶│  Artifact       │──▶│  Windowing            │
│  Sessions        │   │  Detection      │   │  Spectral Features    │
│                  │   │  Interpolation  │   │  Connectivity           │
└──────────────────┘   └─────────────────┘   └───────────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─ Model Training ─┐    ┌─ Validation ─┐
                       │                  │    │              │
                       │  Hyperparameter  │    │  Cross-val   │
                       │  Optimization    │    │  Test Set    │
                       │  Ensemble        │    │  Metrics     │
                       └──────────────────┘    └──────────────┘
```

### Message Flow Example

```
1. Device → Signal Bus
   {
     "device_id": "openbci_cyton_001",
     "stream_id": "eeg_raw",
     "timestamp_ns": 1640995200000000000,
     "channels": [
       {
         "channel_id": 1,
         "channel_name": "C3",
         "samples": [12.5, 12.7, 12.3, ...],
         "sampling": {
           "rate_hz": 250,
           "resolution_bits": 24,
           "voltage_range_mv": 187.5
         }
       },
       ...
     ],
     "metadata": {
       "subject_id": "P001",
       "session_type": "motor_imagery",
       "impedance_ok": "true"
     }
   }

2. Signal Bus → Preprocessing
   - Apply bandpass filter (1-50Hz)
   - Apply notch filter (60Hz)
   - Apply CAR (Common Average Reference)
   - Output: FilteredSignal packet

3. Preprocessing → Feature Extraction
   - Compute CSP (Common Spatial Patterns)
   - Compute band power (mu, beta)
   - Compute statistical features
   - Output: FeatureVector packet

4. Feature Extraction → Classification
   - Input: FeatureVector
   - Model: CNN + LDA ensemble
   - Output: Prediction (left_hand: 0.85, right_hand: 0.15)

5. Classification → Application
   - Intent: "Move left hand"
   - Command: translate_to_robot_control()
   - Action: Robot arm moves left
```

---

## Message Formats

### Raw Signal Packet

```json
{
  "version": "1.0",
  "packet_type": "raw_signal",
  "header": {
    "device_id": "openbci_cyton_001",
    "stream_id": "eeg_raw",
    "sequence_number": 123456,
    "timestamp_ns": 1640995200000000000,
    "timestamp_quality": "high"
  },
  "payload": {
    "num_channels": 8,
    "num_samples": 25,
    "sampling_rate_hz": 250,
    "data_type": "float32",
    "channels": [
      {
        "id": 1,
        "name": "C3",
        "samples": [12.5, 12.7, 12.3, 12.1, 12.8],
        "gain": 24,
        "offset": 0
      }
    ],
    "trigger": {
      "present": true,
      "channel": 9,
      "values": [0, 0, 1, 0, 0]
    }
  },
  "metadata": {
    "subject": "P001",
    "session": "motor_imagery_001",
    "impedances": {
      "C3": "ok",
      "C4": "ok",
      "Cz": "high"
    }
  },
  "checksum": "a1b2c3d4e5f6"
}
```

### Feature Vector Packet

```json
{
  "version": "1.0",
  "packet_type": "features",
  "header": {
    "source_stream": "eeg_raw",
    "window_start_ns": 1640995200000000000,
    "window_duration_ms": 200,
    "overlap_percent": 50
  },
  "payload": {
    "features": {
      "band_power": {
        "delta": {"mean": 12.5, "var": 2.1},
        "theta": {"mean": 8.3, "var": 1.7},
        "alpha": {"mean": 15.2, "var": 3.4},
        "beta": {"mean": 6.8, "var": 1.2},
        "gamma": {"mean": 3.1, "var": 0.8}
      },
      "csp": {
        "components": [0.12, -0.45, 0.78, -0.23, 0.67]
      },
      "statistical": {
        "mean": 10.2,
        "variance": 4.5,
        "skewness": -0.12,
        "kurtosis": 2.8
      }
    },
    "channels_used": ["C3", "C4", "Cz", "P3", "P4"],
    "dimensionality": 125
  }
}
```

### Prediction Packet

```json
{
  "version": "1.0",
  "packet_type": "prediction",
  "header": {
    "model_id": "motor_imagery_cnn_v2.1",
    "inference_time_ms": 3.2,
    "confidence_threshold": 0.6
  },
  "payload": {
    "classes": [
      {"name": "left_hand", "probability": 0.85, "confidence": "high"},
      {"name": "right_hand", "probability": 0.12, "confidence": "low"},
      {"name": "rest", "probability": 0.03, "confidence": "low"}
    ],
    "winner": "left_hand",
    "uncertainty": 0.15,
    "needs_calibration": false
  },
  "control": {
    "action": "move_left",
    "intensity": 0.85,
    "duration_ms": 500
  }
}
```

---

## Timing & Synchronization

### Time Synchronization Protocol

```
Client                          Server
  │                              │
  │─── TimeRequest (T1) ────────▶│
  │                              │
  │◀──── TimeResponse (T2, T3) ──│
  │                              │
  │─── Ack (T4) ────────────────▶│
  │                              │

Round-trip time: RTT = (T4 - T1) - (T3 - T2)
Offset: θ = ((T2 - T1) + (T3 - T4)) / 2
```

### Timing Requirements

| Component | Max Latency | Jitter | Throughput |
|-----------|-------------|--------|------------|
| Signal Acquisition | 1ms | 0.1ms | 4 MB/s |
| Preprocessing | 2ms | 0.5ms | 4 MB/s |
| Feature Extraction | 3ms | 1ms | 100 KB/s |
| Classification | 5ms | 2ms | 1 KB/s |
| Application Response | 10ms | 5ms | 100 B/s |

### Buffer Management

```
┌─ Ring Buffer ─┐
│               │
│  [W]───────▶  │  Write pointer (producer)
│               │
│  ◀───────[R]  │  Read pointer (consumer)
│               │
│  [========]   │  Valid data
│               │
└───────────────┘

Buffer size = sampling_rate * num_channels * buffer_duration * sizeof(float)
Example: 1000 Hz * 64 ch * 0.1s * 4 bytes = 25.6 KB
```

---

## Error Handling

### Error Recovery Strategies

| Error Type | Detection | Recovery Strategy |
|------------|-----------|-------------------|
| **Device Disconnect** | Heartbeat timeout | Auto-reconnect, buffer replay |
| **Data Corruption** | Checksum mismatch | Drop packet, interpolate |
| **Processing Failure** | Exception handling | Fallback to simpler model |
| **Network Partition** | Health check timeout | Local processing, sync later |
| **Memory Exhaustion** | Allocation failure | Drop non-critical streams |

### Health Monitoring

```protobuf
message HealthStatus {
  string component_id = 1;
  ComponentType type = 2;
  Status status = 3;
  repeated Metric metrics = 4;
  int64 last_heartbeat_ns = 5;
}

message Metric {
  string name = 1;
  double value = 2;
  string unit = 3;
  int64 timestamp_ns = 4;
}

enum Status {
  HEALTHY = 0;
  DEGRADED = 1;
  UNHEALTHY = 2;
  DOWN = 3;
}

// Metrics collected:
// - Latency P50, P95, P99
// - Throughput (messages/sec)
// - Error rate
// - Memory usage
// - CPU utilization
// - Network bandwidth
```

---

## Next Steps

1. **Implement core protocol stack** (Rust for performance)
2. **Develop device drivers** (C++ for embedded)
3. **Build Signal Bus** (gRPC + custom streaming)
4. **Create ML pipeline** (Python + ONNX)
5. **Implement security layer** (Rust + WASM sandbox)
6. **Build developer SDK** (Multi-language bindings)

---

*Document version: 1.0*  
*Last updated: 2026-01-17*
