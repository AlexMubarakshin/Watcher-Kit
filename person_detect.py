#!/usr/bin/env python3
"""
Simple Person Detection Script for Watcher
Detects people in video stream and sends screenshots to Telegram
"""

import cv2
import os
import sys
import time
import datetime
import requests
from ultralytics import YOLO
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CAMERA_DEVICE = os.getenv("CAMERA_DEVICE", "auto")

# Create directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def find_external_camera():
    """Find external camera, prefer over built-in"""
    try:
        print("🔍 Searching for cameras...")
        # Test cameras 0-5
        for i in range(6):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Check if it's likely an external camera
                    height, width = frame.shape[:2]
                    print(f"📹 Camera {i}: {width}x{height}")
                    if width >= 1280 or i > 0:  # External cameras usually have ID > 0
                        cap.release()
                        print(f"✅ Using external camera at index {i}")
                        return i
                cap.release()
        
        print("📱 Using default camera (index 0)")
        return 0
    except Exception as e:
        print(f"⚠️ Camera detection error: {e}")
        return 0

def setup_camera():
    """Setup camera for video capture"""
    try:
        # Determine camera device
        if CAMERA_DEVICE == "auto":
            camera_id = find_external_camera()
        else:
            camera_id = int(CAMERA_DEVICE) if CAMERA_DEVICE.isdigit() else 0
        
        print(f"📹 Connecting to camera {camera_id}...")
        camera = cv2.VideoCapture(camera_id)
        
        if not camera.isOpened():
            print(f"❌ Cannot open camera {camera_id}")
            return None
        
        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera setup successful")
        return camera
    except Exception as e:
        print(f"❌ Camera setup failed: {e}")
        return None

def load_model():
    """Load YOLOv8 model for person detection"""
    try:
        print("🤖 Loading YOLOv8 model (this may take a moment on first run)...")
        model = YOLO('yolov8n.pt')  # Nano version for speed
        print("✅ Model loaded successfully")
        return model
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None

def detect_persons(model, frame, confidence_threshold=0.5):
    """Detect persons in frame using YOLO"""
    try:
        results = model(frame, classes=[0], verbose=False)  # Class 0 is 'person' in COCO dataset
        
        persons = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    confidence = float(box.conf[0])
                    if confidence >= confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        persons.append({
                            'bbox': (x1, y1, x2, y2),
                            'confidence': confidence
                        })
        
        return persons
    except Exception as e:
        print(f"❌ Detection error: {e}")
        return []

def draw_detections(frame, persons):
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

def save_screenshot(frame, persons):
    """Save screenshot with detected persons"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"person_detected_{timestamp}.jpg"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Draw detections on frame
        annotated_frame = draw_detections(frame.copy(), persons)
        
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
        print(f"📸 Screenshot saved: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to save screenshot: {e}")
        return None

def send_to_telegram(image_path, persons):
    """Send screenshot to Telegram"""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("❌ Telegram credentials not configured")
            return False
        
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
            print(f"📤 Screenshot sent to Telegram: {os.path.basename(image_path)}")
            return True
        else:
            print(f"❌ Failed to send to Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram send error: {e}")
        return False

def cleanup_old_screenshots(max_age_hours=24):
    """Clean up old screenshots"""
    try:
        current_time = time.time()
        for filename in os.listdir(SCREENSHOTS_DIR):
            if filename.endswith('.jpg'):
                filepath = os.path.join(SCREENSHOTS_DIR, filename)
                file_age = current_time - os.path.getctime(filepath)
                if file_age > max_age_hours * 3600:
                    os.remove(filepath)
                    print(f"🗑️ Removed old screenshot: {filename}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Person Detection for Watcher')
    parser.add_argument('--duration', type=int, default=60, help='Detection duration in minutes (default: 60)')
    parser.add_argument('--preview', action='store_true', help='Show live preview window')
    parser.add_argument('--confidence', type=float, default=0.5, help='Detection confidence threshold (default: 0.5)')
    parser.add_argument('--cooldown', type=int, default=10, help='Seconds between detections (default: 10)')
    parser.add_argument('--test', action='store_true', help='Test mode - take one screenshot and exit')
    
    args = parser.parse_args()
    
    print("🚀 Starting Person Detection System")
    print(f"⏱️ Duration: {args.duration} minutes")
    print(f"🎯 Confidence threshold: {args.confidence}")
    print(f"⏳ Detection cooldown: {args.cooldown} seconds")
    
    # Load model
    model = load_model()
    if not model:
        return False
    
    # Setup camera
    camera = setup_camera()
    if not camera:
        return False
    
    last_detection_time = 0
    start_time = time.time()
    end_time = start_time + (args.duration * 60)
    
    try:
        while time.time() < end_time:
            ret, frame = camera.read()
            if not ret:
                print("❌ Failed to read from camera")
                break
            
            # Detect persons
            persons = detect_persons(model, frame, args.confidence)
            
            if persons:
                current_time = time.time()
                # Check cooldown to avoid spam
                if current_time - last_detection_time >= args.cooldown:
                    print(f"👥 Detected {len(persons)} person(s)")
                    
                    # Save screenshot
                    screenshot_path = save_screenshot(frame, persons)
                    
                    if screenshot_path:
                        # Send to Telegram
                        if send_to_telegram(screenshot_path, persons):
                            last_detection_time = current_time
                    
                    # Cleanup old screenshots
                    cleanup_old_screenshots()
                    
                    # Test mode - exit after first detection
                    if args.test:
                        print("✅ Test completed - exiting")
                        break
            
            # Show preview if requested
            if args.preview:
                display_frame = draw_detections(frame.copy(), persons)
                cv2.imshow('Person Detection', display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("⏹️ Detection stopped by user")
    except Exception as e:
        print(f"❌ Detection error: {e}")
    finally:
        if camera:
            camera.release()
        if args.preview:
            cv2.destroyAllWindows()
        print("🏁 Person detection completed")
    
    return True

if __name__ == "__main__":
    main()
