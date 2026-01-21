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
mkdir -p AxonOS/{.github/workflows,config,docs/{architecture,api,guides},scripts,logs}
mkdir -p AxonOS/src/axonos/{core/{signal,ml,pipeline},security,protocol,hardware,api/{routes,websockets,middleware}}
mkdir -p AxonOS/tests/{unit/{core,security,protocol,hardware,api},integration,e2e}
mkdir -p AxonOS/examples/{basic,advanced,realtime}

print_status 0 "Directory structure created"

# 2. Navigate to project
cd AxonOS

# 3. Create Base Files
echo -e "\n${YELLOW}2. Creating base files...${NC}"
touch .env.example Dockerfile docker-compose.yml README.md
touch docs/CONTRIBUTING.md docs/CHANGELOG.md
touch scripts/{setup_dev.sh,run_tests.sh,build_docker.sh}

print_status 0 "Base files created"

# 4. Create Python Packages (init.py)
echo -e "\n${YELLOW}3. Creating Python package structure...${NC}"
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;

print_status 0 "Python packages initialized"

# 5. Create Requirements Files
echo -e "\n${YELLOW}4. Creating requirements files...${NC}"

# Core requirements
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

# Hardware requirements
cat <<'EOF' > requirements-hardware.txt
brainflow>=5.10.0
pylsl>=1.16.2
pyserial>=3.5
EOF

# API requirements
cat <<'EOF' > requirements-api.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
SQLAlchemy>=2.0.0
alembic>=1.13.0
EOF

# Dev requirements
cat <<'EOF' > requirements-dev.txt
pytest>=8.0.0
ruff>=0.3.0
mypy>=1.8.0
pre-commit>=3.6.0
EOF

# Meta-requirement file
cat <<'EOF' > requirements.txt
-r requirements-core.txt
-r requirements-hardware.txt
-r requirements-api.txt
EOF

print_status 0 "Requirements files created"

# 6. Create Modern Config
echo -e "\n${YELLOW}5. Creating pyproject.toml...${NC}"
cat <<'EOF' > pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "axonos"
version = "2.1.0"
description = "Secure Privacy-First BCI Protocol"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "AxonOS Team", email = "team@axonos.org"},
]

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["src"]
EOF

print_status 0 "pyproject.toml created"

# 7. Create Gitignore
echo -e "\n${YELLOW}6. Creating .gitignore...${NC}"
cat <<'EOF' > .gitignore
__pycache__/
*.pyc
.env
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
build/
.DS_Store
.idea/
.vscode/
*.swp
*.swo
logs/
*.neuraldata
vault/
*.key
EOF

print_status 0 ".gitignore created"

# 8. Create Placeholders for Key Modules
echo -e "\n${YELLOW}7. Creating key module placeholders...${NC}"
touch src/axonos/security/vault.py
touch src/axonos/security/encryption.py
touch src/axonos/hardware/abstract.py
touch src/axonos/api/main.py

print_status 0 "Key module placeholders created"

# 9. Create README
echo -e "\n${YELLOW}8. Creating README.md...${NC}"
cat <<'EOF' > README.md
# AxonOS

Secure Privacy-First BCI Protocol

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start development server
make run-dev
```
EOF

print_status 0 "README.md created"

# 10. Create Makefile
echo -e "\n${YELLOW}9. Creating Makefile...${NC}"
cat <<'EOF' > Makefile
.PHONY: install test lint run clean help

install:
	pip install -r requirements.txt

test:
	pytest tests/

lint:
	ruff check src/
	mypy src/ --ignore-missing-imports

run:
	cd src && uvicorn axonos.api.main:app --host 0.0.0.0 --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

help:
	@echo "Available commands: install, test, lint, run, clean"
EOF

print_status 0 "Makefile created"

# 11. Create Dockerfile
echo -e "\n${YELLOW}10. Creating Dockerfile...${NC}"
cat <<'EOF' > Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY pyproject.toml /app/

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "axonos.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

print_status 0 "Dockerfile created"

# 12. Create Docker Compose
echo -e "\n${YELLOW}11. Creating docker-compose.yml...${NC}"
cat <<'EOF' > docker-compose.yml
version: '3.8'

services:
  axonos:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AXONOS_MASTER_KEY=${AXONOS_MASTER_KEY}
    volumes:
      - ./logs:/app/logs
EOF

print_status 0 "docker-compose.yml created"

# 13. Create .env.example
echo -e "\n${YELLOW}12. Creating .env.example...${NC}"
cat <<'EOF' > .env.example
AXONOS_MASTER_KEY=your-secure-master-key-here
AXONOS_API_HOST=0.0.0.0
AXONOS_API_PORT=8000
DATABASE_URL=sqlite:///./axonos.db
LOG_LEVEL=INFO
EOF

print_status 0 ".env.example created"

# 14. Final message
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}🎉 AxonOS Architecture Initialized!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. cd AxonOS"
echo "2. python -m venv venv && source venv/bin/activate"
echo "3. pip install -r requirements.txt"
echo "4. make test"
echo ""
echo -e "${GREEN}Happy coding! 🧠${NC}"