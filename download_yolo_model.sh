#!/bin/bash

# Download YOLO model script for offline use
# This helps when automatic download fails due to network issues

set -e

echo "🤖 YOLO Model Download Script"
echo "=============================="

# Create models directory
MODELS_DIR="$(dirname "$0")/models"
mkdir -p "$MODELS_DIR"

echo "📁 Created models directory: $MODELS_DIR"

# Download YOLOv8n model
MODEL_URL="https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt"
MODEL_PATH="$MODELS_DIR/yolov8n.pt"

if [ -f "$MODEL_PATH" ]; then
    echo "✅ Model already exists: $MODEL_PATH"
    echo "📏 File size: $(du -h "$MODEL_PATH" | cut -f1)"
else
    echo "📦 Downloading YOLO model..."
    echo "🔗 URL: $MODEL_URL"
    echo "💾 Destination: $MODEL_PATH"
    
    if command -v wget >/dev/null 2>&1; then
        wget -O "$MODEL_PATH" "$MODEL_URL"
    elif command -v curl >/dev/null 2>&1; then
        curl -L -o "$MODEL_PATH" "$MODEL_URL"
    else
        echo "❌ Error: Neither wget nor curl found"
        echo "💡 Please install wget or curl, or download manually:"
        echo "   $MODEL_URL"
        exit 1
    fi
    
    if [ -f "$MODEL_PATH" ]; then
        echo "✅ Download successful!"
        echo "📏 File size: $(du -h "$MODEL_PATH" | cut -f1)"
    else
        echo "❌ Download failed"
        exit 1
    fi
fi

# Also try to copy to ultralytics cache directory
CACHE_DIR="$HOME/.cache/ultralytics"
CACHE_PATH="$CACHE_DIR/yolov8n.pt"

mkdir -p "$CACHE_DIR"

if [ -f "$MODEL_PATH" ] && [ ! -f "$CACHE_PATH" ]; then
    echo "💾 Copying to ultralytics cache directory..."
    cp "$MODEL_PATH" "$CACHE_PATH"
    echo "✅ Cached at: $CACHE_PATH"
fi

echo ""
echo "🎉 YOLO model setup complete!"
echo "💡 The model will now load faster and work offline."
