#!/usr/bin/env python3

"""
Test script for Telegram media group functionality
Creates test screenshots and sends them as media groups
"""

import sys
import os
import json
import tempfile
import numpy as np

# Add the watcher module to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from watcher.merge_and_send import send_detection_media_group, DETECTION_AVAILABLE
    from watcher.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_MEDIA_GROUP_SIZE
    
    if DETECTION_AVAILABLE:
        import cv2
    
    print("📤 Telegram Media Group Test")
    print("=" * 30)
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials not configured")
        print("💡 Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        sys.exit(1)
    
    if not DETECTION_AVAILABLE:
        print("❌ Detection dependencies not available")
        print("💡 Run: ./install_person_detection.sh")
        sys.exit(1)
    
    print(f"✅ Telegram configured (media group size: {TELEGRAM_MEDIA_GROUP_SIZE})")
    
    # Create test screenshots
    print("🎨 Creating test screenshots...")
    
    screenshots_data = []
    temp_files = []
    
    for i in range(3):  # Create 3 test images
        # Create a test image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some content to make them different
        color = (0, 255 - i * 80, i * 80)  # Different colors
        cv2.rectangle(img, (50 + i * 100, 50), (150 + i * 100, 150), color, -1)
        cv2.putText(img, f"Test Image {i+1}", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add fake detection box
        cv2.rectangle(img, (250, 200), (350, 350), (0, 255, 0), 2)
        cv2.putText(img, f"Person {0.85 + i * 0.05:.2f}", (250, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        cv2.imwrite(temp_file.name, img)
        temp_files.append(temp_file.name)
        
        # Create screenshot data
        screenshot_data = {
            'path': temp_file.name,
            'persons': [{
                'bbox': (250, 200, 350, 350),
                'confidence': 0.85 + i * 0.05,
                'timestamp': i * 3.0
            }],
            'timestamp': i * 3.0,
            'video_path': 'test_video.mp4'
        }
        screenshots_data.append(screenshot_data)
        
        print(f"📸 Created test image {i+1}: {os.path.basename(temp_file.name)}")
    
    print(f"\n📤 Sending {len(screenshots_data)} images as media group...")
    
    # Test the media group sending
    sent_count = send_detection_media_group(screenshots_data)
    
    if sent_count > 0:
        print(f"✅ Successfully sent {sent_count} images in media group!")
        print("📱 Check your Telegram chat for the media group message")
    else:
        print("❌ Failed to send media group")
    
    # Cleanup temporary files
    print("\n🧹 Cleaning up test files...")
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
            print(f"🗑️ Deleted: {os.path.basename(temp_file)}")
        except Exception as e:
            print(f"⚠️ Could not delete {temp_file}: {e}")
    
    print("\n🎉 Media group test complete!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run: ./install_person_detection.sh")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test error: {e}")
    sys.exit(1)
