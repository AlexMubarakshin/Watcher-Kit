from setuptools import setup, find_packages

setup(
    name="watcher",
    version="1.0.0",
    description="Python-based video surveillance tool with periodic capture and Telegram upload",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rumps", 
        "python-dotenv",
        "opencv-python",
        "ultralytics",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "watcher-tray=watcher.tray_app:main",
            "watcher-capture=watcher.capture_video:main", 
            "watcher-merge=watcher.merge_and_send:main",
            "watcher-status=watcher.status:main",
            "watcher-devices=watcher.capture_video:list_devices",
            "watcher-camera-test=watcher.camera_test:main",
            "watcher-person-detect=watcher.person_detection:main"
        ]
    },
    python_requires=">=3.7",
)