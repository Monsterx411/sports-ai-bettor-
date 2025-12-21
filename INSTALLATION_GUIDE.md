# Installation & Deployment Guide

## Quick Start Installation

### System Requirements
- Python 3.8+ (3.11+ recommended)
- pip or conda package manager
- 2GB+ disk space
- Internet connection for downloading dependencies

### Operating Systems Supported
✅ macOS (Intel & Apple Silicon)
✅ Linux (Ubuntu, Debian, CentOS, etc.)
✅ Windows 10/11

---

## Installation Methods

### Method 1: Standard pip Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/Monsterx411/sports-ai-bettor.git
cd sports-ai-bettor

# Install in development mode
pip install -e .

# Or production install
pip install .
```

### Method 2: With All Development Tools

```bash
pip install -e ".[dev,test,viz]"
```

### Method 3: Conda Installation

```bash
# Create environment
conda create -n sports-ai python=3.11

# Activate environment
conda activate sports-ai

# Install package
pip install -e .
```

### Method 4: Docker Installation (Coming Soon)

```bash
docker build -t sports-ai-bettor .
docker run -it sports-ai-bettor
```

---

## Installation Profiles

Choose based on your use case:

### Development Setup
```bash
pip install -e ".[dev,test,docs,viz]"
```
Includes: Testing, linting, formatting, type checking, documentation

### Production Deployment
```bash
pip install -e ".[prod]"
```
Includes: Optimized dependencies for production

### Data Science Work
```bash
pip install -e ".[viz,test]"
```
Includes: Visualization and analysis tools

### Minimal Installation
```bash
pip install .
```
Core dependencies only

### Full Installation (All Features)
```bash
pip install -e ".[all]"
```
Everything: dev, test, docs, viz, prod

---

## Post-Installation Setup

### 1. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
```
API_SPORTS_KEY=your_api_key_here
ODDS_API_KEY=your_odds_api_key_here
ENVIRONMENT=development
DEBUG=false
```

### 2. Initialize Data Directories

```bash
# Create data structure (done automatically, but verify)
python -c "from config.settings import settings; print('✅ Directories created')"
```

### 3. Download Training Data

```bash
# Prepare enhanced training dataset
python enhanced_data_pipeline.py
```

### 4. Train Initial Models

```bash
# Train models
python train_enhanced.py
```

---

## Verification

### Test Installation

```bash
# Check version
python -c "import sports_ai_bettor; print(sports_ai_bettor.__version__)"

# Check CLI
sports-ai-bettor --help

# Or use shorthand
sab --help

# Display settings
sports-ai-bettor settings-cmd
```

### Run Test Suite

```bash
# If installed with [test]
pytest

# With coverage
pytest --cov=src tests/

# Verbose output
pytest -v tests/
```

### Test Predictions

```bash
sports-ai-bettor predict --model-name sports_model 0.75 0.70 0.55 2 9 5 60 40
```

---

## System-Wide Installation

### Install as System Package (macOS/Linux)

```bash
# Install to system Python
sudo pip install .

# Or use specific Python version
python3.11 -m pip install --user .

# Verify installation
which sports-ai-bettor
sports-ai-bettor --version
```

### Make Available Globally

```bash
# Add to PATH (if not already)
export PATH="$PATH:/usr/local/bin"

# Or create symlink (if using system-wide)
sudo ln -s /path/to/sports-ai-bettor /usr/local/bin/sab
```

---

## Virtual Environment Setup (Recommended)

### Using venv

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Install package
pip install -e ".[all]"
```

### Using conda

```bash
# Create environment
conda create -n sports-ai python=3.11 -y

# Activate
conda activate sports-ai

# Install package
pip install -e ".[all]"
```

### Using pyenv (macOS)

```bash
# Install specific Python version
pyenv install 3.11.0

# Create local environment
pyenv local 3.11.0

# Install virtual environment
python -m venv venv
source venv/bin/activate

# Install package
pip install -e ".[all]"
```

---

## Troubleshooting

### Issue: "Command not found: sports-ai-bettor"

**Solution:**
```bash
# Check installation
pip list | grep sports-ai-bettor

# Reinstall
pip install --force-reinstall -e .

# Check PATH
echo $PATH
which python
```

### Issue: "ModuleNotFoundError: No module named 'sklearn'"

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or reinstall package
pip install --force-reinstall -e .
```

### Issue: "Python version too old"

**Solution:**
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m pip install -e .

# Or create virtual environment with correct version
pyenv install 3.11.0
pyenv local 3.11.0
```

### Issue: Permission denied (macOS/Linux)

**Solution:**
```bash
# Use --user flag
pip install --user -e .

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Issue: "setup.py not found"

**Solution:**
```bash
# Verify you're in project root
ls setup.py

# Install from correct directory
cd sports-ai-bettor
pip install -e .
```

---

## Uninstallation

```bash
# Remove package
pip uninstall sports-ai-bettor

# Remove virtual environment (if using venv)
rm -rf venv

# Remove conda environment (if using conda)
conda remove --name sports-ai --all
```

---

## Development Setup

### Clone and Setup for Development

```bash
# Clone repository
git clone https://github.com/Monsterx411/sports-ai-bettor.git
cd sports-ai-bettor

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with development tools
pip install -e ".[dev,test,docs,viz]"

# Setup pre-commit hooks (optional)
pre-commit install

# Verify setup
pytest
black --check .
flake8 .
mypy src/
```

### Running Development Commands

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type check
mypy src/

# Run tests
pytest -v

# Generate coverage report
pytest --cov=src tests/
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -e ".[prod]"

EXPOSE 8501

CMD ["streamlit", "run", "web_app.py"]
```

### AWS/Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment instructions.

---

## Support & Documentation

- **Documentation:** [GitHub README](https://github.com/Monsterx411/sports-ai-bettor)
- **Issues:** [Bug Reports](https://github.com/Monsterx411/sports-ai-bettor/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Monsterx411/sports-ai-bettor/discussions)

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version information.

---

**Last Updated:** December 20, 2025
**Status:** ✅ Production Ready
