#!/bin/bash
#
# Optimized Capture System Startup Script
# Applies CPU performance optimizations for AMD GPU systems
#

echo "========================================="
echo "Starting Capture System (CPU Optimized)"
echo "========================================="
echo ""

# Set CPU threading optimizations
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Additional PyTorch CPU optimizations
export PYTORCH_ENABLE_MPS_FALLBACK=1

echo "Applied optimizations:"
echo "  - OMP_NUM_THREADS=4"
echo "  - MKL_NUM_THREADS=4"
echo "  - Camera resolution: 480x360"
echo "  - YOLO model: yolov8n.pt (detection only)"
echo ""
echo "Expected CPU usage: ~200-300% (down from 688%)"
echo ""
echo "Starting capture system..."
echo ""

# Run capture system
uv run python phase_1/capture_system.py

exit_code=$?

echo ""
echo "========================================="
echo "Capture system stopped (exit code: $exit_code)"
echo "========================================="

exit $exit_code
