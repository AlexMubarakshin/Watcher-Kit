#!/usr/bin/env python3
# capture_video.py

import subprocess
import datetime
import os
import signal
import sys
from .config import VIDEO_DIR, LOG_DIR, CAMERA_DEVICE, DURATION, RESOLUTION, FPS
from .logger import setup_logger
from .locale import _

logger = setup_logger("capture", os.path.join(LOG_DIR, "capture.log"))

# Подготовка директорий
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Global variable to track current ffmpeg process
current_process = None

def signal_handler(signum, frame):
    """Handle termination signals to ensure clean video file closure"""
    global current_process
    logger.info(f"📡 Received signal {signum}, attempting graceful shutdown...")
    
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
    global current_process
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(VIDEO_DIR, f"video_{timestamp}.mp4")

    # Use smart camera selection if CAMERA_DEVICE is "auto"
    if CAMERA_DEVICE.lower() == "auto":
        camera_device = get_preferred_camera()
    else:
        camera_device = CAMERA_DEVICE

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
        "-y",
        output_path
    ]

    try:
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
            logger.info(_("capture_completed", output_path))
            
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
        logger.exception(_("capture_failed", str(e)))
    finally:
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

def main():
    capture()

if __name__ == "__main__":
    main()