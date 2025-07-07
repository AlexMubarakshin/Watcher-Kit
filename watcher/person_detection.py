#!/usr/bin/env python3
"""
Person Detection Script for Watcher
Detects people in video stream and sends screenshots to Telegram
"""

import cv2
import os
import time
import datetime
import subprocess
import requests
from ultralytics import YOLO
import numpy as np
from .config import (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CAMERA_DEVICE, LOG_DIR, BASE_DIR,
                    PERSON_DETECT_CONFIDENCE, PERSON_DETECT_COOLDOWN, PERSON_DETECT_MAX_AGE_HOURS)
from .logger import setup_logger

logger = setup_logger("person_detection", os.path.join(LOG_DIR, "person_detection.log"))

# Create screenshots directory
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class PersonDetector:
    def __init__(self):
        self.model = None
        self.camera = None
        self.last_detection_time = 0
        self.detection_cooldown = PERSON_DETECT_COOLDOWN  # Seconds between detections to avoid spam
        self.confidence_threshold = PERSON_DETECT_CONFIDENCE
        
    def load_model(self):
        """Load YOLOv8 model for person detection"""
        try:
            logger.info("🤖 Loading YOLOv8 model...")
            self.model = YOLO('yolov8n.pt')  # Nano version for speed
            logger.info("✅ Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def setup_camera(self):
        """Setup camera for video capture"""
        try:
            # Determine camera device
            if CAMERA_DEVICE == "auto":
                camera_id = self.find_external_camera()
            else:
                camera_id = int(CAMERA_DEVICE) if CAMERA_DEVICE.isdigit() else 0
            
            logger.info(f"📹 Connecting to camera {camera_id}...")
            self.camera = cv2.VideoCapture(camera_id)
            
            if not self.camera.isOpened():
                logger.error(f"❌ Cannot open camera {camera_id}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("✅ Camera setup successful")
            return True
        except Exception as e:
            logger.error(f"❌ Camera setup failed: {e}")
            return False
    
    def find_external_camera(self):
        """Find external camera, prefer over built-in"""
        try:
            # Test cameras 0-5
            for i in range(6):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        # Check if it's likely an external camera (higher resolution usually)
                        height, width = frame.shape[:2]
                        if width >= 1280 or i > 0:  # External cameras usually have ID > 0
                            cap.release()
                            logger.info(f"🎥 Found external camera at index {i} ({width}x{height})")
                            return i
                cap.release()
            
            logger.info("📱 Using default camera (index 0)")
            return 0
        except Exception as e:
            logger.warning(f"⚠️ Camera detection error: {e}")
            return 0
    
    def detect_persons(self, frame):
        """Detect persons in frame using YOLO"""
        try:
            results = self.model(frame, classes=[0])  # Class 0 is 'person' in COCO dataset
            
            persons = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        confidence = float(box.conf[0])
                        if confidence >= self.confidence_threshold:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            persons.append({
                                'bbox': (x1, y1, x2, y2),
                                'confidence': confidence
                            })
            
            return persons
        except Exception as e:
            logger.error(f"❌ Detection error: {e}")
            return []
    
    def draw_detections(self, frame, persons):
        """Draw bounding boxes around detected persons"""
        for person in persons:
            x1, y1, x2, y2 = person['bbox']
            confidence = person['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence label
            label = f"Person {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def save_screenshot(self, frame, persons):
        """Save screenshot with detected persons"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"person_detected_{timestamp}.jpg"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            
            # Draw detections on frame
            annotated_frame = self.draw_detections(frame.copy(), persons)
            
            # Add timestamp overlay
            timestamp_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(annotated_frame, timestamp_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(annotated_frame, timestamp_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
            
            # Add detection count
            count_text = f"Persons detected: {len(persons)}"
            cv2.putText(annotated_frame, count_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(annotated_frame, count_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
            
            # Save image
            cv2.imwrite(filepath, annotated_frame)
            logger.info(f"📸 Screenshot saved: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"❌ Failed to save screenshot: {e}")
            return None
    
    def send_to_telegram(self, image_path, persons):
        """Send screenshot to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            
            # Create caption
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            caption = f"🚨 Person Detection Alert!\n"
            caption += f"⏰ Time: {timestamp}\n"
            caption += f"👥 Persons detected: {len(persons)}\n"
            
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
                logger.info(f"📤 Screenshot sent to Telegram: {os.path.basename(image_path)}")
                return True
            else:
                logger.error(f"❌ Failed to send to Telegram: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
    
    def cleanup_old_screenshots(self, max_age_hours=None):
        """Clean up old screenshots"""
        if max_age_hours is None:
            max_age_hours = PERSON_DETECT_MAX_AGE_HOURS
        try:
            current_time = time.time()
            for filename in os.listdir(SCREENSHOTS_DIR):
                if filename.endswith('.jpg'):
                    filepath = os.path.join(SCREENSHOTS_DIR, filename)
                    file_age = current_time - os.path.getctime(filepath)
                    if file_age > max_age_hours * 3600:
                        os.remove(filepath)
                        logger.debug(f"🗑️ Removed old screenshot: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error: {e}")
    
    def run_detection(self, duration_minutes=60, show_preview=False):
        """Run person detection for specified duration"""
        logger.info(f"🚀 Starting person detection for {duration_minutes} minutes...")
        
        if not self.load_model():
            return False
        
        if not self.setup_camera():
            return False
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                ret, frame = self.camera.read()
                if not ret:
                    logger.error("❌ Failed to read from camera")
                    break
                
                # Detect persons
                persons = self.detect_persons(frame)
                
                if persons:
                    current_time = time.time()
                    # Check cooldown to avoid spam
                    if current_time - self.last_detection_time >= self.detection_cooldown:
                        logger.info(f"👥 Detected {len(persons)} person(s)")
                        
                        # Save screenshot
                        screenshot_path = self.save_screenshot(frame, persons)
                        
                        if screenshot_path:
                            # Send to Telegram
                            if self.send_to_telegram(screenshot_path, persons):
                                self.last_detection_time = current_time
                        
                        # Cleanup old screenshots
                        self.cleanup_old_screenshots()
                
                # Show preview if requested
                if show_preview:
                    display_frame = self.draw_detections(frame.copy(), persons)
                    cv2.imshow('Person Detection', display_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            logger.info("⏹️ Detection stopped by user")
        except Exception as e:
            logger.error(f"❌ Detection error: {e}")
        finally:
            if self.camera:
                self.camera.release()
            if show_preview:
                cv2.destroyAllWindows()
            logger.info("🏁 Person detection completed")
        
        return True

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Person Detection for Watcher')
    parser.add_argument('--duration', type=int, default=60, help='Detection duration in minutes (default: 60)')
    parser.add_argument('--preview', action='store_true', help='Show live preview window')
    parser.add_argument('--confidence', type=float, default=0.5, help='Detection confidence threshold (default: 0.5)')
    parser.add_argument('--cooldown', type=int, default=10, help='Seconds between detections (default: 10)')
    
    args = parser.parse_args()
    
    detector = PersonDetector()
    detector.confidence_threshold = args.confidence
    detector.detection_cooldown = args.cooldown
    
    detector.run_detection(
        duration_minutes=args.duration,
        show_preview=args.preview
    )

if __name__ == "__main__":
    main()
