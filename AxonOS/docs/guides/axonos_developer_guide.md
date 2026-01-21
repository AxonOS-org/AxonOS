# AxonOS™ Developer Guide
## Technical Documentation for Contributors

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [Development Environment](#development-environment)
4. [API Reference](#api-reference)
5. [SDK Development](#sdk-development)
6. [Plugin Development](#plugin-development)
7. [Best Practices](#best-practices)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Quick Start

```bash
# Clone AxonOS repository
git clone https://github.com/axonos/axonos.git
cd axonos

# Install dependencies
./scripts/install-deps.sh

# Build AxonOS
./scripts/build.sh

# Run tests
./scripts/test.sh

# Start development environment
docker-compose up -d
```

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS (12.0+), Windows (WSL2)
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum, 8 cores recommended
- **Storage**: 10GB minimum, SSD recommended
- **Docker**: 20.10+
- **Rust**: 1.70+
- **Python**: 3.9+

### Repository Structure

```
axonos/
├── axoncore/           # Firmware & embedded systems
│   ├── src/
│   ├── drivers/
│   ├── dsp/
│   └── tests/
├── axonstream/         # Data pipeline (Rust)
│   ├── src/
│   ├── proto/
│   └── tests/
├── axonml/             # AI/ML runtime
│   ├── src/
│   ├── models/
│   ├── training/
│   └── inference/
├── axonnet/            # API gateway (Rust)
│   ├── src/
│   ├── api/
│   └── sdk/
├── axonshield/         # Security layer
│   ├── src/
│   ├── crypto/
│   └── sandbox/
├── axonstore/          # Data storage
│   ├── src/
│   └── migrations/
├── plugins/            # Official plugins
│   ├── drivers/
│   ├── processors/
│   └── applications/
├── sdk/                # Language SDKs
│   ├── python/
│   ├── javascript/
│   ├── java/
│   └── cpp/
├── docs/               # Documentation
├── scripts/            # Build & utility scripts
└── tests/              # Integration tests
```

---

## Architecture Overview

### Component Interaction

```
┌─ Application Layer ──────────────────────────────────────┐
│  Cognitive Apps, AI Agents, Avatars                      │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │              AXONNET API GATEWAY                  │   │
│  │  GraphQL • REST • WebSocket • gRPC               │   │
│  │                          │                       │   │
│  │                          ▼                       │   │
│  │  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │  AUTHENTICATE │  │  AUTHORIZE  │             │   │
│  │  │  • mTLS      │  │  • RBAC     │             │   │
│  │  │  • JWT       │  │  • ABAC     │             │   │
│  │  └──────────────┘  └──────────────┘             │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
├─ AI/ML Layer ────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │              AXONML AI RUNTIME                    │   │
│  │  • Model Inference                               │   │
│  │  • Feature Extraction                            │   │
│  │  • Cognitive Models                              │   │
│  │                          │                       │   │
│  │                          ▼                       │   │
│  │  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │  TRAINING   │  │  INFERENCE  │             │   │
│  │  │  • AutoML   │  │  • ONNX     │             │   │
│  │  │  • Privacy  │  │  • GPU      │             │   │
│  │  └──────────────┘  └──────────────┘             │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
├─ Data Layer ─────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │              AXONSTREAM PIPELINE                  │   │
│  │  • Real-time Streaming                           │   │
│  │  • Time Synchronization                          │   │
│  │  • Signal Processing                             │   │
│  │                          │                       │   │
│  │                          ▼                       │   │
│  │  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │  INGEST     │  │  PROCESS    │             │   │
│  │  │  • Buffer   │  │  • Filter   │             │   │
│  │  │  • Validate │  │  • Extract  │             │   │
│  │  └──────────────┘  └──────────────┘             │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
├─ Hardware Layer ─────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │              AXONCORE FIRMWARE                    │   │
│  │  • Device Drivers                                │   │
│  │  • Real-time DSP                                 │   │
│  │  • Signal Acquisition                            │   │
│  │                          │                       │   │
│  │                          ▼                       │   │
│  │  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │  OpenBCI    │  │  LSL        │             │   │
│  │  │  BrainFlow  │  │  Custom     │             │   │
│  │  └──────────────┘  └──────────────┘             │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
└──────────────────────────┴───────────────────────────────┘
```

### Data Flow

```
1. Signal Acquisition (AxonCore)
   - BCI devices → Drivers → Raw signals
   - Sampling: 250-1000 Hz
   - Latency: < 1ms

2. Signal Processing (AxonStream)
   - Raw signals → Filtering → Feature extraction
   - Windowing: 200-1000ms
   - Latency: < 5ms

3. AI Inference (AxonML)
   - Features → Models → Predictions
   - Models: CNN, Transformer, Ensemble
   - Latency: < 5ms

4. Application Interface (AxonNet)
   - Predictions → API → Applications
   - Protocols: GraphQL, REST, WebSocket
   - Latency: < 10ms total
```

---

## Development Environment

### Docker Development

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  axoncore:
    build:
      context: .
      dockerfile: axoncore/Dockerfile
    volumes:
      - ./axoncore:/app
      - /dev:/dev  # Device access
    privileged: true
    environment:
      - RUST_LOG=debug
      - AXONCORE_DEVICE=openbci

  axonstream:
    build:
      context: .
      dockerfile: axonstream/Dockerfile
    ports:
      - "50051:50051"  # gRPC
    volumes:
      - ./axonstream:/app
    environment:
      - RUST_LOG=info
      - DATABASE_URL=postgres://axonos:password@db:5432/axonos

  axonml:
    build:
      context: .
      dockerfile: axonml/Dockerfile
    ports:
      - "50052:50052"  # gRPC
    volumes:
      - ./axonml:/app
      - ./models:/models
    environment:
      - PYTHONPATH=/app
      - CUDA_VISIBLE_DEVICES=0

  axonnet:
    build:
      context: .
      dockerfile: axonnet/Dockerfile
    ports:
      - "8080:8080"  # HTTP
      - "8081:8081"  # GraphQL
    volumes:
      - ./axonnet:/app
    environment:
      - RUST_LOG=info

  db:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: axonos
      POSTGRES_USER: axonos
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Local Development

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node.js dependencies
cd sdk/javascript
npm install

# Build all components
./scripts/build-all.sh

# Run tests
./scripts/test-all.sh

# Start development server
./scripts/dev-server.sh
```

---

## API Reference

### gRPC Services

#### AxonCore Service

```protobuf
service AxonCore {
  // Stream real-time signals
  rpc StreamSignals(StreamConfig) returns (stream SignalPacket);
  
  // Control BCI device
  rpc ControlDevice(DeviceCommand) returns (CommandResponse);
  
  // Get device configuration
  rpc GetDeviceConfig(ConfigRequest) returns (DeviceConfig);
  
  // Set device configuration
  rpc SetDeviceConfig(ConfigUpdate) returns (OperationStatus);
}

// Example usage (Python)
import grpc
from axonos.proto import axoncore_pb2, axoncore_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = axoncore_pb2_grpc.AxonCoreStub(channel)

# Stream signals
config = axoncore_pb2.StreamConfig(
    device_id="openbci_cyton_001",
    topics=["axonos.eeg.raw"],
    sampling_rate_hz=250
)

for packet in stub.StreamSignals(config):
    process_signal(packet)
```

#### AxonML Service

```protobuf
service AxonML {
  // Load ML model
  rpc LoadModel(ModelSpec) returns (ModelStatus);
  
  // Real-time prediction
  rpc Predict(stream FeaturePacket) returns (stream Prediction);
  
  // Get model info
  rpc GetModelInfo(ModelId) returns (ModelInfo);
}

// Example usage (Python)
import numpy as np
from axonos.proto import axonml_pb2, axonml_pb2_grpc

stub = axonml_pb2_grpc.AxonMLStub(channel)

# Load model
model_spec = axonml_pb2.ModelSpec(
    model_id="motor_imagery_cnn_v2.1",
    path="/models/motor_imagery_cnn.onnx"
)
status = stub.LoadModel(model_spec)

# Make prediction
features = axonml_pb2.FeaturePacket(
    features=np.random.randn(125).tolist(),
    timestamp_ns=time.time_ns()
)
prediction = stub.Predict(iter([features]))
```

#### AxonNet Service

```protobuf
service AxonNet {
  // Register application
  rpc RegisterApp(AppInfo) returns (AppRegistration);
  
  // Execute plugin
  rpc ExecutePlugin(stream PluginInput) returns (stream PluginOutput);
  
  // Subscribe to events
  rpc SubscribeEvents(EventFilter) returns (stream Event);
}

// Example usage (JavaScript)
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDefinition = protoLoader.loadSync(
  'axonos/proto/axonnet.proto',
  { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true }
);

const axonnetProto = grpc.loadPackageDefinition(packageDefinition).axonos.axonnet.v1;
const client = new axonnetProto.AxonNet('localhost:50051', grpc.credentials.createInsecure());

// Register app
const appInfo = {
  name: 'Neural Typing App',
  description: 'BCI-based text input',
  permissions: ['read:eeg', 'write:commands']
};

client.RegisterApp(appInfo, (err, response) => {
  if (err) console.error(err);
  else console.log('App registered:', response);
});
```

### REST API

#### Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "researcher@example.com",
  "password": "secure_password",
  "device_id": "openbci_cyton_001"
}

---

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

#### Signal Streaming

```http
GET /api/v1/signals/stream
Authorization: Bearer {access_token}
Accept: text/event-stream

Query Parameters:
- device_id: string (required)
- channels: string[] (optional)
- sampling_rate: number (optional)
- window_size: number (optional)
```

#### Model Inference

```http
POST /api/v1/models/{model_id}/predict
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "features": [0.1, 0.2, 0.3, ...],
  "window_size": 200,
  "return_probabilities": true
}

---

Response:
{
  "prediction": "left_hand",
  "confidence": 0.85,
  "probabilities": {
    "left_hand": 0.85,
    "right_hand": 0.12,
    "rest": 0.03
  },
  "timestamp": "2026-01-17T10:30:00Z"
}
```

### GraphQL API

```graphql
# Schema definition
type Query {
  device(id: ID!): Device
  model(id: ID!): Model
  session(id: ID!): Session
  user(id: ID!): User
}

type Mutation {
  startSession(input: StartSessionInput!): Session!
  stopSession(id: ID!): Session!
  updateDeviceConfig(id: ID!, config: DeviceConfigInput!): Device!
}

type Subscription {
  signalStream(deviceId: ID!): SignalPacket!
  predictions(sessionId: ID!): Prediction!
  events(filter: EventFilter!): Event!
}

# Example queries
query GetDevice($id: ID!) {
  device(id: $id) {
    id
    name
    status
    config {
      samplingRate
      channels
    }
  }
}

mutation StartSession($input: StartSessionInput!) {
  startSession(input: $input) {
    id
    status
    startTime
  }
}

subscription SignalStream($deviceId: ID!) {
  signalStream(deviceId: $deviceId) {
    timestamp
    channels {
      id
      name
      samples
    }
  }
}
```

---

## SDK Development

### Python SDK

```python
# Installation
pip install axonos-sdk

# Usage
from axonos import AxonOS

# Initialize client
client = AxonOS(
    api_key="your_api_key",
    base_url="https://api.axonos.io",
    device_id="openbci_cyton_001"
)

# Connect to device
with client.connect() as session:
    # Start signal streaming
    stream = session.stream_signals(
        channels=["C3", "C4", "Cz"],
        sampling_rate=250
    )
    
    # Process signals in real-time
    for packet in stream:
        features = extract_features(packet)
        prediction = session.predict("motor_imagery", features)
        
        if prediction.class_name == "left_hand":
            send_command("move_left")
```

### JavaScript SDK

```javascript
// Installation
npm install @axonos/sdk

// Usage
import { AxonOS } from '@axonos/sdk';

const client = new AxonOS({
  apiKey: 'your_api_key',
  baseURL: 'https://api.axonos.io',
  deviceId: 'openbci_cyton_001'
});

// Connect and stream
const session = await client.connect();
const stream = session.streamSignals({
  channels: ['C3', 'C4', 'Cz'],
  samplingRate: 250
});

// Process signals
stream.on('data', (packet) => {
  const features = extractFeatures(packet);
  const prediction = await session.predict('motor_imagery', features);
  
  if (prediction.className === 'left_hand') {
    sendCommand('move_left');
  }
});
```

### C++ SDK

```cpp
#include <axonos/axonos.hpp>

int main() {
    // Initialize client
    axonos::Client client(
        "your_api_key",
        "https://api.axonos.io",
        "openbci_cyton_001"
    );
    
    // Connect to device
    auto session = client.connect();
    
    // Configure stream
    axonos::StreamConfig config;
    config.channels = {"C3", "C4", "Cz"};
    config.sampling_rate = 250;
    
    // Start streaming
    auto stream = session.stream_signals(config);
    
    // Process signals
    stream.on_data([](const axonos::SignalPacket& packet) {
        auto features = extract_features(packet);
        auto prediction = session.predict("motor_imagery", features);
        
        if (prediction.class_name == "left_hand") {
            send_command("move_left");
        }
    });
    
    return 0;
}
```

---

## Plugin Development

### Plugin Structure

```
my-plugin/
├── Cargo.toml          # Rust dependencies
├── src/
│   ├── lib.rs         # Plugin entry point
│   ├── processor.rs   # Signal processing
│   └── config.rs      # Configuration
├── tests/
│   └── integration.rs
├── README.md
└── axonos.toml        # Plugin manifest
```

### Plugin Manifest

```toml
# axonos.toml
[plugin]
name = "my-signal-processor"
version = "1.0.0"
description = "Custom signal processing plugin"
author = "Your Name"
license = "MIT"

[capabilities]
signal_processing = true
ml_inference = false
network_access = false
file_system = "readonly"

[permissions]
required = ["read:signals", "write:processed"]
optional = ["read:models"]

[resources]
max_memory = "64MB"
max_cpu = "0.5"
max_execution_time = "5s"

[config]
param1 = { type = "float", default = 1.0, description = "Processing parameter" }
param2 = { type = "int", default = 10, description = "Window size" }
```

### Plugin Implementation

```rust
use axonos_plugin_api::{Plugin, SignalPacket, ProcessedPacket};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct Config {
    param1: f64,
    param2: usize,
}

struct MyProcessor {
    config: Config,
}

impl Plugin for MyProcessor {
    fn new(config: serde_json::Value) -> Self {
        let config: Config = serde_json::from_value(config)
            .expect("Invalid configuration");
        Self { config }
    }
    
    fn process(&self, packet: SignalPacket) -> ProcessedPacket {
        // Custom processing logic
        let processed_samples = packet.samples
            .iter()
            .map(|&x| x * self.config.param1)
            .collect();
        
        ProcessedPacket {
            device_id: packet.device_id,
            timestamp_ns: packet.timestamp_ns,
            samples: processed_samples,
            metadata: packet.metadata,
        }
    }
    
    fn get_info(&self) -> serde_json::Value {
        json!({
            "name": "my-signal-processor",
            "version": env!("CARGO_PKG_VERSION"),
            "description": "Custom signal processing",
            "config": self.config
        })
    }
}

// Export plugin
axonos_plugin_api::export_plugin!(MyProcessor);
```

### Building and Deploying Plugins

```bash
# Build plugin (creates WASM file)
cargo build --target wasm32-unknown-unknown --release

# Upload to AxonOS
axonos plugin upload target/wasm32-unknown-unknown/release/my_processor.wasm

# Deploy to specific device
axonos plugin deploy my-signal-processor --device openbci_cyton_001

# Configure plugin
axonos plugin config my-signal-processor set param1=2.0 param2=20

# Monitor plugin
axonos plugin logs my-signal-processor --follow
```

---

## Best Practices

### Performance

1. **Minimize Allocations**
   ```rust
   // Good: Pre-allocate buffer
   let mut buffer = Vec::with_capacity(1000);
   
   // Bad: Repeated allocation
   let mut buffer = Vec::new();
   ```

2. **Use Zero-Copy Where Possible**
   ```rust
   // Good: Zero-copy slice
   let view = &data[start..end];
   
   // Bad: Unnecessary copy
   let copy = data[start..end].to_vec();
   ```

3. **Profile Before Optimizing**
   ```bash
   cargo bench
   cargo flamegraph
   ```

### Security

1. **Validate All Inputs**
   ```rust
   fn process_signal(data: &[f32]) -> Result<Processed, Error> {
       if data.len() > MAX_SIGNAL_LENGTH {
           return Err(Error::InvalidLength);
       }
       // ...
   }
   ```

2. **Use Constant-Time Operations**
   ```rust
   use subtle::ConstantTimeEq;
   
   // Good: Constant-time comparison
   if secret.ct_eq(&expected).unwrap_u8() == 1 {
       // ...
   }
   ```

3. **Handle Errors Gracefully**
   ```rust
   match result {
       Ok(data) => process_data(data),
       Err(e) => {
           log_error(&e);
           return default_response();
       }
   }
   ```

### Testing

1. **Unit Tests**
   ```rust
   #[cfg(test)]
   mod tests {
       use super::*;
       
       #[test]
       fn test_signal_processing() {
           let input = vec![1.0, 2.0, 3.0];
           let expected = vec![2.0, 4.0, 6.0];
           assert_eq!(process_signal(input), expected);
       }
   }
   ```

2. **Integration Tests**
   ```bash
   # Run integration tests
   cargo test --test integration
   
   # Run with coverage
   cargo tarpaulin --out html
   ```

3. **Benchmark Tests**
   ```rust
   use criterion::{black_box, criterion_group, criterion_main, Criterion};
   
   fn bench_signal_processing(c: &mut Criterion) {
       c.bench_function("process_signal", |b| {
           let data = vec![1.0; 1000];
           b.iter(|| process_signal(black_box(&data)))
       });
   }
   
   criterion_group!(benches, bench_signal_processing);
   criterion_main!(benches);
   ```

---

## Deployment

### Docker Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  axoncore:
    image: axonos/axoncore:latest
    restart: unless-stopped
    environment:
      - RUST_LOG=info
      - DEVICE_TYPE=openbci
    volumes:
      - /dev:/dev
    privileged: true

  axonstream:
    image: axonos/axonstream:latest
    restart: unless-stopped
    ports:
      - "50051:50051"
    environment:
      - DATABASE_URL=postgres://axonos:${DB_PASSWORD}@db:5432/axonos
      - REDIS_URL=redis://redis:6379

  axonml:
    image: axonos/axonml:latest
    restart: unless-stopped
    ports:
      - "50052:50052"
    environment:
      - MODEL_PATH=/models
      - CUDA_VISIBLE_DEVICES=0

  axonnet:
    image: axonos/axonnet:latest
    restart: unless-stopped
    ports:
      - "80:8080"
      - "443:8443"
    environment:
      - TLS_CERT_PATH=/certs/server.crt
      - TLS_KEY_PATH=/certs/server.key

  db:
    image: timescale/timescaledb:latest-pg14
    restart: unless-stopped
    environment:
      POSTGRES_DB: axonos
      POSTGRES_USER: axonos
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
```

### Kubernetes Deployment

```yaml
# k8s/axonos-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: axonos-core
  labels:
    app: axonos
spec:
  replicas: 3
  selector:
    matchLabels:
      app: axonos-core
  template:
    metadata:
      labels:
        app: axonos-core
    spec:
      containers:
      - name: axoncore
        image: axonos/axoncore:latest
        ports:
        - containerPort: 50051
        env:
        - name: RUST_LOG
          value: "info"
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
      - name: axonstream
        image: axonos/axonstream:latest
        ports:
        - containerPort: 50052
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: axonos-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: axonos-service
spec:
  selector:
    app: axonos
  ports:
  - name: grpc
    port: 50051
    targetPort: 50051
  - name: http
    port: 8080
    targetPort: 8080
  type: LoadBalancer
```

### Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"

volumes:
  prometheus_data:
  grafana_data:
```

---

## Troubleshooting

### Common Issues

#### 1. Device Connection Failed

```bash
# Check device permissions
ls -la /dev/ttyUSB*

# Add user to dialout group
sudo usermod -a -G dialout $USER

# Test device connection
axonos device test --device openbci_cyton_001
```

#### 2. High Latency

```bash
# Check CPU usage
htop

# Check memory usage
free -h

# Profile application
cargo flamegraph --bin axonstream

# Optimize buffer sizes
export AXON_BUFFER_SIZE=1024
export AXON_BATCH_SIZE=32
```

#### 3. Model Loading Failed

```bash
# Check model file
ls -la /models/motor_imagery_cnn.onnx

# Validate ONNX model
python -c "import onnx; onnx.checker.check_model('model.onnx')"

# Check dependencies
pip list | grep onnx
```

#### 4. Authentication Issues

```bash
# Check JWT token
echo $AXONOS_TOKEN | jwt decode -

# Test authentication
curl -H "Authorization: Bearer $AXONOS_TOKEN" \
     https://api.axonos.io/api/v1/auth/verify

# Refresh token
axonos auth refresh
```

### Debug Mode

```bash
# Enable debug logging
export RUST_LOG=debug
export PYTHONPATH=/app

# Run with debugger
cargo run --bin axoncore -- --debug
gdb target/debug/axoncore

# Python debugging
python -m pdb my_script.py
```

### Performance Profiling

```bash
# Rust profiling
cargo install flamegraph
cargo flamegraph --bin axonstream

# Python profiling
python -m cProfile -o profile.prof my_script.py
python -m pstats profile.prof

# System profiling
perf record -g ./axoncore
perf report
```

---

## Support

### Getting Help

- **Documentation**: https://docs.axonos.io
- **GitHub Issues**: https://github.com/axonos/axonos/issues
- **Community Forum**: https://community.axonos.io
- **Discord**: https://discord.gg/axonos

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

*Version: 1.0*  
*Last updated: 2026-01-17*
