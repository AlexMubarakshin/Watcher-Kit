#!/usr/bin/env python3
# config.py

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Корневая директория проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
MERGED_DIR = os.path.join(BASE_DIR, "merged")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Настройки камеры и записи (загружаются из .env файла)
FPS = int(os.getenv("FPS", "30"))  # Кадры в секунду
RESOLUTION = os.getenv("RESOLUTION", "1280x720")  # Разрешение видео
DURATION = int(os.getenv("DURATION", "55"))  # Длительность записи в секундах 
CAMERA_DEVICE = os.getenv("CAMERA_DEVICE", "auto")  # Устройство камеры: "auto", "0", "1", etc.

# Настройки наложения времени на видео
SHOW_TIMESTAMP = os.getenv("SHOW_TIMESTAMP", "true").lower() == "true"
TIMESTAMP_POSITION = os.getenv("TIMESTAMP_POSITION", "top-right")
TIMESTAMP_FONT_SIZE = int(os.getenv("TIMESTAMP_FONT_SIZE", "24"))

# Для списка доступных камер: ffmpeg -f avfoundation -list_devices true -i ""