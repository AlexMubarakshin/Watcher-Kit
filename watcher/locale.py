#!/usr/bin/env python3
"""
Localization module for Watcher project.
Provides messages in Russian and English based on system locale.
"""

import os
import locale

def get_locale():
    """Get current system locale, default to English if Russian not detected."""
    try:
        loc = locale.getlocale()[0] or locale.getdefaultlocale()[0] or ""
        return "ru" if "ru" in loc.lower() else "en"
    except:
        return "en"

# Message dictionaries
MESSAGES = {
    "en": {
        # Tray app messages
        "status": "📊 Status",
        "open_logs": "📂 Open Logs", 
        "start": "▶️ Start",
        "stop": "⏹ Stop",
        "quit": "Quit",
        "started": "Started",
        "stopped": "Stopped",
        "agents_activated": "Agents activated",
        "agents_stopped": "Agents stopped",
        "capture_not_running": "⚠️ capture_video is not running!",
        
        # Capture video messages
        "camera_not_found": "Camera device {} not found",
        "camera_list": "Available video devices:",
        "ffmpeg_error": "FFmpeg error: {}",
        "capture_completed": "✅ Capture completed: {}",
        "capture_failed": "💥 Video capture failed: {}",
        
        # Merge and send messages
        "no_videos_to_merge": "No videos to merge",
        "merging_videos": "🔍 Found {} videos to merge",
        "merging_start": "⚙️ Starting merge of {} files...", 
        "merge_completed": "✅ Merge completed: {}",
        "merge_failed": "❌ Video merge failed: {}",
        "merge_list_created": "Merge list created: {}",
        "compressing_file": "Starting compression: {}",
        "compression_command": "Compression command: {}",
        "compression_completed": "✅ Compression completed: {}",
        "compression_failed": "❌ Compression failed: {}",
        "telegram_sent": "✅ File sent to Telegram: {}",
        "telegram_failed": "❌ Failed to send to Telegram: {}",
        "telegram_sending": "📤 Sending to Telegram: {}",
        "cleanup_files": "🧹 Cleaning {} temporary files...",
        "script_start": "🚀 Starting merge and send script",
        "script_complete": "🏁 Script completed",
        "insufficient_files": "⏸ Insufficient files to merge. Need at least 2.",
        "send_failed_keep_files": "📭 Telegram send failed. Files will not be deleted.",
        "compression_failed_no_send": "📦 Compression failed. Files will not be sent.",
        
        # Telegram notifications
        "system_startup": "🟢 Watcher system started",
        "system_shutdown": "🔴 Watcher system stopped", 
        "daily_summary": "📊 Daily summary: {} videos captured, {} files sent",
        "storage_warning": "⚠️ Storage space low: {}% remaining",
        "camera_reconnected": "📹 Camera reconnected successfully",
        "large_file_warning": "📦 Large file detected: {} MB",
        
        # Camera testing messages
        "testing_camera_permissions": "Testing camera permissions and access...",
        "camera_permissions_ok": "Camera permissions granted",
        "camera_permissions_denied": "Camera permissions denied or no cameras found",
        "available_cameras": "Available cameras",
        "no_cameras_found": "No cameras found in system",
        "camera_test_timeout": "Camera test timed out",
        "camera_test_error": "Camera test error",
        "testing_specific_camera": "Testing configured camera device: {}",
        "camera_device_works": "Camera device works correctly",
        "camera_device_failed": "Camera device failed to initialize",
        "camera_device_timeout": "Camera device test timed out",
        "camera_device_error": "Camera device test error",
        "camera_troubleshooting": "Camera Troubleshooting Guide",
        "check_camera_connected": "Check that camera is properly connected",
        "check_camera_permissions_macos": "System Settings → Privacy & Security → Camera → Allow Terminal/App",
        "try_different_camera_app": "Try opening camera in another app (Photo Booth, etc.)",
        "restart_computer_camera": "Restart computer if camera is unresponsive",
        "update_camera_drivers": "Update camera drivers if using external camera",
        "current_camera_setting": "Current camera setting in .env",
        "change_camera_setting": "Edit .env file to change CAMERA_DEVICE if needed",
        "camera_diagnostic_start": "Starting Camera Diagnostic",
        "camera_all_good": "Camera system working correctly!",
        "camera_device_issue": "Camera device has issues but permissions OK",
        "camera_permissions_issue": "Camera permissions or access issue",
        "current_settings": "Current Configuration Settings",
        
        # Status messages
        "agents_status": "Agent Status",
        "agent_running": "running",
        "agent_not_running": "not running",
        "last_run": "Last run",
        "never": "never",
        "error": "error",
    },
    
    "ru": {
        # Tray app messages
        "status": "📊 Статус",
        "open_logs": "📂 Открыть логи",
        "start": "▶️ Запустить", 
        "stop": "⏹ Остановить",
        "quit": "Выход",
        "started": "Запущено",
        "stopped": "Остановлено",
        "agents_activated": "Агенты активированы",
        "agents_stopped": "Агенты выгружены",
        "capture_not_running": "⚠️ capture_video не запущен!",
        
        # Capture video messages
        "camera_not_found": "Камера устройство {} не найдено",
        "camera_list": "Доступные видео устройства:",
        "ffmpeg_error": "❌ Ошибка FFmpeg: {}",
        "capture_completed": "✅ Запись завершена: {}",
        "capture_failed": "💥 Не удалось записать видео: {}",
        
        # Merge and send messages
        "no_videos_to_merge": "Нет видео для объединения",
        "merging_videos": "Объединяю {} видео...",
        "merging_start": "⚙️ Начинаю объединение {} файлов...", 
        "merge_completed": "✅ Объединение завершено: {}",
        "merge_failed": "❌ Не удалось объединить видео: {}",
        "merge_list_created": "Список для объединения создан: {}",
        "compressing_file": "Начинаю сжатие: {}",
        "compression_command": "Команда сжатия: {}",
        "compression_completed": "✅ Сжатие завершено: {}",
        "compression_failed": "❌ Сжатие не удалось: {}",
        "telegram_sent": "✅ Файл отправлен в Telegram: {}",
        "telegram_failed": "❌ Не удалось отправить в Telegram: {}",
        "telegram_sending": "📤 Отправка в Telegram: {}",
        "cleanup_files": "🧹 Очистка {} временных файлов...",
        "script_start": "🚀 Запуск скрипта объединения и отправки",
        "script_complete": "🏁 Скрипт завершен",
        "insufficient_files": "⏸ Недостаточно файлов для объединения. Нужны как минимум 2.",
        "send_failed_keep_files": "📭 Отправка в Telegram не удалась. Файлы не будут удалены.",
        "compression_failed_no_send": "📦 Сжатие не удалось. Файлы не будут отправлены.",
        
        # Telegram notifications
        "system_startup": "🟢 Система Watcher запущена",
        "system_shutdown": "🔴 Система Watcher остановлена", 
        "daily_summary": "📊 Ежедневная сводка: {} видео записано, {} файлов отправлено",
        "storage_warning": "⚠️ Мало места на диске: {}% свободно",
        "camera_reconnected": "📹 Камера успешно переподключена",
        "large_file_warning": "📦 Обнаружен большой файл: {} МБ",
        
        # Camera testing messages
        "testing_camera_permissions": "Тестирование разрешений и доступа к камере...",
        "camera_permissions_ok": "Разрешения для камеры предоставлены",
        "camera_permissions_denied": "Доступ к камере запрещен или камеры не найдены",
        "available_cameras": "Доступные камеры",
        "no_cameras_found": "Камеры не найдены в системе",
        "camera_test_timeout": "Тайм-аут тестирования камеры",
        "camera_test_error": "Ошибка тестирования камеры",
        "testing_specific_camera": "Тестирование настроенного устройства камеры: {}",
        "camera_device_works": "Устройство камеры работает корректно",
        "camera_device_failed": "Не удалось инициализировать устройство камеры",
        "camera_device_timeout": "Тайм-аут тестирования устройства камеры",
        "camera_device_error": "Ошибка тестирования устройства камеры",
        "camera_troubleshooting": "Руководство по устранению проблем с камерой",
        "check_camera_connected": "Проверьте, что камера правильно подключена",
        "check_camera_permissions_macos": "Системные настройки → Конфиденциальность → Камера → Разрешить Терминал/Приложение",
        "try_different_camera_app": "Попробуйте открыть камеру в другом приложении (Photo Booth и т.д.)",
        "restart_computer_camera": "Перезагрузите компьютер, если камера не отвечает",
        "update_camera_drivers": "Обновите драйверы камеры, если используете внешнюю камеру",
        "current_camera_setting": "Текущая настройка камеры в .env",
        "change_camera_setting": "Отредактируйте файл .env для изменения CAMERA_DEVICE при необходимости",
        "camera_diagnostic_start": "Запуск диагностики камеры",
        "camera_all_good": "Система камеры работает корректно!",
        "camera_device_issue": "Устройство камеры имеет проблемы, но разрешения в порядке",
        "camera_permissions_issue": "Проблема с разрешениями или доступом к камере",
        "current_settings": "Текущие настройки конфигурации",
        
        # Status messages
        "agents_status": "Статус агентов",
        "agent_running": "запущен",
        "agent_not_running": "не запущен",
        "last_run": "Последний запуск",
        "never": "никогда",
        "error": "ошибка",
    }
}

def _(key, *args):
    """Get localized message by key with optional formatting arguments."""
    current_locale = get_locale()
    message = MESSAGES[current_locale].get(key, MESSAGES["en"].get(key, key))
    
    if args:
        try:
            return message.format(*args)
        except:
            return message
    return message
