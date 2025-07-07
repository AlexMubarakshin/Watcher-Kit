#!/usr/bin/env python3

"""
Quick test script to verify YOLO model loading works correctly
"""

import sys
import os

# Add the watcher module to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from watcher.merge_and_send import load_yolo_model, DETECTION_AVAILABLE
    
    print("🤖 YOLO Model Loading Test")
    print("=" * 30)
    
    if not DETECTION_AVAILABLE:
        print("❌ Detection dependencies not available")
        print("💡 Run: ./install_person_detection.sh")
        sys.exit(1)
    
    print("📦 Testing model loading...")
    
    try:
        model = load_yolo_model()
        print("✅ Model loaded successfully!")
        print(f"📋 Model info: {type(model)}")
        
        # Test model with a simple prediction
        print("🧪 Testing model inference...")
        import numpy as np
        test_image = np.zeros((640, 640, 3), dtype=np.uint8)  # Black test image
        results = model(test_image, verbose=False)
        print("✅ Model inference test passed!")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Run: ./download_yolo_model.sh")
        print("   2. Check internet connection")
        print("   3. See YOLO_TROUBLESHOOTING.md")
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("💡 Person detection is ready to use.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run: ./install_person_detection.sh")
    sys.exit(1)
