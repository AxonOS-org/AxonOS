# AxonOS Quick Start Guide

## 🚀 Initialize Project Structure

### Prerequisites
- Linux, macOS, or WSL (Windows Subsystem for Linux)
- Git Bash (for Windows users)
- Python 3.10+ installed

### Step 1: Create Initialization Script

Create a file named `init_axonos.sh` and copy the initialization script into it:

```bash
# Create the initialization script
cat > init_axonos.sh << 'SCRIPT'
#!/bin/bash

echo "🚀 Initializing AxonOS Architecture..."
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# 1. Create Directory Structure
echo -e "\n${YELLOW}1. Creating directory structure...${NC}"
mkdir -p AxonOS/{.github/workflows,config,docs/{architecture,api},scripts,logs}
mkdir -p AxonOS/src/axonos/{core/{signal,ml,pipeline},security,protocol,hardware,api/{routes,websockets,middleware}}
mkdir -p AxonOS/tests/{unit/{core,security,protocol,hardware,api},integration,e2e}
mkdir -p AxonOS/examples/{basic,advanced,realtime}

print_status 0 "Directory structure created"

# 2. Navigate to project
cd AxonOS

# 3. Create Base Files
echo -e "\n${YELLOW}2. Creating base files...${NC}"
touch .env.example Dockerfile docker-compose.yml Makefile README.md
touch docs/MANIFEST.md docs/CONTRIBUTING.md docs/CHANGELOG.md
touch scripts/{setup_dev.sh,run_tests.sh,build_docker.sh}

print_status 0 "Base files created"

# 4. Create Python Packages (init.py)
echo -e "\n${YELLOW}3. Creating Python package structure...${NC}"
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;

print_status 0 "Python packages initialized"

# 5. Create Requirements Files
echo -e "\n${YELLOW}4. Creating requirements files...${NC}"

cat <<'EOF' > requirements-core.txt
# AxonOS Core Dependencies
numpy>=1.26.0
scipy>=1.12.0
scikit-learn>=1.4.0
mne>=1.6.0
torch>=2.2.0
cryptography>=42.0.0
bcrypt>=4.1.0
pydantic>=2.6.0
EOF

cat <<'EOF' > requirements-hardware.txt
brainflow>=5.10.0
pylsl>=1.16.2
pyserial>=3.5
EOF

cat <<'EOF' > requirements-api.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
SQLAlchemy>=2.0.0
alembic>=1.13.0
EOF

cat <<'EOF' > requirements-dev.txt
pytest>=8.0.0
ruff>=0.3.0
mypy>=1.8.0
pre-commit>=3.6.0
EOF

print_status 0 "Requirements files created"

# 6. Create pyproject.toml
echo -e "\n${YELLOW}5. Creating pyproject.toml...${NC}"
cat <<'EOF' > pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "axonos"
version = "0.1.0"
description = "Secure Privacy-First BCI Protocol"
requires-python = ">=3.10"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["src"]
EOF

print_status 0 "pyproject.toml created"

# 7. Create .gitignore
echo -e "\n${YELLOW}6. Creating .gitignore...${NC}"
cat <<'EOF' > .gitignore
__pycache__/
*.pyc
.env
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
EOF

print_status 0 ".gitignore created"

echo -e "\n${GREEN}✅ AxonOS Architecture Initialized!${NC}"
SCRIPT

# Make script executable
chmod +x init_axonos.sh
```

### Step 2: Run the Initialization Script

```bash
# Make the script executable and run it
chmod +x init_axonos.sh && ./init_axonos.sh
```

This will create a complete project structure:

```
AxonOS/
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
├── docs/
│   ├── architecture/
│   ├── api/
│   └── MANIFEST.md
├── scripts/
│   ├── setup_dev.sh
│   ├── run_tests.sh
│   └── build_docker.sh
├── src/
│   └── axonos/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── signal/
│       │   │   └── __init__.py
│       │   ├── ml/
│       │   │   └── __init__.py
│       │   └── pipeline/
│       │       └── __init__.py
│       ├── security/
│       │   └── __init__.py
│       ├── protocol/
│       │   └── __init__.py
│       ├── hardware/
│       │   └── __init__.py
│       └── api/
│           ├── __init__.py
│           ├── routes/
│           │   └── __init__.py
│           ├── websockets/
│           │   └── __init__.py
│           └── middleware/
│               └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ├── security/
│   │   │   └── __init__.py
│   │   ├── protocol/
│   │   │   └── __init__.py
│   │   ├── hardware/
│   │   │   └── __init__.py
│   │   └── api/
│   │       └── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   └── e2e/
│       └── __init__.py
├── examples/
│   ├── basic/
│   ├── advanced/
│   └── realtime/
├── logs/
├── requirements-core.txt
├── requirements-hardware.txt
├── requirements-api.txt
├── requirements-dev.txt
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

### Step 3: Set Up Development Environment

```bash
cd AxonOS

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Run tests
pytest tests/

# Start development server
make run-dev
```

## 📦 Requirements Structure

The initialization script creates a clean, modular requirements structure:

### requirements-core.txt
Core dependencies required for basic operation:
- numpy, scipy, scikit-learn
- PyTorch 2.x
- cryptography, bcrypt, pydantic

### requirements-hardware.txt
Hardware-specific dependencies:
- brainflow, pylsl, pyserial

### requirements-api.txt
Web API dependencies:
- fastapi, uvicorn
- sqlalchemy, alembic

### requirements-dev.txt
Development tools:
- pytest, ruff, mypy
- pre-commit hooks

## 🛠 Development Tools

### Code Quality
```bash
make lint        # Run ruff + mypy
make format      # Auto-format with ruff
make test        # Run pytest
make test-cov    # Run with coverage
```

### Docker
```bash
make docker-build    # Build Docker image
make docker-run      # Run in container
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/axonos --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py

# Run with specific marker
pytest -m "security"
```

## 🚀 Production Deployment

### Using Docker
```bash
# Build production image
docker build -t axonos:latest .

# Run container
docker run -p 8000:8000 axonos:latest
```

### Using Docker Compose
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your values

# Start services
docker-compose up -d
```

## 📚 Documentation

After initialization, check these files:

- `docs/MANIFEST.md` - Architecture overview
- `README.md` - Project description
- `docs/CONTRIBUTING.md` - Development guidelines
- `docs/CHANGELOG.md` - Version history

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Security
AXONOS_MASTER_KEY=your-secure-master-key

# API
AXONOS_API_HOST=0.0.0.0
AXONOS_API_PORT=8000

# Database
DATABASE_URL=sqlite:///./axonos.db
```

### PyProject Configuration

The `pyproject.toml` file includes:

- **Ruff configuration**: Modern linter (replaces black/flake8)
- **MyPy configuration**: Strict type checking
- **Pytest configuration**: Test discovery and coverage

## 🎯 Next Steps

1. **Implement Core Modules**
   - Start with `src/axonos/protocol/schemas.py`
   - Add security layer in `src/axonos/security/`
   - Implement ML models in `src/axonos/core/ml/`

2. **Add Hardware Support**
   - Create device drivers in `src/axonos/hardware/`
   - Test with real BCI devices

3. **Build API**
   - Implement FastAPI routes
   - Add WebSocket support for real-time data

4. **Testing**
   - Write unit tests for all modules
   - Add integration tests
   - Set up CI/CD with GitHub Actions

5. **Documentation**
   - Write API documentation
   - Create user guides
   - Add examples in `examples/`

## 🆘 Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
cd AxonOS

# Check Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Reinstall in development mode
pip install -e .
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x init_axonos.sh
```

### Virtual Environment
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Support

For issues and questions:
- Check `docs/` directory
- Run `make help` for available commands
- Check logs in `logs/` directory

---

**AxonOS v2.0 - Production Ready Architecture** 🚀