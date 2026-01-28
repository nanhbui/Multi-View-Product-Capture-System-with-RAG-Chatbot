#!/bin/bash

# GStreamer Integration Test Script
# Ensures proper Python path setup for GI bindings

set -e

echo "🔧 GStreamer Integration Test"
echo "============================"

# Activate virtual environment first
source .venv/bin/activate

# Add system packages to Python path (after venv activation)
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"

echo "✅ Python Path: $PYTHONPATH"
echo "✅ Virtual Env: $VIRTUAL_ENV"

# Test GI imports
echo ""
echo "🧪 Testing GI imports..."
python3 -c "
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import gi
gi.require_version('Gst', '1.0') 
gi.require_version('GstBase', '1.0')
from gi.repository import Gst, GObject, GstBase
print('✅ GStreamer bindings OK')
print(f'✅ GStreamer version: {Gst.version_string()}')
"

echo ""
echo "🧪 Testing YOLO imports..."
python3 -c "
import sys
# Priority: venv packages first, then system for gi only
try:
    from ultralytics import YOLO
    import torch
    print('✅ YOLO OK')
    print(f'✅ PyTorch version: {torch.__version__}')
    print(f'✅ CUDA available: {torch.cuda.is_available()}')
except ImportError as e:
    print(f'⚠️ YOLO import issue: {e}')
    print('✅ Continuing with capture system test...')
"

echo ""
echo "🚀 Running capture system with GStreamer integration..."

# Set environment for GStreamer + Python integration
export GST_PLUGIN_SYSTEM_PATH_1_0="/usr/lib/x86_64-linux-gnu/gstreamer-1.0"
export GST_PLUGIN_PATH_1_0="/usr/lib/x86_64-linux-gnu/gstreamer-1.0"

python3 phase_1/capture_system.py "$@"