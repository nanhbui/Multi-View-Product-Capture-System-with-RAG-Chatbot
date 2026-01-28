#!/bin/bash
# Run enhanced capture system using existing .venv

echo "Starting Enhanced Product Capture System (with .venv)"
echo "======================================================="

cd "$(dirname "$0")"

# Use .venv python directly
if [ -f ".venv/bin/python3" ]; then
    echo "✓ Using .venv virtual environment"
    
    # Download YOLO model if needed
    if [ ! -f "yolov8n-seg.pt" ]; then
        echo "📥 Downloading YOLO segmentation model..."
        .venv/bin/python3 -c "from ultralytics import YOLO; YOLO('yolov8n-seg.pt')"
    fi
    
    # Run with OpenCV fallback (GStreamer not available)
    echo "🚀 Running with OpenCV fallback mode..."
    echo "Press SPACE to capture, Q to quit"
    echo "======================================================="
    
    .venv/bin/python3 phase_1/enhanced_capture_system.py --no-gstreamer "$@"
    
else
    echo "❌ ERROR: .venv not found or incomplete"
    echo "Please ensure .venv is properly set up"
    exit 1
fi