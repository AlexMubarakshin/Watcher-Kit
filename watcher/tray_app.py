#!/usr/bin/env python3
import os
import rumps
import subprocess
from .logger import notify_telegram
from .status import check as check_service  # наша утилита
from .locale import _

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(PROJECT_DIR, "logs", "merge_send.log")

class VideoTrayApp(rumps.App):
    def __init__(self):
        # Static menu items for proper rumps functionality
        status_text = _("status") 
        logs_text = _("open_logs")
        start_text = _("start")
        stop_text = _("stop")
        quit_text = _("quit")
        
        super(VideoTrayApp, self).__init__("🟢 VideoSurv", menu=[
            status_text,
            logs_text,
            start_text,
            stop_text,
            None,
            quit_text
        ])
        
        # Store menu text for dynamic click handlers
        self.status_text = status_text
        self.logs_text = logs_text  
        self.start_text = start_text
        self.stop_text = stop_text
        self.quit_text = quit_text
        
        self.timer = rumps.Timer(self.refresh_status, 60)
        self.timer.start()

    def refresh_status(self, _=None):
        # Автоуведомление при сбое
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "com.watcher.capture" not in result.stdout:
            notify_telegram(_("capture_not_running"))

    @rumps.clicked("📊 Status")
    @rumps.clicked("📊 Статус")
    def status(self, _):
        running = []
        for label in ["com.watcher.capture", "com.watcher.merge_send"]:
            result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
            running.append(f"{label}: {'✅' if label in result.stdout else '❌'}")
        rumps.alert("\n".join(running))

    @rumps.clicked("📂 Open Logs")
    @rumps.clicked("📂 Открыть логи")
    def open_logs(self, _):
        os.system(f"open {LOG_FILE}")

    @rumps.clicked("▶️ Start")
    @rumps.clicked("▶️ Запустить")
    def start_agents(self, _):
        for plist in os.listdir(os.path.join(PROJECT_DIR, "launchd")):
            path = os.path.join(PROJECT_DIR, "launchd", plist)
            os.system(f"launchctl load -w {path}")
        rumps.notification(_("started"), "", _("agents_activated"))

    @rumps.clicked("⏹ Stop")
    @rumps.clicked("⏹ Остановить")
    def stop_agents(self, _):
        for plist in os.listdir(os.path.join(PROJECT_DIR, "launchd")):
            path = os.path.join(PROJECT_DIR, "launchd", plist)
            os.system(f"launchctl unload {path}")
        rumps.notification(_("stopped"), "", _("agents_stopped"))

    @rumps.clicked("Quit")
    @rumps.clicked("Выход")
    def quit_app(self, _):
        rumps.quit_application()

def main():
    VideoTrayApp().run()

if __name__ == "__main__":
    main()