# AxonOS

Sovereign AI Operating System for Humans.

## Overview
AxonOS is a privacy-first AI operating system designed for future human-computer interaction.

## Architecture
See docs/architecture.md

## Status
Early architecture stage.

## Roadmap
See docs/roadmap.md


# 🛠️ Tech Stack & Dependencies

Our architecture consists of four distinct layers designed for modularity, security, and performance.

| Layer | Packages | Purpose |
| :--- | :--- | :--- |
| Core Engine | NumPy, SciPy, PyTorch | Signal processing & Neural computation |
| Security & Logic | Cryptography, BCrypt, Pydantic | Zero-trust encryption & strict typing |
| Hardware IO | BrainFlow, PyLSL, PySerial | Real-time device streaming |
| Interface (API) | FastAPI, Uvicorn, SQLAlchemy | High-performance async gateway |

> Dev Tools: Pytest, Ruff, MyPy, Pre-commit are required for contributors.

---

## 🐳 Deployment

AxonOS is container-native. Deploy the secure protocol in seconds.

### Build & Run
`bash
# 1. Build the hardened image
docker build -t axonos:latest .

# 2. Launch the protocol (exposed on port 8000)
docker run -d \
  --name axonos_core \
  --restart unless-stopped \
  -p 8000:8000 \
  axonos:latest
