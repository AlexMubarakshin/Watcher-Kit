#!/bin/bash

# Install Person Detection Dependencies
echo "🤖 Installing Person Detection dependencies..."

# Activate virtual environment
source .venv/bin/activate

# Install computer vision packages
echo "📦 Installing OpenCV and YOLOv8..."
pip install opencv-python ultralytics numpy

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
