"""
Modular components for the multi-view product capture system.

This package contains specialized modules for:
- Image processing (segmentation, background removal, super-resolution)
- GStreamer pipeline management
- Gesture control
- Quality assessment
"""

from .image_processing import ImageProcessor
from .gstreamer_pipeline import GStreamerPipeline

__all__ = [
    "ImageProcessor",
    "GStreamerPipeline",
]
