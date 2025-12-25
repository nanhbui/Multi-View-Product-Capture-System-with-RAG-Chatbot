import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')

from gi.repository import Gst, GObject, GstBase
import numpy as np
import cv2
from typing import Optional, Dict, List, Any
import json

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARNING] Ultralytics YOLO not available. Install with: pip install ultralytics")


# Initialize GStreamer
Gst.init(None)


class GstYoloInference(GstBase.BaseTransform):
    # Plugin metadata
    __gstmetadata__ = (
        'YOLO Inference',
        'Filter/Analyzer/Video',
        'Performs YOLO object detection/segmentation on video frames',
        'Product Capture System'
    )

    # Pad templates
    _sink_template = Gst.PadTemplate.new(
        'sink',
        Gst.PadDirection.SINK,
        Gst.PadPresence.ALWAYS,
        Gst.Caps.from_string('video/x-raw,format=RGB')
    )

    _src_template = Gst.PadTemplate.new(
        'src',
        Gst.PadDirection.SRC,
        Gst.PadPresence.ALWAYS,
        Gst.Caps.from_string('video/x-raw,format=RGB')
    )

    # Register pad templates
    __gsttemplates__ = (_sink_template, _src_template)

    # Properties
    __gproperties__ = {
        'model-path': (
            str,
            'Model Path',
            'Path to YOLO model file',
            'yolov8n.pt',
            GObject.ParamFlags.READWRITE
        ),
        'confidence': (
            float,
            'Confidence Threshold',
            'Minimum confidence for detections',
            0.0, 1.0, 0.25,
            GObject.ParamFlags.READWRITE
        ),
        'iou-threshold': (
            float,
            'IOU Threshold',
            'IOU threshold for NMS',
            0.0, 1.0, 0.45,
            GObject.ParamFlags.READWRITE
        ),
        'device': (
            str,
            'Device',
            'Device for inference (cpu, cuda, mps, or auto)',
            'auto',
            GObject.ParamFlags.READWRITE
        ),
        'annotate': (
            bool,
            'Annotate',
            'Draw bounding boxes on output frames',
            True,
            GObject.ParamFlags.READWRITE
        ),
        'emit-metadata': (
            bool,
            'Emit Metadata',
            'Emit detection metadata as GStreamer messages',
            True,
            GObject.ParamFlags.READWRITE
        ),
    }

    def __init__(self):
        """Initialize the YOLO inference element."""
        super().__init__()

        # Properties
        self.model_path = 'yolov8n.pt'
        self.confidence = 0.25
        self.iou_threshold = 0.45
        self.device = 'auto'
        self.annotate = True
        self.emit_metadata = True

        # Internal state
        self.model: Optional[YOLO] = None
        self.frame_count = 0
        self.inference_times = []

        # Set transform properties
        self.set_in_place(False)  # We'll modify the buffer
        self.set_passthrough(False)

    def do_start(self):
        """Called when element starts. Load YOLO model."""
        if not YOLO_AVAILABLE:
            Gst.error(f"YOLO not available. Cannot start inference.")
            return False

        try:
            Gst.info(f"Loading YOLO model: {self.model_path}")

            # Determine device
            if self.device == 'auto':
                import torch
                if torch.cuda.is_available():
                    device = 'cuda'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    device = 'mps'
                else:
                    device = 'cpu'
            else:
                device = self.device

            # Load model
            self.model = YOLO(self.model_path)
            self.model.to(device)

            Gst.info(f"YOLO model loaded on device: {device}")
            return True

        except Exception as e:
            Gst.error(f"Failed to load YOLO model: {e}")
            return False

    def do_stop(self):
        """Called when element stops. Cleanup resources."""
        if self.model is not None:
            Gst.info("Releasing YOLO model")
            self.model = None

        # Print statistics
        if self.inference_times:
            avg_time = np.mean(self.inference_times)
            avg_fps = 1.0 / avg_time if avg_time > 0 else 0
            Gst.info(f"Inference statistics: {self.frame_count} frames, "
                    f"avg time: {avg_time*1000:.2f}ms, avg FPS: {avg_fps:.2f}")

        return True

    def do_transform(self, inbuf: Gst.Buffer, outbuf: Gst.Buffer) -> Gst.FlowReturn:
        """
        Transform function - runs YOLO inference on input buffer.

        Args:
            inbuf: Input GStreamer buffer containing video frame
            outbuf: Output GStreamer buffer for annotated frame

        Returns:
            Gst.FlowReturn: GST_FLOW_OK on success, error otherwise
        """
        try:
            # Get video info from caps
            caps = self.sinkpad.get_current_caps()
            if not caps:
                Gst.error("No caps on sink pad")
                return Gst.FlowReturn.ERROR

            struct = caps.get_structure(0)
            width = struct.get_value('width')
            height = struct.get_value('height')

            # Map input buffer to numpy array
            success, map_info = inbuf.map(Gst.MapFlags.READ)
            if not success:
                Gst.error("Failed to map input buffer")
                return Gst.FlowReturn.ERROR

            try:
                # Convert buffer to numpy array (RGB format)
                frame = np.ndarray(
                    shape=(height, width, 3),
                    dtype=np.uint8,
                    buffer=map_info.data
                )

                # Make a copy for modification
                frame_copy = np.copy(frame)

            finally:
                inbuf.unmap(map_info)

            # Run YOLO inference
            import time
            start_time = time.time()

            results = self.model(
                frame_copy,
                conf=self.confidence,
                iou=self.iou_threshold,
                verbose=False
            )[0]

            inference_time = time.time() - start_time
            self.inference_times.append(inference_time)
            self.frame_count += 1

            # Extract detection results
            detections = self._extract_detections(results)

            # Emit metadata as GStreamer message
            if self.emit_metadata and detections:
                self._emit_metadata(detections, inference_time)

            # Annotate frame if requested
            if self.annotate:
                frame_copy = self._annotate_frame(frame_copy, results)

            # Map output buffer and copy annotated frame
            success, map_info = outbuf.map(Gst.MapFlags.WRITE)
            if not success:
                Gst.error("Failed to map output buffer")
                return Gst.FlowReturn.ERROR

            try:
                # Copy annotated frame to output buffer
                out_array = np.ndarray(
                    shape=(height, width, 3),
                    dtype=np.uint8,
                    buffer=map_info.data
                )
                np.copyto(out_array, frame_copy)

            finally:
                outbuf.unmap(map_info)

            return Gst.FlowReturn.OK

        except Exception as e:
            Gst.error(f"Error in transform: {e}")
            import traceback
            traceback.print_exc()
            return Gst.FlowReturn.ERROR

    def _extract_detections(self, results) -> List[Dict[str, Any]]:
        """
        Extract detection information from YOLO results.

        Args:
            results: YOLO result object

        Returns:
            List of detection dictionaries
        """
        detections = []

        if results.boxes is not None:
            boxes = results.boxes.cpu().numpy()

            for i, box in enumerate(boxes):
                detection = {
                    'class_id': int(box.cls[0]),
                    'class_name': results.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                }

                # Add segmentation mask if available
                if results.masks is not None and i < len(results.masks):
                    mask = results.masks[i].cpu().numpy()
                    detection['has_mask'] = True
                    detection['mask_shape'] = mask.shape
                else:
                    detection['has_mask'] = False

                detections.append(detection)

        return detections

    def _annotate_frame(self, frame: np.ndarray, results) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.

        Args:
            frame: Input frame (numpy array)
            results: YOLO result object

        Returns:
            Annotated frame
        """
        # Use YOLO's built-in plotting for consistency
        annotated = results.plot()

        # Convert BGR to RGB (YOLO plot returns BGR)
        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        return annotated

    def _emit_metadata(self, detections: List[Dict[str, Any]], inference_time: float):
        """
        Emit detection metadata as GStreamer message.

        Args:
            detections: List of detection dictionaries
            inference_time: Time taken for inference (seconds)
        """
        metadata = {
            'frame': self.frame_count,
            'inference_time_ms': inference_time * 1000,
            'num_detections': len(detections),
            'detections': detections
        }

        # Create GStreamer structure
        struct = Gst.Structure.new_from_string(f"yolo-inference")
        struct.set_value('metadata', json.dumps(metadata))

        # Post message on bus
        msg = Gst.Message.new_application(self, struct)
        self.post_message(msg)

    def do_set_property(self, prop: GObject.GParamSpec, value):
        """Set element property."""
        if prop.name == 'model-path':
            self.model_path = value
        elif prop.name == 'confidence':
            self.confidence = value
        elif prop.name == 'iou-threshold':
            self.iou_threshold = value
        elif prop.name == 'device':
            self.device = value
        elif prop.name == 'annotate':
            self.annotate = value
        elif prop.name == 'emit-metadata':
            self.emit_metadata = value

    def do_get_property(self, prop: GObject.GParamSpec):
        """Get element property."""
        if prop.name == 'model-path':
            return self.model_path
        elif prop.name == 'confidence':
            return self.confidence
        elif prop.name == 'iou-threshold':
            return self.iou_threshold
        elif prop.name == 'device':
            return self.device
        elif prop.name == 'annotate':
            return self.annotate
        elif prop.name == 'emit-metadata':
            return self.emit_metadata


# Register element
GObject.type_register(GstYoloInference)


def register_plugin():
    """
    Register the YOLO inference plugin with GStreamer.

    This function should be called to make the plugin available to GStreamer.
    """
    return Gst.Plugin.register_static(
        Gst.VERSION_MAJOR,
        Gst.VERSION_MINOR,
        'yoloinference',
        'YOLO inference plugin for GStreamer',
        lambda plugin: plugin.register_type(
            GstYoloInference,
            'yoloinference',
            0,
            GstYoloInference
        ),
        '1.0',
        'MIT',
        'Product Capture System',
        'Product Capture System',
        'https://github.com/yourrepo'
    )


if __name__ == '__main__':
    # Test the plugin
    print("Testing GStreamer YOLO Inference Plugin")
    print("=" * 60)

    # Register plugin
    if register_plugin():
        print("[SUCCESS] Plugin registered successfully")
    else:
        print("[ERROR] Failed to register plugin")
        exit(1)

    # Create a test pipeline
    pipeline_str = (
        "v4l2src device=/dev/video0 ! "
        "videoconvert ! "
        "video/x-raw,format=RGB,width=640,height=480 ! "
        "yoloinference model-path=yolov8n.pt confidence=0.5 ! "
        "videoconvert ! "
        "autovideosink"
    )

    print(f"\nTest pipeline: {pipeline_str}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    # Create and run pipeline
    pipeline = Gst.parse_launch(pipeline_str)

    # Start pipeline
    pipeline.set_state(Gst.State.PLAYING)

    # Wait for EOS or error
    bus = pipeline.get_bus()
    try:
        while True:
            msg = bus.timed_pop_filtered(
                Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.APPLICATION
            )

            if msg:
                if msg.type == Gst.MessageType.ERROR:
                    err, debug = msg.parse_error()
                    print(f"\n[ERROR] {err}: {debug}")
                    break
                elif msg.type == Gst.MessageType.EOS:
                    print("\n[INFO] End of stream")
                    break
                elif msg.type == Gst.MessageType.APPLICATION:
                    struct = msg.get_structure()
                    if struct.get_name() == 'yolo-inference':
                        metadata = json.loads(struct.get_value('metadata'))
                        print(f"[DETECTION] Frame {metadata['frame']}: "
                              f"{metadata['num_detections']} objects, "
                              f"{metadata['inference_time_ms']:.2f}ms")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")

    finally:
        pipeline.set_state(Gst.State.NULL)
        print("[INFO] Pipeline stopped")
