#!/usr/bin/env python3
"""
GPU Detection and Setup Script for YOLO Inference
Checks available hardware and provides installation instructions.
"""

import subprocess
import sys


def check_nvidia_gpu():
    """Check if NVIDIA GPU is available."""
    try:
        result = subprocess.run(
            ["nvidia-smi"], capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_amd_gpu():
    """Check if AMD GPU is available."""
    try:
        result = subprocess.run(
            ["lspci"], capture_output=True, text=True, check=True
        )
        return "AMD" in result.stdout or "ATI" in result.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def check_rocm():
    """Check if ROCm is installed."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--version"], capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_pytorch():
    """Check PyTorch installation and CUDA availability."""
    try:
        import torch
        return {
            "installed": True,
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if hasattr(torch.version, 'cuda') else None,
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    except ImportError:
        return {"installed": False}


def main():
    print("=" * 70)
    print("GPU DETECTION AND SETUP RECOMMENDATIONS")
    print("=" * 70)
    print()

    # Check hardware
    has_nvidia = check_nvidia_gpu()
    has_amd = check_amd_gpu()
    has_rocm = check_rocm()
    pytorch_info = check_pytorch()

    print("Hardware Detection:")
    print(f"  NVIDIA GPU: {'✓ Detected' if has_nvidia else '✗ Not found'}")
    print(f"  AMD GPU:    {'✓ Detected' if has_amd else '✗ Not found'}")
    print(f"  ROCm:       {'✓ Installed' if has_rocm else '✗ Not installed'}")
    print()

    print("PyTorch Status:")
    if pytorch_info["installed"]:
        print(f"  Version:        {pytorch_info['version']}")
        print(f"  CUDA Available: {pytorch_info['cuda_available']}")
        if pytorch_info["cuda_version"]:
            print(f"  CUDA Version:   {pytorch_info['cuda_version']}")
        print(f"  GPU Devices:    {pytorch_info['device_count']}")
    else:
        print("  PyTorch:        ✗ Not installed")
    print()

    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()

    # Provide recommendations
    if has_amd and not has_rocm:
        print("🔶 AMD GPU Detected (ROCm not installed)")
        print()
        print("You have an AMD Radeon GPU but ROCm is not installed.")
        print()
        print("OPTION 1: Install ROCm (Complex - Ubuntu 20.04/22.04 recommended)")
        print("-" * 70)
        print("ROCm installation is complex and works best on Ubuntu.")
        print("Not officially supported on Debian 12.")
        print()
        print("If you want to try (at your own risk):")
        print("  1. Visit: https://rocm.docs.amd.com/")
        print("  2. Follow installation guide for your GPU")
        print("  3. Install PyTorch with ROCm:")
        print("     uv pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.0")
        print()
        print("OPTION 2: Optimize CPU Performance (Recommended for now)")
        print("-" * 70)
        print("Keep using CPU but optimize for better performance:")
        print()
        print("  1. Use faster YOLO model:")
        print("     - Change YOLO_MODEL to 'yolov8n.pt' (detection only, no segmentation)")
        print("     - This is 2-3x faster than yolov8n-seg.pt")
        print()
        print("  2. Reduce camera resolution in .env:")
        print("     CAMERA_WIDTH=320")
        print("     CAMERA_HEIGHT=240")
        print()
        print("  3. Enable multi-threading optimization:")
        print("     export OMP_NUM_THREADS=4")
        print("     export MKL_NUM_THREADS=4")
        print()
        print("  4. Run with optimizations:")
        print("     OMP_NUM_THREADS=4 uv run python phase_1/capture_system.py")
        print()
        print("Expected improvement: 688% CPU → ~200-300% CPU (still high but better)")
        print()

    elif has_nvidia and not pytorch_info["cuda_available"]:
        print("🟢 NVIDIA GPU Detected")
        print()
        print("Install CUDA-enabled PyTorch:")
        print("  uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print()
        print("This will reduce CPU usage from 688% to ~50-100%")
        print()

    elif pytorch_info["cuda_available"]:
        print("✅ GPU Acceleration Already Enabled!")
        print()
        print(f"PyTorch is using {pytorch_info['device_count']} GPU(s)")
        print("YOLO should automatically use GPU for inference.")
        print()

    else:
        print("🔵 No GPU Detected - CPU Only")
        print()
        print("Optimize CPU performance:")
        print("  1. Use faster YOLO model: yolov8n.pt")
        print("  2. Reduce resolution: CAMERA_WIDTH=320, CAMERA_HEIGHT=240")
        print("  3. Enable threading: OMP_NUM_THREADS=4")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
