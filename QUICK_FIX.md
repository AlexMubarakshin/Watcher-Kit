# Quick Troubleshooting Reference

## 🧪 Test Media Group Feature
```bash
python test_media_group.py
```

## ❌ Error: `No module named '_lzma'`
```bash
./setup_enhanced_python.sh
```

## ❌ Error: YOLO model download failed
```bash
./download_yolo_model.sh
```

## ❌ Error: `No module named 'cv2'`
```bash
source .venv/bin/activate
./install_person_detection.sh
```

## ❌ Error: `No module named 'ultralytics'`
```bash
source .venv/bin/activate
pip install ultralytics torch
```

## 🔍 General Diagnostics
```bash
./diagnose_python.py
```

## 🧪 Test Everything
```bash
python test_yolo_model.py
```

## 🔧 Complete Reset & Setup
```bash
rm -rf .venv
./setup_enhanced_python.sh
```

## ⚠️ Disable Person Detection
Add to `.env`:
```
ENABLE_PERSON_DETECTION=false
```

## 📞 Need More Help?
1. Check [PYTHON_TROUBLESHOOTING.md](PYTHON_TROUBLESHOOTING.md)
2. Check [YOLO_TROUBLESHOOTING.md](YOLO_TROUBLESHOOTING.md)
3. Run `./diagnose_python.py` for detailed analysis
