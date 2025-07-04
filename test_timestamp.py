#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/Users/alexdev/projects/personal/watcher')

# Set test duration
os.environ['DURATION'] = '5'

from watcher.capture_video import capture
print('🎬 Starting 5-second test recording with timestamp overlay...')
try:
    capture()
    print('✅ Test recording completed')
except Exception as e:
    print(f'❌ Error: {e}')
