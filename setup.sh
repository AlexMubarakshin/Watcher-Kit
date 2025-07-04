#!/bin/bash

# Load localization
source "$(dirname "$0")/locale.sh"

# Full installation and setup of Watcher
echo "$(get_message "setup_start")"

# Create directories
echo "$(get_message "creating_dirs")"
mkdir -p logs videos merged

# Virtual environment
if [ ! -d ".venv" ]; then
    echo "$(get_message "creating_venv")"
    python3 -m venv .venv
fi

# Package installation
echo "$(get_message "installing_package")"
source .venv/bin/activate
pip install -e .

# Configuration
if [ ! -f ".env" ]; then
    echo "$(get_message "copying_config")"
    cp .env.example .env
    echo "$(get_message "edit_config")"
fi

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "$(get_message "ffmpeg_not_found")"
    exit 1
fi

# Test camera access
echo "$(get_message "testing_camera")"
source .venv/bin/activate

# Test camera with improved detection
python3 -c "
import subprocess
import sys
try:
    cmd = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    print('📹 Available cameras:')
    # ffmpeg outputs device list to stderr
    stderr_output = result.stderr
    print(stderr_output)
    
    # Check if any video devices are found
    if 'AVFoundation video devices:' in stderr_output and '] [' in stderr_output:
        print('\n✅ Camera devices detected successfully')
        sys.exit(0)
    else:
        print('\n⚠️ No camera devices found in output')
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    print('⚠️ Camera detection timed out')
    sys.exit(1)
except Exception as e:
    print(f'💥 Camera detection error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "$(get_message "camera_found")"
else
    echo "$(get_message "camera_not_accessible")"
    echo "$(get_message "check_camera_connection")"
    echo ""
    echo "📋 Manual camera test: Run 'watcher-devices' to check cameras"
fi

echo ""
echo "$(get_message "install_agents_question")"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "$(get_message "installing_agents")"
    ./install_launchd.sh
else
    echo "$(get_message "skipping_agents")"
fi

echo ""
echo "$(get_message "setup_complete")"
echo ""
echo "$(get_message "commands"):"
echo "  watcher-devices     - $(get_message "list_cameras")"
echo "  watcher-capture     - $(get_message "capture_video")"  
echo "  watcher-tray        - $(get_message "system_tray")"
echo "  watcher-status      - $(get_message "agent_status")"
echo "  watcher-camera-test - Test camera access and permissions"
