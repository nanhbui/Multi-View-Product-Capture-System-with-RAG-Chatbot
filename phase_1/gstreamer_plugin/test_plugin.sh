#!/bin/bash
# Quick test script for GStreamer YOLO Inference Plugin

set -e

echo "========================================="
echo "GStreamer YOLO Plugin - Quick Test"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if plugin is built
PLUGIN_PATH="$HOME/.local/share/gstreamer-1.0/plugins/gstyoloinference.so"
if [ ! -f "$PLUGIN_PATH" ]; then
    echo -e "${RED}Error: Plugin not found at $PLUGIN_PATH${NC}"
    echo "Please run ./build.sh first"
    exit 1
fi

# Set plugin path
export GST_PLUGIN_PATH="$HOME/.local/share/gstreamer-1.0/plugins:$GST_PLUGIN_PATH"

# Test 1: Plugin inspection
echo "Test 1: Plugin Inspection"
echo "-------------------------"
if gst-inspect-1.0 yoloinference > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Plugin registered successfully${NC}"
else
    echo -e "${RED}✗ Plugin not registered${NC}"
    echo "Run: export GST_PLUGIN_PATH=$HOME/.local/share/gstreamer-1.0/plugins:\$GST_PLUGIN_PATH"
    exit 1
fi
echo ""

# Test 2: Check model file
echo "Test 2: Model File Check"
echo "-------------------------"
MODEL_PATH="$(dirname "$0")/models/yolov8n-seg.torchscript"
if [ -f "$MODEL_PATH" ]; then
    echo -e "${GREEN}✓ Model found: $MODEL_PATH${NC}"
else
    echo -e "${YELLOW}! Model not found: $MODEL_PATH${NC}"
    echo "Please convert and copy your YOLO model:"
    echo ""
    echo "from ultralytics import YOLO"
    echo "model = YOLO('yolov8n-seg.pt')"
    echo "model.export(format='torchscript')"
    echo "cp yolov8n-seg.torchscript $(dirname "$0")/models/"
    echo ""
    echo "Continuing with default model path..."
    MODEL_PATH="yolov8n-seg.torchscript"
fi
echo ""

# Test 3: Check camera
echo "Test 3: Camera Detection"
echo "-------------------------"
CAMERA_DEVICE="/dev/video0"
if [ -e "$CAMERA_DEVICE" ]; then
    echo -e "${GREEN}✓ Camera found: $CAMERA_DEVICE${NC}"
else
    echo -e "${YELLOW}! Camera not found: $CAMERA_DEVICE${NC}"
    echo "Will use videotestsrc instead"
    CAMERA_DEVICE="videotestsrc"
fi
echo ""

# Test 4: Run simple pipeline
echo "Test 4: Pipeline Test"
echo "-------------------------"
echo "Starting GStreamer pipeline with YOLO plugin..."
echo "Press Ctrl+C to stop"
echo ""

if [ "$CAMERA_DEVICE" = "videotestsrc" ]; then
    # Test pattern
    gst-launch-1.0 \
        videotestsrc pattern=ball ! \
        video/x-raw,width=640,height=480,framerate=30/1 ! \
        videoconvert ! \
        yoloinference model-path="$MODEL_PATH" overlay=true device=cpu ! \
        videoconvert ! \
        autovideosink
else
    # Real camera
    gst-launch-1.0 \
        v4l2src device="$CAMERA_DEVICE" ! \
        video/x-raw,width=640,height=480,framerate=30/1 ! \
        videoconvert ! \
        yoloinference model-path="$MODEL_PATH" overlay=true device=cpu ! \
        videoconvert ! \
        autovideosink
fi

echo ""
echo -e "${GREEN}Test completed!${NC}"
