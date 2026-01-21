# Getting Started Guide

## Prerequisites

- Python 3.10 or higher
- Linux, macOS, or WSL (Windows Subsystem for Linux)
- Git

## Installation

### 1. Clone and Setup

```bash
# Navigate to implementation
cd Phase3_Implementation

# Initialize project
./init_axonos.sh

# Navigate to created project
cd AxonOS
```

### 2. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Install Package

```bash
# Install in development mode
pip install -e .
```

## First Steps

### 1. Run Tests

```bash
# Run all tests
pytest tests/

# Or use the test script
python ../test_new_architecture.py
```

### 2. Try Basic Example

```bash
# Run basic example
python examples/basic/basic_usage.py
```

### 3. Explore Advanced Features

```bash
# Run advanced ML example
python examples/advanced/advanced_ml.py

# Run real-time streaming example
python examples/realtime/realtime_streaming.py
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
AXONOS_MASTER_KEY=your-secure-master-key-here
AXONOS_API_HOST=0.0.0.0
AXONOS_API_PORT=8000
DATABASE_URL=sqlite:///./axonos.db
```

### Security Setup

```python
import os
from axonos.security.vault import NeuralDataVault

# Set master key
os.environ['AXONOS_MASTER_KEY'] = 'your-secure-key'

# Initialize vault
vault = NeuralDataVault()
```

## Basic Usage

### 1. Create Neural Packet

```python
from axonos.protocol.schemas import NeuralPacket, DeviceInfo, SignalData

# Device info
device = DeviceInfo(
    device_id="openbci_001",
    device_type="OpenBCI",
    model="Cyton",
    num_channels=8,
    sampling_rate=250
)

# Signal data
signal = SignalData(
    data=[0.1, 0.2, 0.3] * 100,
    channels=["C3", "C4", "Cz"],
    sampling_rate=250,
    duration_seconds=1.0,
    quality="good"
)

# Create packet
packet = NeuralPacket(
    packet_id="unique_packet_id",
    device_info=device,
    signal_data=signal
)
```

### 2. Process with ML

```python
from axonos.core.ml import ModelFactory, InferenceEngine
from axonos.core.ml.inference import InferenceConfig, SignalType

# Create model
factory = ModelFactory()
model = factory.create_lstm_model()

# Setup inference
config = InferenceConfig(signal_type=SignalType.MOTOR_IMAGERY)
engine = InferenceEngine(config, model)

# Process signal
result = engine.process(signal_data)
print(f"Prediction: {result.prediction}, Confidence: {result.confidence}")
```

### 3. Apply Security

```python
from axonos.security.vault import NeuralDataVault, SecurityConfig

vault = NeuralDataVault(config=SecurityConfig(zero_knowledge_mode=True))

# Encrypt
encrypted, data_id = vault.encrypt_neural_data(data)

# Decrypt
decrypted, metadata = vault.decrypt_neural_data(encrypted, data_id)
```

## Development Workflow

### 1. Make Changes

Edit code in `src/axonos/` following the module structure.

### 2. Test Changes

```bash
# Run tests
make test

# Run linting
make lint

# Check formatting
make format
```

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commits
git commit -m "feat: add new feature"

# Push
git push
```

## Troubleshooting

### Import Errors

```bash
# Ensure correct Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Reinstall package
pip install -e .
```

### Permission Errors

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Virtual Environment Issues

```bash
# Recreate venv
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. **Read the documentation** in `docs/`
2. **Explore examples** in `examples/`
3. **Check architecture** in `ARCHITECTURE_AUDIT_REPORT.md`
4. **Start building** your own modules!

## Getting Help

- Check `docs/` directory
- Run `make help` for commands
- Review examples in `examples/`
- Read architecture documentation