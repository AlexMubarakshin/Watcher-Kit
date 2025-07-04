#!/usr/bin/env python3
"""
Camera diagnostic utility for Watcher
Утилита диагностики камеры для Watcher
"""

import subprocess
import sys
import os
from watcher.config import CAMERA_DEVICE
from watcher.locale import _

def test_camera_permissions():
    """Test if camera permissions are granted"""
    print("🔍 " + _("testing_camera_permissions"))
    
    try:
        # Test basic ffmpeg camera access
        cmd = [
            'ffmpeg', 
            '-f', 'avfoundation',
            '-list_devices', 'true', 
            '-i', ''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        # Check output for video devices
        if 'AVFoundation video devices:' in result.stderr:
            print("✅ " + _("camera_permissions_ok"))
            
            # Parse and show available devices
            lines = result.stderr.split('\n')
            device_lines = [line for line in lines if '] [' in line and 'video devices' not in line]
            
            if device_lines:
                print("\n📹 " + _("available_cameras") + ":")
                for line in device_lines:
                    if 'video devices' not in line and '] [' in line:
                        print(f"  {line.strip()}")
                return True
            else:
                print("⚠️ " + _("no_cameras_found"))
                return False
        else:
            print("❌ " + _("camera_permissions_denied"))
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ " + _("camera_test_timeout"))
        return False
    except Exception as e:
        print(f"💥 " + _("camera_test_error") + f": {e}")
        return False

def test_specific_camera():
    """Test access to the configured camera device"""
    from watcher.capture_video import get_preferred_camera
    
    # Get actual camera device to use
    if CAMERA_DEVICE.lower() == "auto":
        actual_device = get_preferred_camera()
        print(f"\n🤖 Auto mode detected, using preferred camera: {actual_device}")
    else:
        actual_device = CAMERA_DEVICE
    
    print(f"🎯 " + _("testing_specific_camera", actual_device))
    
    try:
        # Try to get just device information first
        info_cmd = [
            'ffmpeg',
            '-hide_banner',
            '-f', 'avfoundation',
            '-i', str(actual_device),
            '-frames:v', '1',
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=15)
        
        # Check different types of errors
        if result.returncode == 0:
            print("✅ " + _("camera_device_works"))
            return True
        elif "Permission denied" in result.stderr or "not permitted" in result.stderr:
            print("🔒 Camera access permission denied - check System Preferences → Privacy & Security → Camera")
            return False
        elif "Device or resource busy" in result.stderr:
            print("📹 Camera is in use by another application")
            return False
        elif "Input/output error" in result.stderr:
            print("⚠️ Camera hardware access issue detected")
            print("� This often means:")
            print("   • Camera access not granted in System Preferences")
            print("   • Camera is being used by another app")
            print("   • Camera drivers need updating")
            
            # Show the available formats/resolutions from error output
            if "fps" in result.stderr:
                print("\n📹 Detected camera formats:")
                for line in result.stderr.split('\n'):
                    if '@' in line and 'fps' in line:
                        print(f"   {line.strip()}")
            return False
        else:
            print("❌ " + _("camera_device_failed"))
            print(f"Error details: {result.stderr[-400:] if result.stderr else 'Unknown error'}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ " + _("camera_device_timeout"))
        return False
    except Exception as e:
        print(f"💥 " + _("camera_device_error") + f": {e}")
        return False

def show_camera_help():
    """Show help for camera issues"""
    print("\n" + "="*50)
    print("🆘 " + _("camera_troubleshooting"))
    print("="*50)
    
    print("\n1. " + _("check_camera_connected"))
    print("2. " + _("check_camera_permissions_macos"))
    print("3. " + _("try_different_camera_app"))
    print("4. " + _("restart_computer_camera"))
    print("5. " + _("update_camera_drivers"))
    
    print(f"\n⚙️ " + _("current_camera_setting") + f": {CAMERA_DEVICE}")
    print("📝 " + _("change_camera_setting"))

def show_current_settings():
    """Show current configuration settings"""
    from watcher.config import FPS, RESOLUTION, DURATION, CAMERA_DEVICE
    
    print("\n⚙️ " + _("current_settings"))
    print("=" * 40)
    print(f"📹 Camera Device: {CAMERA_DEVICE}")
    print(f"🎬 FPS: {FPS}")
    print(f"📐 Resolution: {RESOLUTION}")
    print(f"⏱ Duration: {DURATION} seconds")
    
    if CAMERA_DEVICE.lower() == "auto":
        print("\n🤖 Auto mode: Will prefer external cameras over built-in cameras")

def main():
    """Run complete camera diagnostic"""
    print("🔬 " + _("camera_diagnostic_start"))
    print("="*60)
    
    # Show current settings
    show_current_settings()
    
    # Test 1: Basic permissions and device list
    permissions_ok = test_camera_permissions()
    
    # Test 2: Specific camera device
    if permissions_ok:
        device_ok = test_specific_camera()
        
        if device_ok:
            print(f"\n🎉 " + _("camera_all_good"))
            return 0
        else:
            print(f"\n⚠️ " + _("camera_device_issue"))
    else:
        print(f"\n❌ " + _("camera_permissions_issue"))
    
    # Show troubleshooting help
    show_camera_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
