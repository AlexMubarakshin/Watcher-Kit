#!/usr/bin/env python3
"""
Test script for Telegram file size limits and compression
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from watcher.merge_and_send import send_to_telegram, compress_video
from watcher.config import MAX_FILE_SIZE_MB

def test_file_size_limits():
    """Test file size checking and compression"""
    
    # Check if there are any compressed files in merged directory
    merged_dir = "/Users/alexdev/projects/personal/watcher/merged"
    if not os.path.exists(merged_dir):
        print("❌ Merged directory not found")
        return
    
    # Find the latest compressed file
    compressed_files = [f for f in os.listdir(merged_dir) if f.startswith("compressed_") and f.endswith(".mp4")]
    if not compressed_files:
        print("❌ No compressed files found for testing")
        return
    
    latest_file = os.path.join(merged_dir, sorted(compressed_files)[-1])
    print(f"📁 Testing with file: {latest_file}")
    
    # Check file size
    file_size_mb = os.path.getsize(latest_file) / (1024 * 1024)
    print(f"📏 File size: {file_size_mb:.1f} MB")
    print(f"📏 Max allowed size: {MAX_FILE_SIZE_MB} MB")
    
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(f"⚠️ File exceeds limit by {file_size_mb - MAX_FILE_SIZE_MB:.1f} MB")
    else:
        print(f"✅ File is within limit ({MAX_FILE_SIZE_MB - file_size_mb:.1f} MB under)")
    
    # Test sending to Telegram (this will apply emergency compression if needed)
    print("\n🚀 Testing Telegram send (with size validation)...")
    success = send_to_telegram(latest_file, MAX_FILE_SIZE_MB)
    
    if success:
        print("✅ File sent successfully!")
    else:
        print("❌ File send failed")

if __name__ == "__main__":
    test_file_size_limits()
