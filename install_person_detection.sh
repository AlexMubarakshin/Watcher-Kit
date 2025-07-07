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
echo "🚀 To test person detection:"
echo "  python person_detect.py --test --preview"
echo ""
echo "🎯 To run person detection:"
echo "  python person_detect.py --duration 30 --preview"
echo ""
echo "📋 Available options:"
echo "  --duration X     Run for X minutes (default: 60)"
echo "  --preview        Show live preview window" 
echo "  --confidence X   Detection confidence 0.0-1.0 (default: 0.5)"
echo "  --cooldown X     Seconds between alerts (default: 10)"
echo "  --test           Test mode - single detection and exit"
echo ""
echo "⚠️ Note: The first run will download the YOLOv8 model (~6MB)"
