#!/usr/bin/env python3

import os
import datetime
import subprocess
import requests
import time
from .config import (VIDEO_DIR, MERGED_DIR, LOG_DIR, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, 
                    MAX_FILE_SIZE_MB, BASE_DIR, ENABLE_PERSON_DETECTION, 
                    PERSON_DETECT_CONFIDENCE, PERSON_DETECT_COOLDOWN, PERSON_DETECT_MAX_AGE_HOURS,
                    TELEGRAM_SCREENSHOT_DELAY, TELEGRAM_BATCH_SIZE, TELEGRAM_BATCH_TIMEOUT)
from .logger import setup_logger, notify_telegram
from .locale import _
from .notifications import check_storage_space, notify_file_sent

# Optional person detection imports
try:
    import os
    # Set OpenCV environment variable before importing cv2
    os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
    import cv2
    from ultralytics import YOLO
    DETECTION_AVAILABLE = True
    DETECTION_ERROR = None
except ImportError as e:
    DETECTION_AVAILABLE = False
    DETECTION_ERROR = str(e)
except Exception as e:
    DETECTION_AVAILABLE = False
    DETECTION_ERROR = f"Unexpected error: {str(e)}"

logger = setup_logger("merge_send", os.path.join(LOG_DIR, "merge_send.log"))

# Подготовка директорий
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)

# Create screenshots directory for person detection
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def check_video_integrity(filepath):
    """Check if video file is valid and playable"""
    try:
        cmd = ["ffprobe", "-v", "quiet", "-show_format", "-show_streams", filepath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"⚠️ Error checking video integrity for {filepath}: {e}")
        return False

def try_repair_video(input_path, output_path):
    """Try to repair corrupted video file"""
    logger.info(f"🔧 Attempting to repair video: {input_path}")
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            "-fflags", "+genpts",
            "-y",
            output_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and check_video_integrity(output_path):
            logger.info(f"✅ Successfully repaired video: {output_path}")
            return True
        else:
            logger.warning(f"❌ Failed to repair video: {input_path}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Error during video repair: {e}")
        return False

def get_video_files():
    all_files = sorted([os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")])
    valid_files = []
    repaired_files = []
    
    logger.info(f"🔍 Checking {len(all_files)} video files for integrity...")
    
    for filepath in all_files:
        if check_video_integrity(filepath):
            valid_files.append(filepath)
            logger.debug(f"✅ Valid: {os.path.basename(filepath)}")
        else:
            logger.warning(f"❌ Corrupted: {os.path.basename(filepath)}")
            # Try to repair the file
            repaired_path = filepath.replace(".mp4", "_repaired.mp4")
            if try_repair_video(filepath, repaired_path):
                valid_files.append(repaired_path)
                repaired_files.append(repaired_path)
                logger.info(f"🔧 Repaired and added: {os.path.basename(repaired_path)}")
            else:
                logger.error(f"💥 Cannot repair, skipping: {os.path.basename(filepath)}")
    
    logger.info(f"📊 Processing {len(valid_files)} valid videos ({len(repaired_files)} repaired)")
    return valid_files, repaired_files

def compress_video(input_path, output_path, target_size_mb=None):
    """Compress video with size limit check"""
    if target_size_mb is None:
        target_size_mb = MAX_FILE_SIZE_MB
    
    logger.info(f"⚙️ Compressing file: {input_path}")
    
    # Check input file size
    input_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    logger.info(f"📏 Input file size: {input_size_mb:.1f} MB (target: {target_size_mb} MB)")
    
    # Determine compression level based on file size
    if input_size_mb <= target_size_mb:
        # Light compression for files already under limit
        crf = "28"
        preset = "fast"
        logger.info(f"💡 File under {target_size_mb}MB limit, using light compression")
    else:
        # Aggressive compression for large files
        crf = "32"
        preset = "veryfast"
        logger.info(f"🔧 File over {target_size_mb}MB limit, using aggressive compression")
    
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vcodec", "libx264",
        "-crf", crf,
        "-preset", preset,
        "-acodec", "aac",
        "-b:a", "128k",
        "-y",
        output_path
    ]
    
    logger.debug(f"🛠️ Compression command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        
        # Check output file size
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Compression completed: {output_path}")
        logger.info(f"📏 Output file size: {output_size_mb:.1f} MB (reduction: {input_size_mb - output_size_mb:.1f} MB)")
        
        # If still too large, try extra compression
        if output_size_mb > target_size_mb:
            logger.warning(f"⚠️ File still over {target_size_mb}MB after compression, applying extra compression...")
            extra_compressed_path = output_path.replace(".mp4", "_extra.mp4")
            
            extra_cmd = [
                "ffmpeg",
                "-i", output_path,
                "-vcodec", "libx264",
                "-crf", "35",
                "-preset", "veryfast",
                "-vf", "scale=iw*0.8:ih*0.8",  # Reduce resolution by 20%
                "-acodec", "aac",
                "-b:a", "96k",
                "-y",
                extra_compressed_path
            ]
            
            try:
                subprocess.run(extra_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
                final_size_mb = os.path.getsize(extra_compressed_path) / (1024 * 1024)
                logger.info(f"🔧 Extra compression completed: {final_size_mb:.1f} MB")
                
                # Replace original compressed file with extra compressed version
                os.remove(output_path)
                os.rename(extra_compressed_path, output_path)
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Extra compression failed: {e}")
                # Keep the original compressed file
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(_("merge_failed", str(e)))
        return False

def merge_videos(input_files, output_path):
    logger.info(f"⚙️ " + _("merging_videos", len(input_files)))
    list_file = os.path.join(VIDEO_DIR, "to_merge.txt")
    try:
        with open(list_file, "w") as f:
            for filepath in input_files:
                f.write(f"file '{filepath}'\n")
        logger.debug(f"📝 Merge list created: {list_file}")

        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            "-y",
            output_path
        ]
        logger.debug(f"🛠️ Merge command: {' '.join(cmd)}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        logger.info(_("merge_completed", output_path))
        os.remove(list_file)
        return True
    except Exception as e:
        logger.exception(_("merge_failed", str(e)))
        notify_telegram(_("merge_failed", str(e)))
        return False

def send_to_telegram(filepath, max_size_mb=None):
    """Send video to Telegram with size validation"""
    if max_size_mb is None:
        max_size_mb = MAX_FILE_SIZE_MB
    
    logger.info(f"📤 Preparing to send to Telegram: {filepath}")
    
    # Check file size before sending
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    logger.info(f"📏 File size: {file_size_mb:.1f} MB (limit: {max_size_mb} MB)")
    
    if file_size_mb > max_size_mb:
        logger.error(f"❌ File too large for Telegram ({file_size_mb:.1f} MB > {max_size_mb} MB)")
        logger.info("🔧 Attempting emergency compression...")
        
        # Emergency compression
        emergency_path = filepath.replace(".mp4", "_emergency.mp4")
        emergency_cmd = [
            "ffmpeg",
            "-i", filepath,
            "-vcodec", "libx264",
            "-crf", "45",  # Very high compression
            "-preset", "ultrafast",
            "-vf", "scale=480:270",  # Reduce to 270p
            "-acodec", "aac",
            "-b:a", "32k",  # Very low audio bitrate
            "-r", "15",  # Reduce framerate to 15fps
            "-y",
            emergency_path
        ]
        
        try:
            subprocess.run(emergency_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
            emergency_size_mb = os.path.getsize(emergency_path) / (1024 * 1024)
            logger.info(f"🚑 Emergency compression: {emergency_size_mb:.1f} MB")
            
            if emergency_size_mb <= max_size_mb:
                # Use emergency compressed file
                filepath = emergency_path
                file_size_mb = emergency_size_mb  # Update file size variable
                logger.info("✅ Using emergency compressed file for sending")
            else:
                logger.error(f"❌ Even emergency compression failed ({emergency_size_mb:.1f} MB)")
                os.remove(emergency_path)
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Emergency compression failed: {e}")
            return False
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    try:
        logger.info(f"📤 Sending {file_size_mb:.1f} MB file to Telegram...")
        with open(filepath, 'rb') as f:
            response = requests.post(
                url,
                data={'chat_id': TELEGRAM_CHAT_ID},
                files={'video': f},
                timeout=300  # 5 minute timeout for large files
            )
        
        logger.debug(f"📨 Telegram response: {response.status_code} — {response.text}")
        
        if response.ok:
            logger.info(_("telegram_sent", filepath))
            # Clean up emergency file if used
            if filepath.endswith("_emergency.mp4"):
                try:
                    os.remove(filepath)
                    logger.debug("🗑️ Cleaned up emergency compressed file")
                except:
                    pass
            return True
        else:
            logger.error(_("telegram_failed", response.text))
            
            # Check if it's a size error (413 = Request Entity Too Large)
            if response.status_code == 413 or "413" in response.text or "Too Large" in response.text or "Entity Too Large" in response.text:
                logger.error(f"📏 File rejected by Telegram as too large (HTTP {response.status_code})")
                logger.error(f"💡 Consider reducing MAX_FILE_SIZE_MB below {max_size_mb}MB in .env file")
            
            notify_telegram(_("telegram_failed", response.text))
            return False
            
    except requests.exceptions.Timeout:
        logger.error("⏰ Telegram upload timed out")
        return False
    except Exception as e:
        logger.exception(_("telegram_failed", str(e)))
        return False

def clean_files(file_list):
    logger.info(f"🧹 Cleaning {len(file_list)} temporary files...")
    for f in file_list:
        try:
            os.remove(f)
            logger.debug(f"🗑️ Deleted: {f}")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete {f}: {e}")

def load_yolo_model():
    """Load YOLO model with robust error handling and caching"""
    try:
        # First, try to load from local cache
        cache_dir = os.path.expanduser("~/.cache/ultralytics")
        model_cache_path = os.path.join(cache_dir, "yolov8n.pt")
        
        if os.path.exists(model_cache_path):
            logger.info(f"📦 Loading YOLO model from cache: {model_cache_path}")
            return YOLO(model_cache_path)
        
        # Try to create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Try to download to local project directory first
        local_model_path = os.path.join(BASE_DIR, "models", "yolov8n.pt")
        os.makedirs(os.path.dirname(local_model_path), exist_ok=True)
        
        if os.path.exists(local_model_path):
            logger.info(f"📦 Loading YOLO model from local path: {local_model_path}")
            return YOLO(local_model_path)
        
        # Try to download model with retries
        logger.info("📦 Downloading YOLO model: yolov8n.pt")
        for attempt in range(3):
            try:
                model = YOLO('yolov8n.pt')
                
                # Try to save a copy locally for future use
                try:
                    import shutil
                    if os.path.exists(model_cache_path):
                        shutil.copy2(model_cache_path, local_model_path)
                        logger.info(f"💾 Saved model copy to: {local_model_path}")
                except Exception as e:
                    logger.debug(f"Could not save local model copy: {e}")
                
                return model
                
            except Exception as e:
                logger.warning(f"❌ Download attempt {attempt + 1}/3 failed: {e}")
                if attempt < 2:
                    logger.info(f"⏳ Retrying in {(attempt + 1) * 5} seconds...")
                    time.sleep((attempt + 1) * 5)
                else:
                    raise e
        
    except Exception as e:
        logger.error(f"❌ Failed to load YOLO model: {e}")
        logger.error("💡 Possible solutions:")
        logger.error("   1. Check internet connection")
        logger.error("   2. Download model manually: wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt")
        logger.error(f"   3. Place model file in: {os.path.join(BASE_DIR, 'models', 'yolov8n.pt')}")
        logger.error("   4. Disable person detection: ENABLE_PERSON_DETECTION=false")
        raise e

def analyze_video_for_persons(video_path):
    """Analyze video for person detection and send alerts"""
    if not DETECTION_AVAILABLE:
        error_msg = f"⚠️ Person detection dependencies not available: {DETECTION_ERROR}" if DETECTION_ERROR else "⚠️ Person detection dependencies not available"
        logger.warning(error_msg)
        
        # Provide helpful error-specific guidance
        if DETECTION_ERROR and "_lzma" in DETECTION_ERROR:
            logger.error("❌ Python LZMA module missing - this is a Python environment issue")
            logger.error("💡 Possible solutions:")
            logger.error("   1. Use Python installed via Homebrew: brew install python")
            logger.error("   2. Use pyenv: pyenv install 3.9.16 && pyenv global 3.9.16")
            logger.error("   3. Use conda: conda install python")
            logger.error("   4. Disable person detection: ENABLE_PERSON_DETECTION=false")
        elif DETECTION_ERROR and ("cv2" in DETECTION_ERROR or "opencv" in DETECTION_ERROR):
            logger.error("❌ OpenCV not installed properly")
            logger.error("💡 Run: ./install_person_detection.sh")
        elif DETECTION_ERROR and "ultralytics" in DETECTION_ERROR:
            logger.error("❌ YOLOv8 (ultralytics) not installed")
            logger.error("💡 Run: ./install_person_detection.sh")
        
        return []
    
    try:
        # Load model with robust error handling
        model = load_yolo_model()
        
        logger.info("✅ Person detection model loaded")
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"❌ Cannot open video file: {video_path}")
            return []
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"📹 Analyzing video: {duration:.1f}s, {total_frames} frames at {fps}fps")
        
        # Sample frames for analysis (every 3 seconds to reduce processing)
        sample_interval = fps * 3 if fps > 0 else 90  # Every 3 seconds
        detections = []
        frame_count = 0
        sent_screenshots = []
        last_alert_time = 0  # Track when we last sent an alert
        batch_count = 0  # Track screenshots in current batch
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Only analyze sampled frames
            if frame_count % sample_interval == 0:
                timestamp = frame_count / fps if fps > 0 else frame_count
                
                try:
                    # Detect persons in frame
                    results = model(frame, classes=[0], verbose=False)  # Class 0 is 'person'
                    
                    persons = []
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                confidence = float(box.conf[0])
                                if confidence >= PERSON_DETECT_CONFIDENCE:
                                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                                    persons.append({
                                        'bbox': (x1, y1, x2, y2),
                                        'confidence': confidence,
                                        'timestamp': timestamp
                                    })
                    
                    if persons:
                        detections.extend(persons)
                        logger.debug(f"👥 Found {len(persons)} person(s) at {timestamp:.1f}s")
                        
                        # Check cooldown before sending alert
                        time_since_last_alert = timestamp - last_alert_time
                        if time_since_last_alert >= PERSON_DETECT_COOLDOWN:
                            # Save screenshot and send to Telegram
                            screenshot_path = save_detection_screenshot(frame, persons, timestamp, video_path)
                            if screenshot_path:
                                if send_detection_to_telegram(screenshot_path, persons, video_path, timestamp):
                                    sent_screenshots.append(screenshot_path)
                                    last_alert_time = timestamp  # Update last alert time
                                    batch_count += 1
                                    logger.info(f"📤 Detection alert sent: {os.path.basename(screenshot_path)} (batch: {batch_count}/{TELEGRAM_BATCH_SIZE})")
                                    
                                    # Check if we've reached the batch size limit
                                    if batch_count >= TELEGRAM_BATCH_SIZE:
                                        logger.info(f"⏸️ Batch size limit reached ({TELEGRAM_BATCH_SIZE}), applying batch timeout of {TELEGRAM_BATCH_TIMEOUT}s...")
                                        time.sleep(TELEGRAM_BATCH_TIMEOUT)
                                        batch_count = 0  # Reset batch counter
                                    else:
                                        # Add regular delay to prevent Telegram rate limiting
                                        logger.debug(f"⏳ Waiting {TELEGRAM_SCREENSHOT_DELAY}s to prevent Telegram rate limiting...")
                                        time.sleep(TELEGRAM_SCREENSHOT_DELAY)
                                else:
                                    logger.warning(f"⚠️ Failed to send detection alert: {os.path.basename(screenshot_path)}")
                        else:
                            logger.debug(f"⏰ Cooldown active: {time_since_last_alert:.1f}s < {PERSON_DETECT_COOLDOWN}s, skipping alert")
                
                except Exception as e:
                    logger.error(f"❌ Error analyzing frame at {timestamp:.1f}s: {e}")
        
        cap.release()
        
        # Summary
        if detections:
            unique_timestamps = set(d['timestamp'] for d in detections)
            logger.info(f"🎯 Person detection complete: {len(detections)} detections across {len(unique_timestamps)} time points")
            logger.info(f"📤 Sent {len(sent_screenshots)} detection alerts (cooldown: {PERSON_DETECT_COOLDOWN}s, delay: {TELEGRAM_SCREENSHOT_DELAY}s)")
            
            if len(sent_screenshots) < len(unique_timestamps):
                suppressed = len(unique_timestamps) - len(sent_screenshots)
                logger.info(f"⏰ Suppressed {suppressed} alerts due to cooldown period")
            
            if len(sent_screenshots) > 0:
                # Calculate total delays including batch timeouts
                regular_delays = len(sent_screenshots) * TELEGRAM_SCREENSHOT_DELAY
                batch_timeouts = (len(sent_screenshots) // TELEGRAM_BATCH_SIZE) * TELEGRAM_BATCH_TIMEOUT
                total_delay = regular_delays + batch_timeouts
                
                logger.info(f"⏳ Total rate limiting delay: {total_delay}s")
                logger.info(f"   - Regular delays: {regular_delays}s ({len(sent_screenshots)} alerts × {TELEGRAM_SCREENSHOT_DELAY}s)")
                if batch_timeouts > 0:
                    batches = len(sent_screenshots) // TELEGRAM_BATCH_SIZE
                    logger.info(f"   - Batch timeouts: {batch_timeouts}s ({batches} batches × {TELEGRAM_BATCH_TIMEOUT}s)")
        else:
            logger.info("👤 No persons detected in video")
        
        return sent_screenshots
            
    except Exception as e:
        logger.error(f"❌ Video analysis error: {e}")
        return []

def save_detection_screenshot(frame, persons, timestamp, video_path):
    """Save screenshot with detected persons"""
    try:
        video_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        filename = f"person_detected_{video_name}_t{timestamp:.1f}s_{video_timestamp}.jpg"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Draw detections on frame
        annotated_frame = frame.copy()
        for person in persons:
            x1, y1, x2, y2 = person['bbox']
            confidence = person['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence label
            label = f"Person {confidence:.2f}"
            cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add timestamp overlays
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated_frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(annotated_frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        
        # Add video timestamp
        video_time = f"Video time: {timestamp:.1f}s"
        cv2.putText(annotated_frame, video_time, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(annotated_frame, video_time, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        
        # Add video filename
        video_file = f"Source: {os.path.basename(video_path)}"
        cv2.putText(annotated_frame, video_file, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated_frame, video_file, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        
        # Add detection count
        count_text = f"Persons detected: {len(persons)}"
        cv2.putText(annotated_frame, count_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(annotated_frame, count_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        
        # Save image
        cv2.imwrite(filepath, annotated_frame)
        logger.debug(f"📸 Detection screenshot saved: {filename}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Failed to save detection screenshot: {e}")
        return None

def send_detection_to_telegram(image_path, persons, video_path, timestamp):
    """Send detection screenshot to Telegram"""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("⚠️ Telegram credentials not configured for detection alerts")
            return False
            
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        # Create caption
        detection_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caption = f"🚨 Person Detection Alert!\n"
        caption += f"⏰ Analysis time: {detection_time}\n"
        caption += f"👥 Persons detected: {len(persons)}\n"
        caption += f"📹 Video: {os.path.basename(video_path)}\n"
        caption += f"⏱️ Video timestamp: {timestamp:.1f}s\n"
        
        for i, person in enumerate(persons, 1):
            confidence = person['confidence']
            caption += f"Person {i}: {confidence:.1%} confidence\n"
        
        with open(image_path, 'rb') as f:
            response = requests.post(
                url,
                data={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': caption
                },
                files={'photo': f},
                timeout=30
            )
        
        if response.ok:
            logger.debug(f"✅ Detection alert sent to Telegram: {os.path.basename(image_path)}")
            return True
        else:
            logger.error(f"❌ Failed to send detection to Telegram: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram detection send error: {e}")
        return False

def cleanup_old_screenshots():
    """Clean up old detection screenshots based on PERSON_DETECT_MAX_AGE_HOURS"""
    try:
        current_time = time.time()
        max_age_hours = PERSON_DETECT_MAX_AGE_HOURS
        cleaned_count = 0
        
        for filename in os.listdir(SCREENSHOTS_DIR):
            if filename.endswith('.jpg') and filename.startswith('person_detected_'):
                filepath = os.path.join(SCREENSHOTS_DIR, filename)
                file_age = current_time - os.path.getctime(filepath)
                if file_age > max_age_hours * 3600:
                    os.remove(filepath)
                    cleaned_count += 1
                    logger.debug(f"🗑️ Removed old detection screenshot: {filename}")
        
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} old detection screenshots")
    except Exception as e:
        logger.warning(f"⚠️ Detection cleanup error: {e}")

def clean_detection_files(sent_screenshots):
    """Clean up detection screenshots that were successfully sent"""
    logger.info(f"🧹 Cleaning {len(sent_screenshots)} sent detection screenshots...")
    for screenshot_path in sent_screenshots:
        try:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                logger.debug(f"🗑️ Deleted sent screenshot: {os.path.basename(screenshot_path)}")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete {screenshot_path}: {e}")

def main():
    logger.info(_("script_start"))
    
    # Check storage space before processing
    if not check_storage_space():
        logger.warning("Storage space low, but continuing with processing")
    
    valid_files, repaired_files = get_video_files()
    
    if len(valid_files) < 2:
        logger.warning(_("insufficient_files"))
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_file = os.path.join(MERGED_DIR, f"merged_{timestamp}.mp4")
    compressed_file = os.path.join(MERGED_DIR, f"compressed_{timestamp}.mp4")

    sent_screenshots = []
    video_sent = False

    if merge_videos(valid_files, merged_file):
        if compress_video(merged_file, compressed_file, MAX_FILE_SIZE_MB):
            if send_to_telegram(compressed_file, MAX_FILE_SIZE_MB):
                video_sent = True
                logger.info("✅ Video successfully sent to Telegram")
                # Use enhanced notification
                notify_file_sent(compressed_file)
                
                # Now analyze the video for person detection
                if ENABLE_PERSON_DETECTION and DETECTION_AVAILABLE:
                    logger.info("🤖 Starting person detection analysis on sent video...")
                    sent_screenshots = analyze_video_for_persons(compressed_file)
                    if sent_screenshots:
                        logger.info(f"📤 Sent {len(sent_screenshots)} person detection alerts")
                    else:
                        logger.info("👤 No persons detected or alerts sent")
                elif ENABLE_PERSON_DETECTION and not DETECTION_AVAILABLE:
                    logger.warning("⚠️ Person detection enabled but dependencies not available")
                    logger.warning("💡 Run: ./fix_person_detection.sh to install dependencies")
                
                # Clean up files only after successful sending
                files_to_clean = [f for f in valid_files if not f.endswith("_repaired.mp4")] + repaired_files + [merged_file, compressed_file]
                clean_files(files_to_clean)
                
                # Clean up successfully sent detection screenshots
                if sent_screenshots:
                    clean_detection_files(sent_screenshots)
                
                # Clean up old detection screenshots
                cleanup_old_screenshots()
                
            else:
                logger.warning(_("send_failed_keep_files"))
        else:
            logger.warning(_("compression_failed_no_send"))
            # Clean up repaired files even if compression failed
            if repaired_files:
                clean_files(repaired_files)
    else:
        logger.warning(_("merge_failed"))
        # Clean up repaired files even if merge failed
        if repaired_files:
            clean_files(repaired_files)

    # Summary
    if video_sent:
        logger.info("🎯 Session complete: Video sent successfully")
        if ENABLE_PERSON_DETECTION and sent_screenshots:
            logger.info(f"📤 Person detection: {len(sent_screenshots)} alerts sent")
    else:
        logger.warning("⚠️ Session complete: Video not sent - files preserved")

    logger.info(_("script_complete") + "\n")

if __name__ == "__main__":
    main()