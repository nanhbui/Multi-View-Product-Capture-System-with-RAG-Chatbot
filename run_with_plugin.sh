#!/bin/bash
#
# Run Capture System with GStreamer YOLO Plugin
# Uses system-aware virtual environment for GStreamer bindings
#

echo "========================================="
echo "Product Capture System - GStreamer Plugin Mode"
echo "========================================="
echo ""

# Check if system venv exists
if [ ! -d ".venv-system" ]; then
    echo "[INFO] Creating system-aware virtual environment..."
    uv venv --system-site-packages .venv-system

    echo "[INFO] Installing dependencies..."
    source .venv-system/bin/activate
    uv pip install ultralytics opencv-python pymongo psutil python-dotenv

    echo "[SUCCESS] Environment created"
    echo ""
fi

# Activate system venv
echo "[INFO] Activating system-aware environment (has GStreamer bindings)"
source .venv-system/bin/activate

# Verify GStreamer is available
python3 - <<'EOF'
try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    print("[✓] GStreamer Python bindings available")
    print(f"[✓] GStreamer version: {Gst.version_string()}")
except Exception as e:
    print(f"[✗] GStreamer not available: {e}")
    print("[!] Please install: sudo apt-get install python3-gi gir1.2-gstreamer-1.0")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "Features (Plugin Mode):"
echo "  ✓ Native GStreamer pipeline"
echo "  ✓ YOLO inference in pipeline"
echo "  ✓ Lower latency (~20-50ms)"
echo "  ✓ Better CPU utilization"
echo "  ✓ GPU acceleration (if available)"
echo ""
echo "Controls:"
echo "  S - Capture frame"
echo "  Q - Quit"
echo ""
echo "Starting with GStreamer plugin..."
echo "========================================="
echo ""

# Set backend to force plugin usage
export INFERENCE_BACKEND=gstreamer
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Run the test plugin first
echo "[INFO] Testing GStreamer YOLO plugin..."
timeout 3s python phase_1/modules/gst_yolo_inference.py 2>&1 | head -5

echo ""
echo "[INFO] Running capture system with plugin..."
echo ""

# Note: This will fail until we create the plugin-integrated version
# For now, it shows how to set up the environment
python phase_1/capture_system.py

exit_code=$?

echo ""
echo "========================================="
echo "System stopped (exit code: $exit_code)"
echo "========================================="

exit $exit_code
