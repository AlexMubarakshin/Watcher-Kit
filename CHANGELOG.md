# Changelog

## 2025-07-04 - Video System Improvements

### Camera Selection Enhancements
- ✅ Moved all configuration (FPS, RESOLUTION, DURATION, CAMERA_DEVICE) to .env file
- ✅ Implemented robust auto camera selection that prefers external cameras over built-in
- ✅ Improved camera detection logic with better device categorization
- ✅ Enhanced camera diagnostic tool with detailed error reporting

### Video Processing Improvements
- ✅ Added video file integrity checking before merging
- ✅ Implemented automatic repair attempts for corrupted video files
- ✅ Enhanced error handling in video merge process
- ✅ Added graceful signal handling to prevent video corruption during recording
- ✅ Improved ffmpeg parameters for better file compatibility

### Timestamp Overlay Feature
- ✅ Added configurable timestamp overlay on video recordings
- ✅ Configurable position (top-left, top-right, bottom-left, bottom-right)
- ✅ Adjustable font size and styling with background box
- ✅ Can be enabled/disabled via SHOW_TIMESTAMP setting

### Scheduling Fix
- ✅ Fixed launchd agent scheduling to record continuously every minute without gaps
- ✅ Changed from StartInterval to StartCalendarInterval for precise timing
- ✅ Reduced DURATION from 60 to 55 seconds to ensure no overlap between recordings

### Configuration
- All video settings now loaded from .env:
  - `FPS=30` - Frames per second
  - `RESOLUTION=1280x720` - Video resolution
  - `DURATION=55` - Recording duration in seconds (55s to allow for seamless timing)
  - `CAMERA_DEVICE=auto` - Camera selection (auto/0/1/2...)
  - `SHOW_TIMESTAMP=true` - Enable/disable timestamp overlay
  - `TIMESTAMP_POSITION=top-right` - Timestamp position
  - `TIMESTAMP_FONT_SIZE=24` - Timestamp font size in pixels

### Bug Fixes
- Fixed video merge failures caused by corrupted files
- Prevented creation of corrupted video files through better signal handling
- Improved camera selection reliability
- Enhanced error messages and logging
- **Fixed continuous recording gaps - now records every minute without pauses**

### Usage
- Use `watcher-camera-test` to diagnose camera issues
- Configure all settings in `.env` file
- System automatically selects best available camera in "auto" mode
- Corrupted video files are automatically detected and excluded from merging
- Video recording runs continuously every minute at :00 seconds
- Timestamp overlay shows recording start time on each video
