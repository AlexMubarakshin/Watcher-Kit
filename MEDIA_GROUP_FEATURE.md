# Media Group Feature Comparison

## Before: Individual Screenshot Messages

When 12 people were detected in a video, you would receive:

```
📱 Message 1: 🚨 Person Detection Alert! (1 image)
📱 Message 2: 🚨 Person Detection Alert! (1 image)  
📱 Message 3: 🚨 Person Detection Alert! (1 image)
📱 Message 4: 🚨 Person Detection Alert! (1 image)
📱 Message 5: 🚨 Person Detection Alert! (1 image)
📱 Message 6: 🚨 Person Detection Alert! (1 image)
📱 Message 7: 🚨 Person Detection Alert! (1 image)
📱 Message 8: 🚨 Person Detection Alert! (1 image)
📱 Message 9: 🚨 Person Detection Alert! (1 image)
📱 Message 10: 🚨 Person Detection Alert! (1 image)
📱 Message 11: 🚨 Person Detection Alert! (1 image)
📱 Message 12: 🚨 Person Detection Alert! (1 image)
```

**Result**: 12 separate notifications, chat spam, slower sending

## After: Media Group Messages

The same 12 detections now result in:

```
📱 Message 1: 🚨 Person Detection Alert! (10 images in media group)
   📸 Image 1: t=3.0s P1:87%
   📸 Image 2: t=6.0s P1:92%  
   📸 Image 3: t=9.0s P1:85% P2:78%
   📸 Image 4: t=12.0s P1:89%
   📸 Image 5: t=15.0s P1:91% P2:83%
   📸 Image 6: t=18.0s P1:88%
   📸 Image 7: t=21.0s P1:86% P2:79%
   📸 Image 8: t=24.0s P1:90%
   📸 Image 9: t=27.0s P1:84%
   📸 Image 10: t=30.0s P1:87%

📱 Message 2: 🚨 Person Detection Alert! (2 images in media group)
   📸 Image 1: t=33.0s P1:89%
   📸 Image 2: t=36.0s P1:85% P2:81%
```

**Result**: 2 notifications instead of 12, organized display, faster sending

## Benefits

### 🔔 Fewer Notifications
- **Before**: 12 notifications for 12 detections
- **After**: 2 notifications for 12 detections

### 📱 Better Chat Organization  
- **Before**: Chat flooded with individual images
- **After**: Clean, grouped presentation

### ⚡ Faster Sending
- **Before**: 12 API calls + 12 delays = ~36+ seconds
- **After**: 2 API calls + 2 delays = ~60 seconds total

### 📊 Rich Information
- **Before**: One timestamp per message
- **After**: Multiple timestamps with person counts and confidence levels

### 🎛️ Configurable
- Adjust media group size (1-10 images)
- Control delays between groups
- Maintain cooldown between detections

## Configuration Options

```bash
# Media group size (1-10, default: 10)
TELEGRAM_MEDIA_GROUP_SIZE=10

# Delay between media groups (seconds)
TELEGRAM_BATCH_TIMEOUT=30

# Cooldown between detections (seconds)  
PERSON_DETECT_COOLDOWN=10
```

## Use Cases

### High Activity Areas
```bash
# Send smaller groups more frequently
TELEGRAM_MEDIA_GROUP_SIZE=5
TELEGRAM_BATCH_TIMEOUT=15
```

### Low Activity Areas
```bash
# Send larger groups less frequently
TELEGRAM_MEDIA_GROUP_SIZE=10
TELEGRAM_BATCH_TIMEOUT=60
```

### Testing/Debug
```bash
# Send individual images for detailed analysis
TELEGRAM_MEDIA_GROUP_SIZE=1
TELEGRAM_BATCH_TIMEOUT=5
```

The media group feature makes the Watcher system much more practical for real-world use, especially in areas with frequent person detection events.
