# Watcher - Упрощенна├── 🚀 setup.sh                   # Установка
├── ⚙️ install_launchd.sh         # Включить агентов
├── 🗑 uninstall_launchd.sh       # Выключить агентов
├── 🧪 system_test.py             # Тест
├── 📄 .env                       # Настройки
├── 🌍 locale.sh                  # Локализация скриптов
├── 📚 README.md                  # Документация (EN)
├── 📚 README_rus.md              # Документация (RU)
├── 📁 PROJECT_STRUCTURE.md       # Структура (EN)
└── 📁 PROJECT_STRUCTURE_rus.md   # Структура (RU)ктура

```
watcher/                          # Основной проект
├── 📁 watcher/                   # Python пакет
│   ├── __init__.py               # Инициализация
│   ├── capture_video.py          # 🎥 Захват видео
│   ├── merge_and_send.py         # 🎞 Объединение и Telegram
│   ├── tray_app.py               # 🖥 Системный трей
│   ├── logger.py                 # 🪵 Логирование
│   ├── status.py                 # 📊 Статус агентов
│   ├── config.py                 # ⚙️ Конфигурация
│   └── locale.py                 # 🌐 Локализация
├── 📁 launchd/                   # macOS агенты
│   ├── com.watcher.capture.plist
│   └── com.watcher.merge_send.plist
├── 📁 logs/                      # Логи (авто)
├── 📁 videos/                    # Видео (авто)  
├── 📁 merged/                    # Готовые (авто)
├── 🔧 setup.py                   # Пакет
├── 📦 requirements.txt           # Зависимости
├── � setup.sh                   # Установка
├── ⚙️ install_launchd.sh         # Включить агентов
├── 🗑 uninstall_launchd.sh       # Выключить агентов
├── 🧪 system_test.py             # Тест
├──  .env                       # Настройки
└── 📚 README.md                  # Документация
```

## Команды

- `./setup.sh` → полная установка
- `watcher-devices` → список камер
- `watcher-capture` → захват видео
- `watcher-tray` → системный трей
- `watcher-status` → статус агентов

## Особенности

### 🌐 Локализация
- Все Python скрипты поддерживают русский и английский язык
- Определение языка по системной локали
- Bash скрипты используют `locale.sh` для сообщений

### 📦 Упрощенная структура
- Весь код в пакете `watcher/`
- Унифицированные имена агентов (`com.watcher.*`)
- Централизованная конфигурация в `.env`

### 🔧 Простая установка
- Один скрипт `setup.sh` для всего
- Интерактивная настройка агентов
- Автоматическая проверка зависимостей

---

📖 **English version:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
