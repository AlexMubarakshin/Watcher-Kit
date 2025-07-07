# Person Detection Feature

The Watcher system includes an AI-powered person detection feature that can monitor your camera feed in real-time and send alerts to Telegram when people are detected.

## Features

- 🤖 **AI-Powered Detection**: Uses YOLOv8 for accurate person detection
- 📸 **Smart Screenshots**: Automatically captures and annotates images when people are detected
- 📱 **Telegram Alerts**: Sends detection alerts with screenshots to your Telegram chat
- ⚡ **Real-time Processing**: Live video stream analysis
- 🎯 **Configurable Sensitivity**: Adjustable confidence thresholds
- 🕐 **Smart Cooldowns**: Prevents spam by limiting alert frequency
- 🧹 **Auto Cleanup**: Automatically removes old screenshots

## Installation

1. **Install Dependencies**:
   ```bash
   ./install_person_detection.sh
   ```

2. **Test the System**:
   ```bash
   python test_person_detection.py
   ```

## Usage

### Quick Test
```bash
# Test with preview window (look for a person in the camera view)
python person_detect.py --test --preview
```

### Normal Operation
```bash
# Run for 30 minutes with live preview
python person_detect.py --duration 30 --preview

# Run for 1 hour in background
python person_detect.py --duration 60
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--duration X` | Run for X minutes | 60 |
| `--preview` | Show live preview window | Off |
| `--confidence X` | Detection confidence (0.0-1.0) | 0.5 |
| `--cooldown X` | Seconds between alerts | 10 |
| `--test` | Test mode - single detection and exit | Off |

## Configuration

Add these settings to your `.env` file:

```bash
# Person Detection Settings
PERSON_DETECT_CONFIDENCE=0.5        # Detection confidence (0.0-1.0)
PERSON_DETECT_COOLDOWN=10           # Seconds between alerts
PERSON_DETECT_MAX_AGE_HOURS=24      # Hours before screenshot cleanup
```

## How It Works

1. **Video Capture**: Connects to your camera (same as regular video recording)
2. **AI Analysis**: Each frame is analyzed by the YOLOv8 model
3. **Person Detection**: When a person is detected with sufficient confidence
4. **Screenshot Creation**: Captures the frame with bounding boxes and labels
5. **Telegram Alert**: Sends the annotated screenshot to your Telegram chat
6. **Cooldown**: Waits for the configured cooldown period before next alert

## Telegram Alert Format

When a person is detected, you'll receive a message like:

```
🚨 Person Detection Alert!
⏰ Time: 2025-07-07 15:30:45
👥 Persons detected: 2
Person 1: 87% confidence
Person 2: 72% confidence
```

## File Management

- Screenshots are saved to `screenshots/` directory
- Files are automatically named with timestamps: `person_detected_20250707_153045.jpg`
- Old screenshots are automatically cleaned up after 24 hours (configurable)

## Performance Notes

- **First Run**: Downloads YOLOv8 model (~6MB) - this only happens once
- **CPU Usage**: Moderate CPU usage during detection
- **Memory**: ~200-500MB RAM depending on video resolution
- **Accuracy**: YOLOv8 nano model provides good balance of speed and accuracy

## Troubleshooting

### "No module named 'cv2'"
```bash
./install_person_detection.sh
```

### "Cannot open camera"
```bash
python test_person_detection.py
```

### Poor Detection Accuracy
- Lower confidence threshold: `--confidence 0.3`
- Ensure good lighting
- Check camera positioning

### Too Many Alerts
- Increase cooldown: `--cooldown 30`
- Increase confidence: `--confidence 0.7`

## Integration with Main System

The person detection runs independently of the main video recording system. You can:

- Run person detection while regular video recording is active
- Use the same camera for both systems
- Configure different settings for each system

## Privacy and Security

- All processing happens locally on your device
- No video data is sent to external servers
- Only detection screenshots are sent to your Telegram chat
- Models are downloaded from official Ultralytics repository
