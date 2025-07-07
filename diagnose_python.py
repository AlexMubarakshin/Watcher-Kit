#!/usr/bin/env python3

"""
Python Environment Diagnostic Script for Watcher
Helps identify and troubleshoot Python-related issues
"""

import sys
import os
import platform
import subprocess

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def check_python_info():
    print_header("Python Information")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Python Path: {sys.path[:3]}...")  # Show first 3 paths

def check_virtual_env():
    print_header("Virtual Environment")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        print(f"Virtual env path: {sys.prefix}")
        if 'VIRTUAL_ENV' in os.environ:
            print(f"VIRTUAL_ENV: {os.environ['VIRTUAL_ENV']}")
    else:
        print("⚠️ NOT running in virtual environment")
        print("💡 Consider using: python -m venv .venv && source .venv/bin/activate")

def check_critical_modules():
    print_header("Critical Module Check")
    
    modules_to_check = [
        ('_lzma', 'LZMA compression'),
        ('cv2', 'OpenCV'),
        ('ultralytics', 'YOLOv8'),
        ('numpy', 'NumPy'),
        ('requests', 'HTTP requests'),
        ('PIL', 'Pillow image processing'),
        ('torch', 'PyTorch (for YOLO)'),
    ]
    
    for module, description in modules_to_check:
        try:
            __import__(module)
            print(f"✅ {module:12} - {description}")
        except ImportError as e:
            print(f"❌ {module:12} - {description} - ERROR: {e}")
        except Exception as e:
            print(f"⚠️ {module:12} - {description} - WARNING: {e}")

def check_python_build():
    print_header("Python Build Information")
    
    # Check if Python was compiled with required modules
    try:
        import sysconfig
        print(f"Python build date: {platform.python_build()}")
        print(f"Python compiler: {platform.python_compiler()}")
        
        # Check for common build flags
        config_vars = sysconfig.get_config_vars()
        if config_vars:
            print(f"CONFIG_ARGS: {config_vars.get('CONFIG_ARGS', 'N/A')[:100]}...")
    except Exception as e:
        print(f"⚠️ Could not get build info: {e}")

def check_homebrew_python():
    print_header("Homebrew Python Check")
    
    try:
        result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Homebrew is installed")
            
            # Check if Python is installed via Homebrew
            result = subprocess.run(['brew', 'list', 'python@3.9'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Python 3.9 installed via Homebrew")
            else:
                result = subprocess.run(['brew', 'list', 'python@3.11'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Python 3.11 installed via Homebrew")
                else:
                    print("❌ Python not installed via Homebrew")
                    print("💡 Consider: brew install python")
        else:
            print("❌ Homebrew not installed")
            print("💡 Install from: https://brew.sh/")
    except FileNotFoundError:
        print("❌ Homebrew not found in PATH")
        print("💡 Install from: https://brew.sh/")

def check_pyenv():
    print_header("pyenv Check")
    
    try:
        result = subprocess.run(['pyenv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pyenv is installed: {result.stdout.strip()}")
            
            # Check available Python versions
            result = subprocess.run(['pyenv', 'versions'], capture_output=True, text=True)
            if result.returncode == 0:
                print("Available Python versions:")
                for line in result.stdout.strip().split('\n')[:5]:  # Show first 5
                    print(f"  {line}")
        else:
            print("❌ pyenv not working properly")
    except FileNotFoundError:
        print("❌ pyenv not found in PATH")
        print("💡 Install from: https://github.com/pyenv/pyenv")

def run_lzma_test():
    print_header("LZMA Module Test")
    
    try:
        import _lzma
        print("✅ _lzma module is available")
        
        # Test LZMA functionality
        import lzma
        test_data = b"Hello, World! This is a test for LZMA compression."
        compressed = lzma.compress(test_data)
        decompressed = lzma.decompress(compressed)
        
        if decompressed == test_data:
            print("✅ LZMA compression/decompression works")
        else:
            print("❌ LZMA compression test failed")
            
    except ImportError as e:
        print(f"❌ _lzma module not available: {e}")
        print("\n💡 This is usually caused by:")
        print("   - Using system Python on macOS")
        print("   - Incomplete Python installation")
        print("   - Missing development libraries during Python build")
        print("\n🔧 Recommended solutions:")
        print("   1. Install Python via Homebrew: brew install python")
        print("   2. Use pyenv: pyenv install 3.9.16")
        print("   3. Use conda: conda install python")

def provide_recommendations():
    print_header("Recommendations")
    
    # Check current Python executable
    if '/usr/bin/python' in sys.executable:
        print("⚠️ You're using system Python - this often causes issues")
        print("💡 Recommended: Switch to Homebrew or pyenv Python")
    elif 'homebrew' in sys.executable or '/opt/homebrew' in sys.executable:
        print("✅ Using Homebrew Python - good choice!")
    elif '.pyenv' in sys.executable:
        print("✅ Using pyenv Python - good choice!")
    elif 'conda' in sys.executable or 'anaconda' in sys.executable:
        print("✅ Using Conda Python - should work well!")
    else:
        print(f"ℹ️ Using Python from: {sys.executable}")
    
    print("\n🔧 If you're having LZMA issues, try:")
    print("   1. brew install python && brew link python")
    print("   2. Create new venv: python3 -m venv .venv")
    print("   3. Activate: source .venv/bin/activate")
    print("   4. Install deps: ./install_person_detection.sh")

def main():
    print("🔍 Watcher Python Environment Diagnostics")
    print("==========================================")
    
    check_python_info()
    check_virtual_env()
    check_critical_modules()
    check_python_build()
    check_homebrew_python()
    check_pyenv()
    run_lzma_test()
    provide_recommendations()
    
    print("\n" + "="*50)
    print(" Diagnostic Complete")
    print("="*50)

if __name__ == "__main__":
    main()
