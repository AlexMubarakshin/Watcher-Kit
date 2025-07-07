# YOLO Model Download Troubleshooting

This document provides solutions for common YOLO model download issues.

## Common Error

```
❌ Video analysis error: ❌ Download failure for https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt. Retry limit reached.
```

## Solutions

### 1. Automatic Download Script

Run the provided download script to manually download the model:

```bash
./download_yolo_model.sh
```

This script will:
- Download the YOLO model to `models/yolov8n.pt`
- Copy it to the ultralytics cache directory
- Work with both `wget` and `curl`

### 2. Manual Download

If the script fails, download manually:

```bash
# Create models directory
mkdir -p models

# Download with wget
wget -O models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt

# OR download with curl
curl -L -o models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
```

### 3. Copy to Cache Directory

Copy the model to ultralytics cache directory:

```bash
mkdir -p ~/.cache/ultralytics
cp models/yolov8n.pt ~/.cache/ultralytics/yolov8n.pt
```

### 4. Disable Person Detection

If you don't need person detection, disable it in `.env`:

```bash
ENABLE_PERSON_DETECTION=false
```

## Model Loading Priority

The system tries to load the model in this order:

1. **Ultralytics cache**: `~/.cache/ultralytics/yolov8n.pt`
2. **Local project**: `models/yolov8n.pt`
3. **Download**: Automatic download with 3 retry attempts
4. **Fallback**: Error with helpful suggestions

## Verification

After downloading, verify the model works:

```python
from ultralytics import YOLO
model = YOLO('models/yolov8n.pt')
print("✅ Model loaded successfully!")
```

## Network Issues

If you're behind a corporate firewall or have network restrictions:

1. Download the model on a different network
2. Transfer the file to your machine
3. Place it in `models/yolov8n.pt`

## File Size

The YOLOv8n model is approximately 6.2 MB. If your download is smaller, it may be corrupted.

## Alternative Models

You can also use other YOLO models by changing the filename:
- `yolov8s.pt` (11.2 MB) - Small model
- `yolov8m.pt` (25.9 MB) - Medium model
- `yolov8l.pt` (43.7 MB) - Large model
- `yolov8x.pt` (68.2 MB) - Extra large model

Update the model name in the code if using a different variant.
