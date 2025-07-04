#!/bin/bash

# Locale detection and messages (Compatible with bash 3.x)
# Определение локали и сообщений (Совместимо с bash 3.x)

detect_locale() {
    if [[ "$LANG" == *"ru"* ]] || [[ "$LC_ALL" == *"ru"* ]]; then
        echo "ru"
    else
        echo "en"
    fi
}

# Function to get localized message
get_message() {
    local key="$1"
    local locale=$(detect_locale)
    
    case "$key" in
        "setup_start")
            if [ "$locale" = "ru" ]; then
                echo "🚀 Установка Watcher (Система видеонаблюдения)..."
            else
                echo "🚀 Installing Watcher (Video Surveillance Toolkit)..."
            fi
            ;;
        "creating_dirs")
            if [ "$locale" = "ru" ]; then
                echo "📁 Создание директорий..."
            else
                echo "📁 Creating directories..."
            fi
            ;;
        "creating_venv")
            if [ "$locale" = "ru" ]; then
                echo "🐍 Создание виртуального окружения..."
            else
                echo "🐍 Creating virtual environment..."
            fi
            ;;
        "installing_package")
            if [ "$locale" = "ru" ]; then
                echo "📦 Установка пакета..."
            else
                echo "📦 Installing package..."
            fi
            ;;
        "copying_config")
            if [ "$locale" = "ru" ]; then
                echo "⚠️ Копирование примера конфигурации..."
            else
                echo "⚠️ Copying example configuration..."
            fi
            ;;
        "edit_config")
            if [ "$locale" = "ru" ]; then
                echo "📝 Пожалуйста, отредактируйте .env с вашими настройками"
            else
                echo "📝 Please edit .env with your settings"
            fi
            ;;
        "ffmpeg_not_found")
            if [ "$locale" = "ru" ]; then
                echo "❌ ffmpeg не найден. Установите с помощью: brew install ffmpeg"
            else
                echo "❌ ffmpeg not found. Install with: brew install ffmpeg"
            fi
            ;;
        "testing_camera")
            if [ "$locale" = "ru" ]; then
                echo "📹 Тестирование доступа к камере..."
            else
                echo "📹 Testing camera access..."
            fi
            ;;
        "camera_found")
            if [ "$locale" = "ru" ]; then
                echo "✅ Доступ к камере подтвержден"
            else
                echo "✅ Camera access confirmed"
            fi
            ;;
        "camera_not_accessible")
            if [ "$locale" = "ru" ]; then
                echo "⚠️ Камера недоступна или проблема с ffmpeg"
            else
                echo "⚠️ Camera not accessible or ffmpeg issue"
            fi
            ;;
        "check_camera_connection")
            if [ "$locale" = "ru" ]; then
                echo "Проверьте подключение камеры и разрешения"
            else
                echo "Please check camera connection and permissions"
            fi
            ;;
        "install_agents_question")
            if [ "$locale" = "ru" ]; then
                echo "Хотите ли вы установить автоматические агенты? (y/n)"
            else
                echo "Do you want to install automatic agents? (y/n)"
            fi
            ;;
        "installing_agents")
            if [ "$locale" = "ru" ]; then
                echo "⚙️ Установка launchd агентов..."
            else
                echo "⚙️ Installing launchd agents..."
            fi
            ;;
        "skipping_agents")
            if [ "$locale" = "ru" ]; then
                echo "⏩ Пропуск установки агентов"
            else
                echo "⏩ Skipping agent installation"
            fi
            ;;
        "setup_complete")
            if [ "$locale" = "ru" ]; then
                echo "✅ Установка завершена!"
            else
                echo "✅ Installation complete!"
            fi
            ;;
        "commands")
            if [ "$locale" = "ru" ]; then
                echo "Команды:"
            else
                echo "Commands:"
            fi
            ;;
        "list_cameras")
            if [ "$locale" = "ru" ]; then
                echo "Список камер"
            else
                echo "List cameras"
            fi
            ;;
        "capture_video")
            if [ "$locale" = "ru" ]; then
                echo "Захват видео"
            else
                echo "Capture video"
            fi
            ;;
        "system_tray")
            if [ "$locale" = "ru" ]; then
                echo "Системный трей"
            else
                echo "System tray"
            fi
            ;;
        "agent_status")
            if [ "$locale" = "ru" ]; then
                echo "Статус агентов"
            else
                echo "Agent status"
            fi
            ;;
        *)
            echo "$key"  # Return key if not found
            ;;
    esac
}
