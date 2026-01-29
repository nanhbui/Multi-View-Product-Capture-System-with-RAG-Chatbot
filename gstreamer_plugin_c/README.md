# GStreamer YOLO Plugin (C/C++)

This is a **native C/C++ GStreamer plugin** for YOLOv8 inference.

## Why C/C++ Plugin?

✅ **Advantages:**
- Works with `gst-launch-1.0` and `gst_parse_launch()`
- Better performance (no Python overhead)
- Proper GStreamer integration
- Can be installed system-wide

❌ **Python Plugin limitations:**
- Cannot use with pipeline strings
- Requires manual pipeline construction
- Performance overhead

## Architecture

```
Camera → v4l2src → jpegdec → videoconvert → yoloinference (C++) → videoconvert → appsink
                                                    ↓
                                            Ultralytics C++ API
                                                    ↓
                                            YOLOv8 with libtorch
```

## Build Dependencies

```bash
# GStreamer development files
sudo apt-get install \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

# OpenCV (for image processing)
sudo apt-get install libopencv-dev

# LibTorch (PyTorch C++ API)
# Download from: https://pytorch.org/get-started/locally/
# Select: Linux, LibTorch, C++/Java, CPU

# Or download directly:
wget https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip
unzip libtorch-cxx11-abi-shared-with-deps-2.1.0+cpu.zip
```

## Project Structure

```
gstreamer_plugin_c/
├── README.md               (this file)
├── CMakeLists.txt         (build configuration)
├── src/
│   ├── gstyoloinference.h     (plugin header)
│   ├── gstyoloinference.cpp   (plugin implementation)
│   └── yolo_runner.cpp        (YOLO inference wrapper)
└── models/
    └── yolov8n.torchscript    (exported model)
```

## Quick Start

### 1. Export YOLOv8 model to TorchScript

```python
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO('yolov8n-seg.pt')

# Export to TorchScript
model.export(format='torchscript')
# This creates: yolov8n.torchscript
```

### 2. Build the plugin

```bash
mkdir build && cd build
cmake ..
make
sudo make install
```

### 3. Test the plugin

```bash
# Check if plugin is registered
gst-inspect-1.0 yoloinference

# Test pipeline
gst-launch-1.0 v4l2src device=/dev/video0 ! \
    image/jpeg,width=1280,height=720 ! \
    jpegdec ! videoconvert ! \
    yoloinference model=yolov8n.torchscript confidence=0.25 ! \
    videoconvert ! autovideosink
```

## Integration with Python

```python
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

# Create pipeline using C++ plugin
pipeline = Gst.parse_launch(
    "v4l2src device=/dev/video0 ! "
    "image/jpeg,width=1280,height=720 ! "
    "jpegdec ! videoconvert ! "
    "yoloinference model=yolov8n.torchscript confidence=0.25 annotate=true ! "
    "videoconvert ! appsink name=sink"
)

pipeline.set_state(Gst.State.PLAYING)
```

## Performance

Expected performance on CPU:
- **640x480**: ~15-20 FPS
- **1280x720**: ~8-12 FPS

With GPU (CUDA):
- **640x480**: ~60-100 FPS
- **1280x720**: ~30-60 FPS

## Next Steps

1. Complete C++ implementation
2. Build and install
3. Integrate with capture_system.py
4. Optional: Add CUDA support for GPU acceleration
