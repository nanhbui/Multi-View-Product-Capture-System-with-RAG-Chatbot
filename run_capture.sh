#!/bin/bash
#
# Run Product Capture System (Original - Full Features)
#

echo "=========================================
"
echo "Product Capture System - Full Featured"
echo "=========================================
"
echo ""

# Apply CPU optimizations
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

echo "Features:"
echo "  ✓ Multi-angle capture (3 angles)"
echo "  ✓ YOLOv8 segmentation with masks"
echo "  ✓ Real-time UI with histogram"
echo "  ✓ Quality assessment (IQA)"
echo "  ✓ MongoDB storage"
echo "  ✓ Review mode"
echo "  ✓ GStreamer video pipeline"
echo ""
echo "Controls:"
echo "  S - Capture current frame"
echo "  Enter - Confirm capture"
echo "  R - Retake"
echo "  Q - Quit"
echo ""
echo "Starting..."
echo "=========================================
"
echo ""

# Run capture system
uv run python phase_1/capture_system.py

exit_code=$?

echo ""
echo "=========================================
"
echo "System stopped (exit code: $exit_code)"
echo "=========================================
"

exit $exit_code
