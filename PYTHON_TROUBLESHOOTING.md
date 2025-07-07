# Python Environment Troubleshooting

This document addresses common Python environment issues encountered with the Watcher system, particularly the `No module named '_lzma'` error.

## Common Error: `No module named '_lzma'`

### What is this error?

The `_lzma` module is part of Python's standard library and provides LZMA compression support. This error typically occurs when:

1. **System Python on macOS**: The built-in Python on macOS often has missing modules
2. **Incomplete Python build**: Python was compiled without LZMA support
3. **Missing system libraries**: Required compression libraries weren't available during Python compilation

### Quick Diagnosis

Run our diagnostic script:
```bash
./diagnose_python.py
```

This will check your Python environment and identify specific issues.

### Solutions (in order of recommendation)

#### 1. Enhanced Setup Script (Recommended)

Our enhanced setup script automatically detects and fixes most issues:

```bash
./setup_enhanced_python.sh
```

This script:
- Detects LZMA issues
- Installs proper Python via Homebrew if needed
- Sets up a clean virtual environment
- Installs all dependencies with proper error handling
- Tests everything to ensure it works

#### 2. Manual Homebrew Installation

Install Python via Homebrew (includes all required modules):

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Create new virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
./install_person_detection.sh
```

#### 3. Using pyenv

Install a proper Python version using pyenv:

```bash
# Install pyenv (if not already installed)
brew install pyenv

# Install Python
pyenv install 3.11.7
pyenv global 3.11.7

# Reload shell
exec "$SHELL"

# Create new virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
./install_person_detection.sh
```

#### 4. Using Conda

If you prefer Conda:

```bash
# Install Miniconda (if not already installed)
# Download from: https://docs.conda.io/en/latest/miniconda.html

# Create conda environment
conda create -n watcher python=3.11
conda activate watcher

# Install dependencies
pip install opencv-python-headless ultralytics torch torchvision
```

#### 5. Disable Person Detection

If you can't resolve the Python issues, disable person detection:

In your `.env` file:
```bash
ENABLE_PERSON_DETECTION=false
```

The system will work normally without person detection features.

## Other Common Issues

### OpenCV Import Errors

**Error**: `ImportError: No module named 'cv2'`

**Solution**:
```bash
pip install opencv-python-headless
```

### PyTorch/YOLO Issues

**Error**: Various PyTorch or ultralytics errors

**Solution**:
```bash
# For Apple Silicon Macs
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# For Intel Macs
pip install torch torchvision

# Then install YOLO
pip install ultralytics
```

### Permission Errors

**Error**: Permission denied when installing packages

**Solutions**:
1. Use virtual environment (recommended)
2. Use `--user` flag: `pip install --user package_name`
3. Use `sudo` (not recommended): `sudo pip install package_name`

### Virtual Environment Issues

**Error**: Virtual environment not activating or not found

**Solution**:
```bash
# Remove old environment
rm -rf .venv

# Create new environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV
```

## Environment Verification

After fixing issues, verify your environment:

```bash
# Test basic functionality
python3 test_yolo_model.py

# Full diagnostic
./diagnose_python.py

# Test person detection
python3 test_person_detection.py
```

## Which Python Should I Use?

### ✅ Recommended Python Sources

1. **Homebrew** (`brew install python`)
   - Complete, well-maintained
   - Includes all standard library modules
   - Easy to manage

2. **pyenv** (`pyenv install 3.11.7`)
   - Multiple Python versions
   - Clean installations
   - Good for development

3. **Conda** (`conda install python`)
   - Scientific computing focused
   - Excellent package management
   - Good for ML/AI projects

### ❌ Avoid These Python Sources

1. **System Python** (`/usr/bin/python3`)
   - Often missing modules
   - Hard to modify
   - May break system tools

2. **Python.org installer** (sometimes)
   - May have missing optional modules
   - Depends on system libraries

## macOS Specific Notes

### Apple Silicon (M1/M2) Macs

- Use Homebrew for best compatibility
- Some packages may need specific versions
- PyTorch has special Apple Silicon builds

### Intel Macs

- Most packages work without issues
- Standard PyTorch installations work

### System Integrity Protection (SIP)

macOS SIP may prevent modifications to system Python. This is another reason to use Homebrew or pyenv.

## Getting Help

If you're still having issues:

1. **Run diagnostics**: `./diagnose_python.py`
2. **Check logs**: Look at the specific error messages
3. **Try enhanced setup**: `./setup_enhanced_python.sh`
4. **Disable feature**: Set `ENABLE_PERSON_DETECTION=false`

## Technical Details

### Why LZMA Matters

The LZMA module is used by:
- PyTorch for model serialization
- Various data compression tasks
- Package management tools

### Building Python with LZMA

If you need to build Python from source with LZMA support:

```bash
# Install required libraries (macOS)
brew install xz

# When building Python, ensure xz-dev is available
# Python's configure script will detect and include LZMA support
```

### Virtual Environment Best Practices

1. Always use virtual environments for Python projects
2. Name them descriptively (`.venv` for project-specific)
3. Recreate if you have persistent issues
4. Keep requirements.txt updated

This comprehensive troubleshooting should resolve most Python environment issues you encounter with the Watcher system.
