"""
GStreamer pipeline management module.

This module provides utilities for creating and managing complex GStreamer pipelines:
- Tee for splitting video streams
- Multi-format streaming (RTSP, HLS, WebRTC)
- Recording to file
- Live display
"""

import cv2
import subprocess
from typing import Optional, List, Dict, Any
from pathlib import Path


class GStreamerPipeline:
    """
    Manage complex GStreamer pipelines for video streaming and processing.
    """

    def __init__(self, device: str = "/dev/video0", width: int = 1280, height: int = 720, fps: int = 30):
        """
        Initialize GStreamer pipeline manager.

        Args:
            device: Camera device path
            width: Frame width
            height: Frame height
            fps: Frames per second
        """
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.pipeline_process = None

    def create_basic_pipeline(self, codec: str = "MJPG") -> str:
        """
        Create a basic GStreamer pipeline for camera capture.

        Args:
            codec: Video codec (MJPG, H264, etc.)

        Returns:
            GStreamer pipeline string
        """
        if codec == "MJPG":
            pipeline = (
                f"v4l2src device={self.device} ! "
                f"image/jpeg, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
                "jpegdec ! videoconvert ! appsink"
            )
        else:
            pipeline = (
                f"v4l2src device={self.device} ! "
                f"video/x-raw, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
                "videoconvert ! appsink"
            )

        return pipeline

    def create_tee_pipeline(
        self,
        display: bool = True,
        record: bool = False,
        stream: bool = False,
        record_path: Optional[str] = None
    ) -> str:
        """
        Create a pipeline with tee for splitting stream to multiple outputs.

        Args:
            display: Enable display output
            record: Enable recording to file
            stream: Enable RTSP streaming
            record_path: Path to save recorded video

        Returns:
            GStreamer pipeline string
        """
        # Source
        pipeline = (
            f"v4l2src device={self.device} ! "
            f"image/jpeg, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
            "jpegdec ! videoconvert ! "
        )

        # Add tee for splitting
        pipeline += "tee name=t "

        outputs = []

        # Display branch
        if display:
            outputs.append("t. ! queue ! autovideosink")

        # Recording branch
        if record:
            if record_path is None:
                record_path = "output.mp4"

            outputs.append(
                f"t. ! queue ! x264enc ! mp4mux ! filesink location={record_path}"
            )

        # Streaming branch (RTSP)
        if stream:
            outputs.append(
                "t. ! queue ! x264enc tune=zerolatency ! "
                "rtph264pay config-interval=1 pt=96 ! "
                "udpsink host=127.0.0.1 port=8554"
            )

        # Combine all outputs
        pipeline += " ".join(outputs)

        return pipeline

    def create_rtsp_server_pipeline(
        self,
        rtsp_path: str = "/stream",
        port: int = 8554
    ) -> str:
        """
        Create pipeline for RTSP streaming server.

        Args:
            rtsp_path: RTSP path (e.g., /stream -> rtsp://localhost:8554/stream)
            port: RTSP port

        Returns:
            GStreamer pipeline string for RTSP server
        """
        pipeline = (
            f"v4l2src device={self.device} ! "
            f"image/jpeg, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
            "jpegdec ! videoconvert ! "
            "x264enc tune=zerolatency bitrate=2000 speed-preset=superfast ! "
            "rtph264pay config-interval=1 name=pay0 pt=96"
        )

        return pipeline

    def create_hls_pipeline(self, output_dir: str = "./hls") -> str:
        """
        Create pipeline for HLS (HTTP Live Streaming).

        Args:
            output_dir: Directory to save HLS segments

        Returns:
            GStreamer pipeline string
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        pipeline = (
            f"v4l2src device={self.device} ! "
            f"image/jpeg, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
            "jpegdec ! videoconvert ! "
            "x264enc tune=zerolatency ! "
            "mpegtsmux ! "
            f"hlssink location={output_dir}/segment%05d.ts "
            f"playlist-location={output_dir}/playlist.m3u8 max-files=5"
        )

        return pipeline

    def start_pipeline(self, pipeline_str: str) -> subprocess.Popen:
        """
        Start a GStreamer pipeline as a subprocess.

        Args:
            pipeline_str: GStreamer pipeline string

        Returns:
            Subprocess handle
        """
        cmd = ["gst-launch-1.0"] + pipeline_str.split()

        print(f"[INFO] Starting GStreamer pipeline: {' '.join(cmd)}")

        self.pipeline_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return self.pipeline_process

    def stop_pipeline(self):
        """Stop the running pipeline."""
        if self.pipeline_process:
            self.pipeline_process.terminate()
            self.pipeline_process.wait()
            print("[INFO] Pipeline stopped")

    def create_opencv_capture(self, pipeline: Optional[str] = None) -> cv2.VideoCapture:
        """
        Create OpenCV VideoCapture with GStreamer pipeline.

        Args:
            pipeline: GStreamer pipeline string. If None, uses basic MJPG pipeline.

        Returns:
            cv2.VideoCapture object
        """
        if pipeline is None:
            pipeline = self.create_basic_pipeline()

        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not cap.isOpened():
            raise RuntimeError(f"Failed to open GStreamer pipeline: {pipeline}")

        return cap

    @staticmethod
    def test_gstreamer_available() -> bool:
        """
        Test if GStreamer is available on the system.

        Returns:
            True if GStreamer is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["gst-launch-1.0", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def list_v4l2_devices() -> List[str]:
        """
        List available V4L2 video devices.

        Returns:
            List of device paths
        """
        devices = []
        for i in range(10):
            device = f"/dev/video{i}"
            if Path(device).exists():
                devices.append(device)

        return devices

    def get_device_capabilities(self) -> Dict[str, Any]:
        """
        Get device capabilities using v4l2-ctl.

        Returns:
            Dictionary of device capabilities
        """
        try:
            result = subprocess.run(
                ["v4l2-ctl", "-d", self.device, "--list-formats-ext"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return {
                    "device": self.device,
                    "capabilities": result.stdout
                }
            else:
                return {"error": "Failed to get capabilities"}

        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"error": "v4l2-ctl not available"}


# Example usage
if __name__ == "__main__":
    # Test GStreamer availability
    gst = GStreamerPipeline()

    if GStreamerPipeline.test_gstreamer_available():
        print("[SUCCESS] GStreamer is available")
    else:
        print("[ERROR] GStreamer is not available")

    # List devices
    devices = GStreamerPipeline.list_v4l2_devices()
    print(f"[INFO] Available devices: {devices}")

    # Create basic pipeline
    pipeline = gst.create_basic_pipeline()
    print(f"[INFO] Basic pipeline: {pipeline}")

    # Create tee pipeline
    tee_pipeline = gst.create_tee_pipeline(
        display=True,
        record=True,
        record_path="test_recording.mp4"
    )
    print(f"[INFO] Tee pipeline: {tee_pipeline}")
