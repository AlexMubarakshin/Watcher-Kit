#!/usr/bin/env python3
"""
Простой тест Watcher
"""

def main():
    print("🧪 Тест Watcher...")
    
    try:
        # Тест импорта
        from watcher.tray_app import VideoTrayApp
        from watcher.config import CAMERA_DEVICE
        print("✅ Импорт - OK")
        
        # Тест команд
        import subprocess
        result = subprocess.run(['which', 'watcher-status'], capture_output=True)
        if result.returncode == 0:
            print("✅ Команды - OK")
        else:
            print("❌ Команды - не найдены")
            return False
        
        # Тест ffmpeg
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True)
        if result.returncode == 0:
            print("✅ ffmpeg - OK")
        else:
            print("❌ ffmpeg - не найден")
            return False
            
        print("🎉 Всё работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    main()
