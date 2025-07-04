# Watcher - Simplified Structure

```
watcher/                          # Main project
├── 📁 watcher/                   # Python package
│   ├── __init__.py               # Initialization
│   ├── capture_video.py          # 🎥 Video capture
│   ├── merge_and_send.py         # 🎞 Merge and Telegram
│   ├── tray_app.py               # 🖥 System tray
│   ├── logger.py                 # 🪵 Logging
│   ├── status.py                 # 📊 Agent status
│   ├── config.py                 # ⚙️ Configuration
│   └── locale.py                 # 🌐 Localization
├── 📁 launchd/                   # macOS agents
│   ├── com.watcher.capture.plist
│   └── com.watcher.merge_send.plist
├── 📁 logs/                      # Logs (auto)
├── 📁 videos/                    # Videos (auto)  
├── 📁 merged/                    # Ready files (auto)
├── 🔧 setup.py                   # Package
├── 📦 requirements.txt           # Dependencies
├── 🚀 setup.sh                   # Installation
├── ⚙️ install_launchd.sh         # Enable agents
├── 🗑 uninstall_launchd.sh       # Disable agents
├── 🧪 system_test.py             # Test
├── 📄 .env                       # Settings
├── 🌍 locale.sh                  # Script localization
├── 📚 README.md                  # Documentation (EN)
├── 📚 README_rus.md              # Documentation (RU)
├── 📁 PROJECT_STRUCTURE.md       # Structure (EN)
└── 📁 PROJECT_STRUCTURE_rus.md   # Structure (RU)
```

## Commands

- `./setup.sh` → full installation
- `watcher-devices` → list cameras
- `watcher-capture` → capture video
- `watcher-tray` → system tray
- `watcher-status` → agent status

## Features

### 🌐 Localization
- All Python scripts support Russian and English languages
- Language detection based on system locale
- Bash scripts use `locale.sh` for messages

### 📦 Simplified Structure
- All code in `watcher/` package
- Unified agent names (`com.watcher.*`)
- Centralized configuration in `.env`

### 🔧 Easy Installation
- Single `setup.sh` script for everything
- Interactive agent setup
- Automatic dependency checking

---

📖 **Russian version:** [PROJECT_STRUCTURE_rus.md](PROJECT_STRUCTURE_rus.md)
