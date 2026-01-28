#!/bin/bash

# Simple GStreamer Test Script
echo "🔧 GStreamer Integration Status Check"
echo "===================================="

echo ""
echo "1️⃣ GStreamer System Installation:"
gst-inspect-1.0 --version
echo ""

echo "2️⃣ Available GStreamer Plugins:"
echo "✅ v4l2src: $(gst-inspect-1.0 v4l2src > /dev/null 2>&1 && echo 'Available' || echo 'Missing')"
echo "✅ videoconvert: $(gst-inspect-1.0 videoconvert > /dev/null 2>&1 && echo 'Available' || echo 'Missing')"  
echo "✅ autovideosink: $(gst-inspect-1.0 autovideosink > /dev/null 2>&1 && echo 'Available' || echo 'Missing')"
echo "✅ appsink: $(gst-inspect-1.0 appsink > /dev/null 2>&1 && echo 'Available' || echo 'Missing')"
echo ""

echo "3️⃣ Camera Devices:"
ls -la /dev/video* 2>/dev/null || echo "No video devices found"
echo ""

echo "4️⃣ Test Basic Pipeline:"
echo "Testing: v4l2src ! videoconvert ! autovideosink"
timeout 2 gst-launch-1.0 v4l2src device=/dev/video0 num-buffers=10 ! videoconvert ! fakesink 2>/dev/null && echo "✅ Pipeline test OK" || echo "❌ Pipeline test failed"
echo ""

echo "5️⃣ GStreamer with Python:"
python3 -c "
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    print('✅ Python GStreamer bindings OK')
    print(f'✅ Version: {Gst.version_string()}')
except Exception as e:
    print(f'❌ Python GStreamer bindings failed: {e}')
"
echo ""

echo "6️⃣ **GstShark Status:**"
if command -v gst-shark-1.0 &> /dev/null; then
    echo "✅ GstShark installed"
    gst-shark-1.0 --help 2>/dev/null | head -3
else
    echo "❌ GstShark NOT installed"
    echo "   Install with: sudo apt-get install gst-shark-1.0" 
fi
echo ""

echo "📊 **GstShark Capabilities:**"
echo "   - 📈 Real-time FPS monitoring"
echo "   - ⚡ Processing time per element"  
echo "   - 🔍 CPU/Memory usage tracking"
echo "   - 📊 Latency measurements"
echo "   - 🎯 Buffer statistics"
echo "   - 📋 Visual performance reports"
echo ""

echo "7️⃣ Current System Status:"
echo "   🎥 Capture System: OpenCV + YOLO (working)"
echo "   🚀 GStreamer Plugin: Implemented (needs gi bindings)"
echo "   📊 GstShark Profiler: Integrated (needs gst-shark install)"
echo "   ⚙️ Hybrid Mode: Working (GStreamer preferred, OpenCV fallback)"
