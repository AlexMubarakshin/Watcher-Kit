#!/usr/bin/env python3
"""
Enhanced notification system for Watcher
Система расширенных уведомлений для Watcher
"""

import os
import shutil
from datetime import datetime
from .locale import _
from .logger import notify_telegram

def check_storage_space(threshold=10):
    """Check available storage space and warn if low"""
    try:
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100
        
        if free_percent < threshold:
            notify_telegram(_("storage_warning", round(free_percent, 1)))
            return False
        return True
    except:
        return True

def get_file_size_mb(filepath):
    """Get file size in megabytes"""
    try:
        return round(os.path.getsize(filepath) / (1024 * 1024), 1)
    except:
        return 0

def notify_file_sent(filepath):
    """Notify about successful file send with size info"""
    file_size = get_file_size_mb(filepath)
    filename = os.path.basename(filepath)
    
    if file_size > 50:  # Large file warning
        notify_telegram(_("large_file_warning", file_size))
    
    notify_telegram(_("telegram_sent", filename))

def notify_system_startup():
    """Notify when system starts"""
    notify_telegram(_("system_startup"))

def notify_system_shutdown():
    """Notify when system stops"""
    notify_telegram(_("system_shutdown"))

def notify_camera_reconnected():
    """Notify when camera is reconnected after failure"""
    notify_telegram(_("camera_reconnected"))

def daily_summary():
    """Send daily summary of activity"""
    try:
        from .config import VIDEO_DIR, MERGED_DIR
        
        # Count files created today
        today = datetime.now().strftime("%Y%m%d")
        
        video_count = 0
        if os.path.exists(VIDEO_DIR):
            video_count = len([f for f in os.listdir(VIDEO_DIR) 
                             if f.startswith(f"video_{today}") and f.endswith(".mp4")])
        
        sent_count = 0
        if os.path.exists(MERGED_DIR):
            sent_count = len([f for f in os.listdir(MERGED_DIR) 
                            if f.startswith(f"compressed_{today}") and f.endswith(".mp4")])
        
        if video_count > 0 or sent_count > 0:
            notify_telegram(_("daily_summary", video_count, sent_count))
            
    except Exception:
        pass  # Don't fail if summary can't be generated
