# 📹 Camera Troubleshooting Guide / Руководство по устранению проблем с камерой

## 🔍 Quick Diagnosis / Быстрая диагностика

### English
Run the camera diagnostic tool:
```bash
watcher-camera-test
```

This will test:
- Camera permissions
- Available devices
- Specific camera access

### Русский
Запустите диагностику камеры:
```bash
watcher-camera-test
```

Это проверит:
- Разрешения для камеры
- Доступные устройства  
- Доступ к конкретной камере

## 🚨 Common Issues / Распространённые проблемы

### 1. "Camera not accessible" / "Камера недоступна"

**English:**
- **Cause:** macOS camera permissions not granted
- **Solution:** 
  1. Go to System Settings → Privacy & Security → Camera
  2. Enable access for Terminal or your shell app
  3. Restart terminal and try again

**Русский:**
- **Причина:** Не предоставлены разрешения камеры в macOS
- **Решение:**
  1. Перейти в Системные настройки → Конфиденциальность → Камера
  2. Включить доступ для Терминала или вашего приложения
  3. Перезапустить терминал и попробовать снова

### 2. "No cameras found" / "Камеры не найдены"

**English:**
- **Cause:** No cameras connected or drivers missing
- **Solutions:**
  - Check USB connections for external cameras
  - Try built-in camera first
  - Test camera in Photo Booth or other app
  - Update camera drivers

**Русский:**
- **Причина:** Нет подключённых камер или отсутствуют драйверы
- **Решения:**
  - Проверьте USB подключения для внешних камер
  - Сначала попробуйте встроенную камеру
  - Протестируйте камеру в Photo Booth или другом приложении
  - Обновите драйверы камеры

### 3. "Camera device failed" / "Устройство камеры не работает"

**English:**
- **Cause:** Wrong camera device number in configuration
- **Solutions:**
  1. Run `watcher-devices` to see available cameras
  2. Note the device number (e.g., [0], [1], [2])
  3. Edit `.env` file and set `CAMERA_DEVICE=X` with correct number
  4. Test again with `watcher-camera-test`

**Русский:**
- **Причина:** Неверный номер устройства камеры в конфигурации
- **Решения:**
  1. Запустите `watcher-devices` для просмотра доступных камер
  2. Запишите номер устройства (например, [0], [1], [2])
  3. Отредактируйте файл `.env` и установите `CAMERA_DEVICE=X` с правильным номером
  4. Протестируйте снова с помощью `watcher-camera-test`

## 🔧 Advanced Troubleshooting / Расширенное устранение проблем

### English
1. **Check ffmpeg installation:**
   ```bash
   ffmpeg -version
   ```

2. **Test manual camera access:**
   ```bash
   ffmpeg -f avfoundation -list_devices true -i ""
   ```

3. **Test specific camera:**
   ```bash
   ffmpeg -f avfoundation -i "0" -t 5 -y test.mp4
   ```

### Русский
1. **Проверьте установку ffmpeg:**
   ```bash
   ffmpeg -version
   ```

2. **Протестируйте доступ к камере вручную:**
   ```bash
   ffmpeg -f avfoundation -list_devices true -i ""
   ```

3. **Протестируйте конкретную камеру:**
   ```bash
   ffmpeg -f avfoundation -i "0" -t 5 -y test.mp4
   ```

## 📱 Contact Support / Поддержка

If issues persist, include the output of `watcher-camera-test` when reporting the problem.

Если проблемы продолжаются, включите вывод `watcher-camera-test` при сообщении о проблеме.
