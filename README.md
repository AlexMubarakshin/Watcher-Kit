# Watcher (Video Surveillance Toolkit)

## 🎯 Purpose

Watcher is a local video surveillance system for macOS designed for emergency services or personal monitoring that:

- captures video from external USB cameras
- periodically merges and compresses them into a single file
- sends it to a Telegram channel
- works completely offline and autonomously as a background agent, visible in the macOS menu bar

## 📂 Structure and Script Roles

The project is divided into several isolated components, each performing one responsible task:

### 1. capture_video.py

**⏱ What it does:** Records 1-minute video files from external camera (every minute).

**📦 Features:**
- Uses ffmpeg through subprocess
- Works with external camera (AVFoundation, indexed)
- Saves .mp4 to videos/
- Supports logging with rotation

### 2. merge_and_send.py

**🎞 What it does:**
- Merges accumulated .mp4 videos together
- Compresses them to save traffic
- Sends to Telegram channel
- Deletes old files on success

**📦 Features:**
- Uses ffmpeg for merging and compression
- Triggers on schedule (e.g., every 10 minutes)
- Sends errors back to Telegram via notify_telegram()

### 3. tray_app.py

**🖥 What it does:**
- Shows icon in macOS menu bar
- Allows manual control of background tasks (start, stop, status)
- Encapsulates interaction with launchctl
- Allows opening logs and monitoring agent status

**📦 Based on:** rumps (Python-to-macOS MenuBar framework)

### 4. logger.py

**🪵 What it does:**
- Creates loggers that write to file and console
- Supports log rotation
- Implements notify_telegram(message) — universal error sending

### 5. config.py + .env

**⚙️ What it does:**
- Stores all paths, camera settings, and Telegram API
- Secrets (TELEGRAM_BOT_TOKEN, CHAT_ID) — through .env, excluded from Git

## 🚀 Installation

### Quick

```bash
./setup.sh
```

### Manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## ⚙️ Usage

```bash
watcher-devices     # List cameras
watcher-capture     # Capture video
watcher-tray        # System tray
watcher-status      # Status
watcher-camera-test # Test camera access and permissions
```

### System Tray

After running `watcher-tray`, look for the green 🟢 icon in your macOS menu bar (top right). 

**If you don't see the tray icon:**
1. Check System Settings → Privacy & Security → Accessibility
2. Allow Terminal or your app to control the computer
3. Try running: `watcher-tray` again

The tray menu provides:
- 📊 Status - Check if agents are running
- 📂 Open Logs - View system logs  
- ▶️ Start - Start background agents
- ⏹ Stop - Stop background agents

### Automatic operation

```bash
./install_launchd.sh    # Enable
./uninstall_launchd.sh  # Disable
```

## 🗂 Settings

`.env` file:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
CAMERA_DEVICE=0
```

## 🔧 Diagnostics

```bash
watcher-devices         # List cameras
watcher-status          # Agent status
watcher-camera-test     # Full camera diagnostic
python system_test.py   # System test
```

## 🗑 Removal

```bash
./uninstall_launchd.sh  # Stop agents
rm -rf .venv            # Remove environment
```

---

📖 **Russian documentation:** [README_rus.md](README_rus.md)  
📁 **Project structure:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
