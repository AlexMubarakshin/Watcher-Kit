#!/bin/bash

# Enhanced Python Environment Setup for Watcher
# Addresses common issues like missing LZMA module

set -e

echo "🔧 Enhanced Python Environment Setup for Watcher"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python LZMA support
check_lzma() {
    python3 -c "import _lzma; print('✅ LZMA module available')" 2>/dev/null || {
        echo "❌ LZMA module not available"
        return 1
    }
}

echo "🔍 Checking current Python environment..."

# Check current Python
echo "📍 Current Python: $(which python3)"
echo "📍 Python version: $(python3 --version)"

# Test LZMA availability
if check_lzma; then
    echo "✅ Current Python supports LZMA"
    PYTHON_OK=true
else
    echo "❌ Current Python missing LZMA support"
    PYTHON_OK=false
fi

# If LZMA is missing, suggest better Python installation
if [ "$PYTHON_OK" = false ]; then
    echo ""
    echo "🚨 LZMA Module Issue Detected"
    echo "============================="
    echo "The current Python installation is missing the LZMA module."
    echo "This is common with system Python on macOS."
    echo ""
    
    # Check for Homebrew
    if command_exists brew; then
        echo "✅ Homebrew detected"
        echo "💡 Installing Python via Homebrew (recommended)..."
        
        # Install Python via Homebrew
        brew install python@3.11 || {
            echo "⚠️ Homebrew Python installation failed, trying alternative..."
        }
        
        # Update PATH for current session
        if [ -d "/opt/homebrew/bin" ]; then
            export PATH="/opt/homebrew/bin:$PATH"
        elif [ -d "/usr/local/bin" ]; then
            export PATH="/usr/local/bin:$PATH"
        fi
        
        # Test again
        echo "🔄 Testing Homebrew Python..."
        if command_exists python3 && check_lzma; then
            echo "✅ Homebrew Python with LZMA support is now available"
            PYTHON_OK=true
        fi
        
    else
        echo "❌ Homebrew not found"
        echo "💡 Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [ -d "/opt/homebrew/bin" ]; then
            echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
            export PATH="/opt/homebrew/bin:$PATH"
        fi
        
        echo "💡 Installing Python via Homebrew..."
        brew install python@3.11
        
        # Test again
        if check_lzma; then
            echo "✅ Homebrew Python with LZMA support is now available"
            PYTHON_OK=true
        fi
    fi
fi

# If still having issues, try pyenv
if [ "$PYTHON_OK" = false ] && command_exists pyenv; then
    echo ""
    echo "🔄 Trying pyenv Python installation..."
    pyenv install 3.11.7 -s  # -s = skip if already installed
    pyenv global 3.11.7
    
    # Reload shell
    eval "$(pyenv init -)"
    
    if check_lzma; then
        echo "✅ pyenv Python with LZMA support is now available"
        PYTHON_OK=true
    fi
fi

# Final check
if [ "$PYTHON_OK" = false ]; then
    echo ""
    echo "❌ Unable to resolve LZMA issue automatically"
    echo "💡 Manual solutions:"
    echo "   1. Install Python via Homebrew: brew install python@3.11"
    echo "   2. Use pyenv: pyenv install 3.11.7 && pyenv global 3.11.7"
    echo "   3. Use conda: conda install python=3.11"
    echo "   4. Disable person detection: ENABLE_PERSON_DETECTION=false in .env"
    echo ""
    echo "🔍 Run ./diagnose_python.py for detailed diagnostics"
    exit 1
fi

echo ""
echo "✅ Python environment is ready!"
echo "📍 Using Python: $(which python3)"

# Continue with virtual environment setup
echo ""
echo "🏗️ Setting up virtual environment..."

# Remove old virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🧹 Removing old virtual environment..."
    rm -rf .venv
fi

# Create new virtual environment
echo "📦 Creating new virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Verify we're in virtual environment
if [ "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Test LZMA in virtual environment
if check_lzma; then
    echo "✅ LZMA support confirmed in virtual environment"
else
    echo "❌ LZMA still not available in virtual environment"
    echo "💡 This suggests a fundamental Python installation issue"
    exit 1
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "📦 Installing core dependencies..."
pip install requests python-dotenv

# Install OpenCV with proper handling
echo "📦 Installing OpenCV..."
pip install opencv-python-headless

# Install PyTorch (required for YOLO)
echo "📦 Installing PyTorch..."
if [[ $(uname -m) == "arm64" ]]; then
    # Apple Silicon
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
else
    # Intel Mac
    pip install torch torchvision
fi

# Install YOLOv8
echo "📦 Installing YOLOv8 (ultralytics)..."
pip install ultralytics

# Install additional dependencies
echo "📦 Installing additional dependencies..."
pip install Pillow numpy

# Test installations
echo ""
echo "🧪 Testing installations..."

python3 -c "
import sys
print(f'✅ Python: {sys.version}')

try:
    import _lzma
    print('✅ LZMA module')
except ImportError as e:
    print(f'❌ LZMA module: {e}')

try:
    import cv2
    print(f'✅ OpenCV: {cv2.__version__}')
except ImportError as e:
    print(f'❌ OpenCV: {e}')

try:
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
except ImportError as e:
    print(f'❌ PyTorch: {e}')

try:
    from ultralytics import YOLO
    print('✅ YOLOv8 (ultralytics)')
except ImportError as e:
    print(f'❌ YOLOv8: {e}')

try:
    import requests
    print('✅ Requests')
except ImportError as e:
    print(f'❌ Requests: {e}')
"

# Download YOLO model
echo ""
echo "📦 Downloading YOLO model..."
./download_yolo_model.sh

# Final test
echo ""
echo "🎯 Final test..."
python3 test_yolo_model.py

echo ""
echo "🎉 Enhanced setup complete!"
echo "💡 To activate this environment in the future:"
echo "   source .venv/bin/activate"
echo ""
echo "🔍 If you encounter issues, run: ./diagnose_python.py"
