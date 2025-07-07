#!/bin/bash

# Install Person Detection Dependencies
echo "🤖 Installing Person Detection dependencies..."

# Check if LZMA module is available
echo "🔍 Checking Python environment..."
python3 -c "import _lzma; print('✅ LZMA module available')" 2>/dev/null || {
    echo "❌ LZMA module not available - this will cause issues"
    echo "💡 Run enhanced setup: ./setup_enhanced_python.sh"
    echo "💡 Or run diagnostics: ./diagnose_python.py"
    echo ""
    echo "⚠️ Continuing anyway, but expect potential failures..."
}

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    echo "💡 Run: python3 -m venv .venv && source .venv/bin/activate"
    exit 1
fi

# Install computer vision packages
echo "📦 Installing OpenCV and YOLOv8..."

# Install with better error handling
pip install opencv-python-headless ultralytics numpy torch torchvision || {
    echo "❌ Installation failed"
    echo "💡 Try the enhanced setup: ./setup_enhanced_python.sh"
    exit 1
}

# Test the installation
echo "🧪 Testing installation..."
python3 -c "
try:
    import cv2
    print('✅ OpenCV imported successfully')
except Exception as e:
    print(f'❌ OpenCV import failed: {e}')

try:
    from ultralytics import YOLO
    print('✅ YOLOv8 imported successfully')
except Exception as e:
    print(f'❌ YOLOv8 import failed: {e}')
    if '_lzma' in str(e):
        print('💡 This is an LZMA issue - run: ./setup_enhanced_python.sh')
"

echo "✅ Person Detection dependencies installed!"

echo ""
echo "🎯 To enable person detection:"
echo "  1. Edit .env file: ENABLE_PERSON_DETECTION=true"
echo "  2. Run normal video capture: watcher-capture"
echo "  3. Detection will run automatically alongside video recording"
echo ""
echo "🧪 To test person detection:"
echo "  python test_person_detection.py"
echo ""
echo "⚠️ Note: The first run will download the YOLOv8 model (~6MB)"
echo "💡 If you encounter LZMA errors, run: ./setup_enhanced_python.sh"
