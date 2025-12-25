# Phase 1 Modules

Modular components for the multi-view product capture system.

## Overview

This package provides specialized modules for advanced image processing, streaming, and gesture control:

```
modules/
├── __init__.py              # Package initialization
├── image_processing.py      # GrabCut, SIFT, Super-Resolution
├── gstreamer_pipeline.py    # Complex GStreamer pipelines
├── gesture_control.py       # Hand gesture recognition
└── README.md               # This file
```

---

## Modules

### 1. Image Processing (`image_processing.py`)

Advanced image processing operations for product capture.

**Features:**
- GrabCut background segmentation
- SIFT feature extraction and matching
- Super-resolution enhancement
- Transparent image creation
- Morphological mask refinement
- CLAHE contrast enhancement
- Image alignment using homography

**Example Usage:**

```python
from modules.image_processing import ImageProcessor

processor = ImageProcessor()

# Apply GrabCut for background removal
mask, segmented = processor.apply_grabcut(image, bbox=(50, 50, 400, 400))

# Create transparent PNG
transparent_img = processor.create_transparent_image(image, mask)

# Refine mask
refined_mask = processor.refine_mask_with_morphology(mask, kernel_size=5)

# Apply super-resolution
upscaled = processor.apply_super_resolution(image, scale_factor=2)

# Extract SIFT features
keypoints, descriptors = processor.extract_sift_features(image)

# Match features between two images
matches = processor.match_features(desc1, desc2)

# Align images
aligned_img, homography = processor.align_images(
    img1, img2, kp1, kp2, matches
)

# Enhance contrast
enhanced = processor.enhance_contrast(image, clip_limit=2.0)
```

---

### 2. GStreamer Pipeline (`gstreamer_pipeline.py`)

Utilities for creating and managing complex GStreamer pipelines.

**Features:**
- Basic camera capture pipelines
- Tee for splitting streams
- RTSP streaming server
- HLS (HTTP Live Streaming)
- Multi-output pipelines (display + record + stream)
- V4L2 device detection
- Device capability checking

**Example Usage:**

```python
from modules.gstreamer_pipeline import GStreamerPipeline

gst = GStreamerPipeline(device="/dev/video0", width=1280, height=720, fps=30)

# Test GStreamer availability
if GStreamerPipeline.test_gstreamer_available():
    print("GStreamer is available")

# List available devices
devices = GStreamerPipeline.list_v4l2_devices()
print(f"Devices: {devices}")

# Create basic pipeline
pipeline = gst.create_basic_pipeline(codec="MJPG")

# Create tee pipeline (display + record + stream)
tee_pipeline = gst.create_tee_pipeline(
    display=True,
    record=True,
    stream=True,
    record_path="output.mp4"
)

# Create RTSP server pipeline
rtsp_pipeline = gst.create_rtsp_server_pipeline(
    rtsp_path="/stream",
    port=8554
)

# Create HLS pipeline
hls_pipeline = gst.create_hls_pipeline(output_dir="./hls")

# Start pipeline as subprocess
process = gst.start_pipeline(pipeline)

# Stop pipeline
gst.stop_pipeline()

# Create OpenCV capture with GStreamer
cap = gst.create_opencv_capture()
ret, frame = cap.read()
```

---

### 3. Gesture Control (`gesture_control.py`)

Hand gesture recognition using MediaPipe for touchless interaction.

**Features:**
- MediaPipe hand tracking
- Gesture recognition (thumbs up, peace sign, OK, fist, open palm, pointing)
- Gesture history for stability
- Palm center tracking
- Customizable gesture-to-action mapping

**Recognized Gestures:**
- `THUMBS_UP` → Capture image
- `PEACE_SIGN` → Confirm action
- `FIST` → Cancel
- `OPEN_PALM` → Open menu
- `POINTING` → Select item

**Example Usage:**

```python
from modules.gesture_control import GestureController, GestureType

# Initialize controller
controller = GestureController(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Process frame
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

annotated_frame, hand_data_list = controller.process_frame(frame, draw_landmarks=True)

# Check gestures
for hand_data in hand_data_list:
    gesture = hand_data["stable_gesture"]
    handedness = hand_data["handedness"]

    if gesture == GestureType.THUMBS_UP:
        print("Capture gesture detected!")

    palm_center = hand_data["palm_center"]
    print(f"Palm center: {palm_center}")

# Release resources
controller.close()
```

**Demo:**

```bash
python -m modules.gesture_control
```

---

## Integration with Capture System

To integrate these modules with the main capture system:

### 1. Import Modules

```python
from modules.image_processing import ImageProcessor
from modules.gstreamer_pipeline import GStreamerPipeline
from modules.gesture_control import GestureController
```

### 2. Initialize in `__init__`

```python
class CaptureSystem:
    def __init__(self, ...):
        # ... existing code ...

        # Initialize modules
        self.image_processor = ImageProcessor()
        self.gst_pipeline = GStreamerPipeline()

        # Optional: gesture control
        try:
            self.gesture_controller = GestureController()
            self.gesture_enabled = True
        except ImportError:
            self.gesture_enabled = False
```

### 3. Use in Capture Loop

```python
# In run() method:

# Apply super-resolution
enhanced_frame = self.image_processor.apply_super_resolution(frame)

# Refine segmentation mask
if mask is not None:
    mask = self.image_processor.refine_mask_with_morphology(mask)

# Gesture control
if self.gesture_enabled:
    annotated_frame, hand_data = self.gesture_controller.process_frame(frame)

    for hand in hand_data:
        if hand["stable_gesture"] == GestureType.THUMBS_UP:
            # Trigger capture
            self.capture_image()
```

---

## Dependencies

### Core Dependencies
```bash
opencv-python>=4.8.0
numpy>=1.24.0
ultralytics>=8.0.0
```

### GStreamer
```bash
# Ubuntu/Debian
sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly

# Check installation
gst-launch-1.0 --version
```

### MediaPipe (for gesture control)
```bash
pip install mediapipe
```

---

## Architecture

```
capture_system.py (main)
    │
    ├─→ ImageProcessor
    │     ├─ GrabCut segmentation
    │     ├─ SIFT feature matching
    │     ├─ Super-resolution
    │     └─ Contrast enhancement
    │
    ├─→ GStreamerPipeline
    │     ├─ Camera capture
    │     ├─ Tee for splitting
    │     ├─ RTSP streaming
    │     └─ HLS streaming
    │
    └─→ GestureController (optional)
          ├─ Hand detection
          ├─ Gesture recognition
          └─ Touchless control
```

---

## Future Enhancements

1. **Image Processing**
   - DNN-based super-resolution (ESRGAN, RealESRGAN)
   - Advanced background removal (U2-Net, RMBG)
   - 3D reconstruction from multi-view images

2. **GStreamer**
   - WebRTC support for browser streaming
   - Hardware encoding (VAAPI, NVENC)
   - Multi-camera synchronization

3. **Gesture Control**
   - Custom gesture training
   - Two-hand gestures
   - Gesture velocity/direction tracking

---

## Troubleshooting

### GStreamer Issues

**Problem:** Pipeline fails to start
```bash
# Check GStreamer installation
gst-launch-1.0 --version

# Test camera
gst-launch-1.0 v4l2src device=/dev/video0 ! autovideosink

# List formats
v4l2-ctl -d /dev/video0 --list-formats-ext
```

**Solution:** Install missing plugins or check device permissions

### MediaPipe Issues

**Problem:** `ImportError: No module named 'mediapipe'`
```bash
pip install mediapipe
```

**Problem:** Low FPS with gesture control
```bash
# Reduce frame resolution or use lighter hand tracking model
controller = GestureController(
    min_detection_confidence=0.5,  # Lower confidence for speed
    min_tracking_confidence=0.3
)
```

---

## Testing

Each module includes standalone testing:

```bash
# Test image processing
python -m modules.image_processing

# Test GStreamer pipeline
python -m modules.gstreamer_pipeline

# Test gesture control
python -m modules.gesture_control
```

---

## License

Part of the Multi-View Product Capture System.

---

## Contact

For questions or issues, please refer to the main project README.
