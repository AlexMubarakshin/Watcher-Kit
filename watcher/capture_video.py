#!/usr/bin/env python3
# capture_video.py

import subprocess
import datetime
import os
import signal
import sys
import threading
import time
from .config import (VIDEO_DIR, LOG_DIR, CAMERA_DEVICE, DURATION, RESOLUTION, FPS, 
                    SHOW_TIMESTAMP, TIMESTAMP_POSITION, TIMESTAMP_FONT_SIZE,
                    CAPTURE_DEBUG_PREVIEW)
from .logger import setup_logger
from .locale import _

# Optional debug preview imports
try:
    import os
    # Set OpenCV environment variable before importing cv2
    os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
    import cv2
    PREVIEW_AVAILABLE = True
except ImportError:
    PREVIEW_AVAILABLE = False

logger = setup_logger("capture", os.path.join(LOG_DIR, "capture.log"))

# Подготовка директорий
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Global variable to track current ffmpeg process and preview thread
current_process = None
preview_thread = None
stop_detection = threading.Event()

def signal_handler(signum, frame):
    """Handle termination signals to ensure clean video file closure"""
    global current_process, preview_thread
    logger.info(f"📡 Received signal {signum}, attempting graceful shutdown...")
    
    # Stop preview thread if running
    if preview_thread and preview_thread.is_alive():
        stop_detection.set()
        preview_thread.join(timeout=5)
    
    if current_process and current_process.poll() is None:
        logger.info("🛑 Stopping ffmpeg process gracefully...")
        try:
            # Send SIGTERM to ffmpeg for graceful shutdown
            current_process.terminate()
            current_process.wait(timeout=5)
            logger.info("✅ ffmpeg process terminated gracefully")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ ffmpeg didn't respond to SIGTERM, using SIGKILL")
            current_process.kill()
            current_process.wait()
        except Exception as e:
            logger.error(f"❌ Error stopping ffmpeg: {e}")
    
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def get_timestamp_filter():
    """
    Create ffmpeg filter for timestamp overlay with real-time updates
    Создает фильтр ffmpeg для наложения времени с обновлением в реальном времени
    """
    if not SHOW_TIMESTAMP:
        return []
    
    # Parse resolution to get width and height
    try:
        width, height = map(int, RESOLUTION.split('x'))
    except:
        width, height = 1280, 720  # Default fallback
    
    # Determine position coordinates
    positions = {
        'top-left': 'x=10:y=30',
        'top-right': f'x={width-280}:y=30',
        'bottom-left': f'x=10:y={height-50}',
        'bottom-right': f'x={width-280}:y={height-50}'
    }
    
    position = positions.get(TIMESTAMP_POSITION, positions['top-right'])
    
    # Use drawtext with localtime for real-time updates
    # Format: 2025-07-04 21:50:15 (updates every frame)
    filter_complex = (
        f"drawtext="
        f"text='%{{localtime\\:%Y-%m-%d %H\\\\\\:%M\\\\\\:%S}}'"
        f":fontcolor=white"
        f":fontsize={TIMESTAMP_FONT_SIZE}"
        f":box=1"
        f":boxcolor=black@0.5"
        f":boxborderw=3"
        f":{position}"
    )
    
    return ["-vf", filter_complex]

def get_preferred_camera():
    """
    Smart camera selection: prefer external cameras over built-in
    Умный выбор камеры: предпочитаем внешние камеры встроенным
    """
    try:
        cmd = ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        devices = []
        in_video_section = False
        
        for line in result.stderr.split('\n'):
            # Check for video devices section
            if 'AVFoundation video devices:' in line:
                in_video_section = True
                continue
            elif 'AVFoundation audio devices:' in line:
                in_video_section = False
                continue
            
            # Only process video devices
            if in_video_section and '] [' in line:
                # Format: [AVFoundation indev @ 0x...] [0] Device Name
                parts = line.split('] [')
                if len(parts) >= 2:
                    device_index = parts[1].split(']')[0]  # Get the device number
                    device_name = parts[1].split('] ')[1] if '] ' in parts[1] else parts[1].split(']')[1]
                    devices.append((device_index, device_name))
        
        logger.info(f"📋 Found {len(devices)} video devices")
        for idx, name in devices:
            logger.info(f"  [{idx}] {name}")
        
        # Define built-in camera patterns to exclude
        builtin_patterns = [
            'MacBook Pro', 'MacBook Air', 'iMac', 'Mac mini', 
            'built-in', 'Built-in', 'Internal', 'internal',
            'Desk View', 'FaceTime', 'Capture screen'
        ]
        
        # Prioritize external cameras (not matching built-in patterns)
        external_cameras = []
        builtin_cameras = []
        
        for device_idx, device_name in devices:
            is_builtin = any(pattern in device_name for pattern in builtin_patterns)
            if is_builtin:
                builtin_cameras.append((device_idx, device_name))
            else:
                external_cameras.append((device_idx, device_name))
        
        if external_cameras:
            selected = external_cameras[0]
            logger.info(f"🎯 Selected external camera: [{selected[0]}] {selected[1]}")
            return selected[0]
        elif builtin_cameras:
            selected = builtin_cameras[0]
            logger.info(f"📱 Selected built-in camera: [{selected[0]}] {selected[1]}")
            return selected[0]
        elif devices:
            selected = devices[0]
            logger.info(f"❓ Selected first available camera: [{selected[0]}] {selected[1]}")
            return selected[0]
        else:
            logger.warning("⚠️ No cameras found, using fallback device")
            return "0"  # Default fallback
            
    except Exception as e:
        logger.warning(f"⚠️ Camera detection failed: {e}, using fallback device")
        return "0"  # Default fallback

def capture():
    global current_process, preview_thread
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(VIDEO_DIR, f"video_{timestamp}.mp4")

    # Use smart camera selection if CAMERA_DEVICE is "auto"
    if CAMERA_DEVICE.lower() == "auto":
        camera_device = get_preferred_camera()
    else:
        camera_device = CAMERA_DEVICE

    # Start debug preview thread if enabled (no conflicts with ffmpeg)
    if CAPTURE_DEBUG_PREVIEW and PREVIEW_AVAILABLE:
        logger.info("📺 Starting debug preview window")
        stop_detection.clear()
        preview_thread = threading.Thread(target=preview_worker, args=(camera_device,))
        preview_thread.daemon = True
        preview_thread.start()
    elif CAPTURE_DEBUG_PREVIEW and not PREVIEW_AVAILABLE:
        logger.warning("⚠️ Debug preview enabled but OpenCV not available")
        logger.warning("💡 Run: ./fix_person_detection.sh to install OpenCV")

    # Base ffmpeg command
    cmd = [
        "ffmpeg",
        "-f", "avfoundation",
        "-framerate", str(FPS),
        "-video_size", RESOLUTION,
        "-i", camera_device,
        "-t", str(DURATION),
        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-movflags", "+faststart",  # Improve file compatibility
        "-avoid_negative_ts", "make_zero",  # Handle timestamp issues
    ]
    
    # Add timestamp filter if enabled
    timestamp_filter = get_timestamp_filter()
    if timestamp_filter:
        cmd.extend(timestamp_filter)
        logger.info(f"📅 Adding timestamp overlay: {TIMESTAMP_POSITION}, size {TIMESTAMP_FONT_SIZE}px")
    
    # Add output file and overwrite flag
    cmd.extend(["-y", output_path])

    try:
        features = []
        if CAPTURE_DEBUG_PREVIEW and PREVIEW_AVAILABLE:
            features.append("debug preview")
        
        if features:
            logger.info(f"🎬 Starting video capture with {' + '.join(features)}: {output_path}")
        else:
            logger.info(f"🎬 Starting video capture: {output_path}")
        
        logger.debug(f"🛠️ ffmpeg command: {' '.join(cmd)}")
        
        current_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        
        # Wait for process to complete
        stdout, _ = current_process.communicate()
        
        if current_process.returncode == 0:
            logger.info(f"✅ Video capture completed: {output_path}")
            
            # Verify the created file is valid
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                # Quick integrity check
                check_cmd = ["ffprobe", "-v", "quiet", "-show_format", output_path]
                check_result = subprocess.run(check_cmd, capture_output=True)
                if check_result.returncode == 0:
                    logger.info(f"✅ Video file verified: {output_path}")
                else:
                    logger.warning(f"⚠️ Video file may be corrupted: {output_path}")
            else:
                logger.error(f"❌ Video file not created or empty: {output_path}")
        else:
            logger.error(f"❌ ffmpeg failed with return code {current_process.returncode}")
            if stdout:
                logger.error(f"ffmpeg output: {stdout}")
                
    except KeyboardInterrupt:
        logger.info("🛑 Capture interrupted by user")
        if current_process and current_process.poll() is None:
            signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.exception(f"❌ Video capture failed: {str(e)}")
    finally:
        # Stop preview thread if running
        if preview_thread and preview_thread.is_alive():
            stop_detection.set()
            preview_thread.join(timeout=5)
            logger.info("📺 Debug preview stopped")
        
        current_process = None

def list_devices():
    """Показать список доступных камер"""
    cmd = [
        "ffmpeg",
        "-f", "avfoundation", 
        "-list_devices", "true",
        "-i", ""
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("📹 " + _("camera_list"))
        print(result.stderr)  # ffmpeg выводит список устройств в stderr
    except Exception as e:
        print(_("camera_not_found", str(e)))

def preview_worker(camera_device):
    """Worker thread for debug preview window"""
    if not PREVIEW_AVAILABLE:
        logger.warning("⚠️ Debug preview requires OpenCV")
        return
    
    try:
        logger.info("📺 Starting debug preview window...")
        
        # Setup camera for preview
        cam_id = int(camera_device) if camera_device.isdigit() else 0
        camera = cv2.VideoCapture(cam_id)
        
        if not camera.isOpened():
            logger.error(f"❌ Cannot open camera for preview: {camera_device}")
            return
        
        # Set camera properties to match recording
        try:
            width, height = map(int, RESOLUTION.split('x'))
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            camera.set(cv2.CAP_PROP_FPS, FPS)
        except:
            logger.warning("⚠️ Could not set camera properties for preview")
        
        logger.info("✅ Debug preview window opened (press 'q' to close preview only)")
        
        while not stop_detection.is_set():
            ret, frame = camera.read()
            if not ret:
                logger.warning("⚠️ Failed to read frame for preview")
                break
            
            # Add recording indicator
            recording_text = "🔴 RECORDING"
            cv2.putText(frame, recording_text, (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Add timestamp if enabled
            if SHOW_TIMESTAMP:
                timestamp_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add resolution info
            res_text = f"{frame.shape[1]}x{frame.shape[0]} @ {FPS}fps"
            cv2.putText(frame, res_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow('Watcher Debug Preview', frame)
            
            # Check for quit key (only closes preview, not recording)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("🛑 Debug preview closed by user (recording continues)")
                break
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.033)  # ~30fps for preview
        
        camera.release()
        cv2.destroyAllWindows()
        logger.info("📺 Debug preview stopped")
        
    except Exception as e:
        logger.error(f"❌ Preview worker error: {e}")

def main():
    capture()

if __name__ == "__main__":
    main()