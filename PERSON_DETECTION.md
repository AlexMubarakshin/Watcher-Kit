# Person Detection Feature

The Watcher system includes an AI-powered person detection feature that runs **integrated with video capture**. This means you can record video while simultaneously detecting people and sending alerts to Telegram - all using the same camera stream efficiently.

## Features

- 🤖 **AI-Powered Detection**: Uses YOLOv8 for accurate person detection
- 📸 **Smart Screenshots**: Automatically captures and annotates images when people are detected
- 📱 **Telegram Alerts**: Sends detection alerts with screenshots to your Telegram chat
- ⚡ **Integrated Processing**: Runs alongside video capture using the same camera
- 🎯 **Configurable Sensitivity**: Adjustable confidence thresholds
- 🕐 **Smart Cooldowns**: Prevents spam by limiting alert frequency
- 🧹 **Auto Cleanup**: Automatically removes old screenshots

## Installation

1. **Install Dependencies**:
   ```bash
   ./install_person_detection.sh
   ```

2. **Download YOLO Model** (if automatic download fails):
   ```bash
   ./download_yolo_model.sh
   ```

3. **Test the System**:
   ```bash
   python test_person_detection.py
   ```

## Usage

### Enable Integrated Detection
Add to your `.env` file:
```bash
ENABLE_PERSON_DETECTION=true
```

### Run Video Capture with Detection
```bash
# Regular capture command now includes detection if enabled
watcher-capture
```

### Test Detection Only
```bash
# Test with preview window
python test_person_detection.py
```

## Configuration

Add these settings to your `.env` file:

```bash
# Person Detection Settings
ENABLE_PERSON_DETECTION=true           # Enable detection during video capture
PERSON_DETECT_CONFIDENCE=0.5        # Detection confidence (0.0-1.0)
PERSON_DETECT_COOLDOWN=10           # Seconds between alerts
PERSON_DETECT_MAX_AGE_HOURS=24      # Hours before screenshot cleanup
```

## How It Works

1. **Video Capture**: Records video using ffmpeg as normal
2. **Parallel Detection**: Runs AI detection in a separate thread
3. **Shared Camera**: Both processes use the same camera efficiently
4. **Person Detection**: When a person is detected with sufficient confidence
5. **Screenshot Creation**: Captures the frame with bounding boxes and labels
6. **Telegram Alert**: Sends the annotated screenshot to your Telegram chat
7. **Cooldown**: Waits for the configured cooldown period before next alert

## Telegram Alert Format

When a person is detected, you'll receive a message like:

```
🚨 Person Detection Alert!
⏰ Time: 2025-07-07 15:30:45
👥 Persons detected: 1
📹 During video capture session
Person 1: 87% confidence
```

## File Management

- Screenshots are saved to `screenshots/` directory
- Files are automatically named with timestamps: `person_detected_20250707_153045.jpg`
- Old screenshots are automatically cleaned up after 24 hours (configurable)

## Performance Notes

- **First Run**: Downloads YOLOv8 model (~6MB) - this only happens once
- **CPU Usage**: Moderate additional CPU usage during detection
- **Memory**: +200-500MB RAM for AI model
- **Efficiency**: Much more efficient than separate detection processes

## Troubleshooting

### "Person detection enabled but dependencies not available"
```bash
./install_person_detection.sh
```

### "Cannot open camera for detection"
```bash
python test_person_detection.py
```

### Poor Detection Accuracy
- Lower confidence threshold: `PERSON_DETECT_CONFIDENCE=0.3`
- Ensure good lighting
- Check camera positioning

### Too Many Alerts
- Increase cooldown: `PERSON_DETECT_COOLDOWN=30`
- Increase confidence: `PERSON_DETECT_CONFIDENCE=0.7`

### YOLO Model Download Issues
If you encounter YOLO model download errors, see [YOLO_TROUBLESHOOTING.md](YOLO_TROUBLESHOOTING.md) for detailed solutions.

### Python Environment Issues
If you encounter Python-related errors (like `No module named '_lzma'`), see [PYTHON_TROUBLESHOOTING.md](PYTHON_TROUBLESHOOTING.md) for comprehensive solutions.

### Diagnostic Tools
- **Python diagnostics**: `./diagnose_python.py`
- **Enhanced setup**: `./setup_enhanced_python.sh`
- **YOLO model test**: `python test_yolo_model.py`

Common issues and quick fixes:
- **LZMA module missing**: Run `./setup_enhanced_python.sh`
- **Network connectivity problems**: Run `./download_yolo_model.sh`
- **OpenCV issues**: Run `./install_person_detection.sh`
- **General Python issues**: Run `./diagnose_python.py`

## Installation Troubleshooting

If you encounter YOLO model download errors, see [YOLO_TROUBLESHOOTING.md](YOLO_TROUBLESHOOTING.md) for detailed solutions.

Common issues:
- Network connectivity problems
- Corporate firewall blocking downloads
- GitHub rate limiting

Quick fix: Run `./download_yolo_model.sh` to download manually.

## Integration Benefits

The integrated detection system provides several advantages:

- ✅ **No Camera Conflicts**: Single camera access for both video and detection
- ✅ **Efficient Processing**: Shared resources between video capture and detection
- ✅ **Unified Configuration**: All settings in one place
- ✅ **Automatic Operation**: Works with existing scheduled video capture
- ✅ **Seamless Integration**: Compatible with all existing features

## Privacy and Security

- All processing happens locally on your device
- No video data is sent to external servers
- Only detection screenshots are sent to your Telegram chat
- Models are downloaded from official Ultralytics repository
