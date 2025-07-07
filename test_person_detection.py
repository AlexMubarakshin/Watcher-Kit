#!/usr/bin/env python3
"""
Test script to verify person detection dependencies
"""

def test_imports():
    """Test if required packages can be imported"""
    try:
        print("🔍 Testing OpenCV...")
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV not available: {e}")
        return False
    
    try:
        print("🔍 Testing NumPy...")
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy not available: {e}")
        return False
    
    try:
        print("🔍 Testing Ultralytics YOLO...")
        from ultralytics import YOLO
        print("✅ Ultralytics available")
    except ImportError as e:
        print(f"❌ Ultralytics not available: {e}")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    try:
        import cv2
        print("📹 Testing camera access...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera working: {frame.shape}")
                cap.release()
                return True
            else:
                print("❌ Cannot read from camera")
                cap.release()
                return False
        else:
            print("❌ Cannot open camera")
            return False
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def main():
    print("🧪 Person Detection System Test")
    print("=" * 40)
    
    if test_imports():
        print("\n✅ All dependencies are available!")
        
        if test_camera():
            print("\n🎉 System ready for person detection!")
            print("\n🚀 Next steps:")
            print("1. Run: python person_detect.py --test --preview")
            print("2. Look for a person in the camera view")
            print("3. Check if detection works and screenshot is saved")
        else:
            print("\n⚠️ Camera issues detected")
    else:
        print("\n❌ Missing dependencies")
        print("Run: ./install_person_detection.sh")

if __name__ == "__main__":
    main()
