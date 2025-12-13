import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
import random
import sys
import json
from datetime import datetime
from enum import Enum
import pymongo


# State Machine States
class CaptureState(Enum):
    CAPTURING = "capturing"
    REVIEWING = "reviewing"
    SUMMARY = "summary"


class CaptureSystem:
    """
    Real-time multi-angle product capture system with object tracking and IQA.

    This system uses GStreamer for robust video streaming, YOLOv8 for object
    detection and tracking, and a simulated IQA module to ensure image quality.

    Features:
    - Separate subfolders for each captured image
    - 2/3 screen camera feed with side panel
    - Persistent thumbnail display
    - Review mode with quality recommendations
    - Final summary with retake options
    """

    def __init__(
        self,
        total_angles: int = 3,
        min_bbox_area: int = 10000,
        camera_id: int = 0,
        output_dir: str = "captured_images",
        model_name: str = "yolov8n.pt",

        mongo_uri: str = "mongodb://localhost:27017/", 
        db_name: str = "product_capture_db"
    ):
        """
        Initialize the capture system.

        Args:
            total_angles: Number of different angles to capture
            min_bbox_area: Minimum bounding box area for quality assessment
            camera_id: Camera device ID (default: 0)
            output_dir: Directory to save captured images
            model_name: YOLOv8 model name (default: yolov8n.pt for lightweight)
        """
        self.total_angles = total_angles
        self.min_bbox_area = min_bbox_area
        self.camera_id = camera_id
        self.model_name = model_name

        # Generate session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create session directory
        self.output_base = Path(output_dir)
        self.session_dir = self.output_base / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # State management
        self.state = CaptureState.CAPTURING
        self.current_angle = 1

        # Captured images storage: {angle_num: {"path": str, "thumbnail": np.ndarray, "status": str, "metadata": dict}}
        self.captured_images: Dict[int, Dict[str, Any]] = {}

        # Current frame being reviewed
        self.review_frame = None
        self.review_bbox = None
        self.review_detection_info = None
        self.recommendations = []

        # Close button state
        self.close_button_rect = None  # Will store (x1, y1, x2, y2)
        self.close_button_hovered = False

        print("[INFO] Connecting to MongoDB...")
        try:
            self.mongo_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            self.db = self.mongo_client[db_name]
            self.collection = self.db["captures"]
            # Kiểm tra kết nối
            self.mongo_client.server_info()
            print(f"[SUCCESS] Connected to MongoDB database: {db_name}")
        except Exception as e:
            print(f"[WARNING] MongoDB connection failed: {e}")
            print("Data will only be saved locally.")
            self.collection = None

        self.cap = None
        self.model = None
        self._initialize_camera()
        self._initialize_yolo()


    def _initialize_camera(self) -> None:
        """
        Khởi tạo camera ưu tiên GStreamer (MJPG) để đạt FPS cao.
        """
        print("[INFO] Initializing camera...")
        self.cap = None
        
        # Thử các ID phổ biến
        camera_ids = [self.camera_id, 0, 2, 1]
        
        # Cấu hình mong muốn: 1280x720 (HD)
        w, h, fps = 1280, 720, 30

        for cam_id in camera_ids:
            # --- PIPELINE GSTREAMER (FIXED) ---
            # Quan trọng: Request image/jpeg (MJPG) thay vì video/x-raw
            gst_pipeline = (
                f"v4l2src device=/dev/video{cam_id} ! "
                f"image/jpeg, width={w}, height={h}, framerate={fps}/1 ! "
                "jpegdec ! videoconvert ! appsink"
            )

            print(f"[INFO] Trying /dev/video{cam_id} with GStreamer (MJPG)...")
            try:
                self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
                if self.cap.isOpened():
                    # Đọc thử 1 frame để chắc chắn pipeline chạy
                    ret, _ = self.cap.read()
                    if ret:
                        print(f"[SUCCESS] GStreamer Pipeline Active on /dev/video{cam_id}")
                        self.camera_id = cam_id
                        return
            except Exception as e:
                print(f"[WARN] GStreamer error: {e}")

            # --- FALLBACK V4L2 ---
            # Nếu GStreamer tạch, dùng V4L2 chuẩn
            if self.cap: self.cap.release()
            print(f"[INFO] Trying /dev/video{cam_id} with standard V4L2...")
            self.cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    real_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    real_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    print(f"[SUCCESS] V4L2 Camera working: {real_w}x{real_h}")
                    self.camera_id = cam_id
                    return
        
        raise RuntimeError("No working camera found!")

    def _initialize_yolo(self) -> None:
        """
        Initialize YOLOv8 model with tracking capabilities.
        Downloads the model if not already present.
        """
        try:
            print(f"[INFO] Loading YOLOv8 model: {self.model_name}")
            self.model = YOLO(self.model_name)
            print("[INFO] YOLOv8 model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize YOLO model: {e}")

    def generate_recommendations(self, frame: np.ndarray, bbox: Optional[List[float]]) -> List[str]:
        """
        Generate quality recommendations based on image analysis.

        Uses OpenCV-based metrics for:
        - Blur detection (Laplacian variance)
        - Brightness analysis (HSV color space)
        - Object positioning
        - Object size

        Args:
            frame: Input frame
            bbox: Bounding box [x1, y1, x2, y2]

        Returns:
            List of recommendation strings
        """
        recs = []

        # 1. Check blur using Laplacian variance
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < 50:
            recs.append("⚠ BLURRY IMAGE: Hold camera steady or refocus")
        elif laplacian_var < 100:
            recs.append("⚠ SLIGHTLY BLURRY: Try to hold steadier")

        # 2. Check lighting
        if bbox:
            x1, y1, x2, y2 = map(int, bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            cropped = frame[y1:y2, x1:x2]
            if cropped.size > 0:
                hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
                brightness = np.mean(hsv[:, :, 2])

                if brightness < 50:
                    recs.append("⚠ TOO DARK: Increase lighting")
                elif brightness > 200:
                    recs.append("⚠ TOO BRIGHT: Reduce direct light")
                elif brightness < 80:
                    recs.append("⚠ SLIGHTLY DARK: Add more light")

        # 3. Check object position
        if bbox:
            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            img_cx, img_cy = frame.shape[1] / 2, frame.shape[0] / 2

            offset_x = abs(cx - img_cx)
            offset_y = abs(cy - img_cy)

            if offset_x > 150 or offset_y > 100:
                recs.append("⚠ OFF-CENTER: Center object in frame")

            # 4. Check object size
            area = (x2 - x1) * (y2 - y1)
            if area < 15000:
                recs.append("⚠ TOO SMALL: Move camera closer")
            elif area > 250000:
                recs.append("⚠ TOO LARGE: Move camera farther")

        # If no issues, give positive feedback
        if not recs:
            recs.append("✅ EXCELLENT QUALITY")
            recs.append("💡 Photo looks good, ready to save!")

        return recs

    def get_largest_detection(self, results) -> Optional[Tuple[List[float], int, float]]:
        """
        Extract the largest detected object from YOLO results.

        Returns:
            Tuple of (bbox, track_id, confidence) or None if no detection
        """
        if not results or not results[0].boxes:
            return None

        boxes = results[0].boxes

        # Calculate areas
        areas = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            areas.append((x2 - x1) * (y2 - y1))

        if not areas:
            return None

        # Get largest box
        largest_idx = np.argmax(areas)
        largest_box = boxes[largest_idx]

        bbox = largest_box.xyxy[0].cpu().numpy().tolist()
        track_id = int(largest_box.id.cpu().numpy()[0]) if largest_box.id is not None else -1
        confidence = float(largest_box.conf.cpu().numpy()[0])

        return bbox, track_id, confidence

    def save_image_and_metadata(
            self,
            frame: np.ndarray,
            angle_num: int,
            bbox: List[float],
            track_id: int,
            confidence: float,
            recommendations: List[str]
        ) -> Dict[str, str]:
            """
            Save image locally and detailed metadata to both JSON file and MongoDB.
            MongoDB stores ONLY metadata, NOT images.
            """
            # 1. Save image locally (e.g., captured_images/20231206_143022/angle_1.jpg)
            image_filename = f"angle_{angle_num}.jpg"
            image_path = self.session_dir / image_filename
            cv2.imwrite(str(image_path), frame)

            # Get image dimensions for metadata
            img_height, img_width = frame.shape[:2]

            # Calculate additional quality metrics
            has_warnings = any("⚠" in rec for rec in recommendations)
            has_success = any("✅" in rec for rec in recommendations)
            quality_status = "excellent" if has_success and not has_warnings else "warning" if has_warnings else "acceptable"

            # 2. Prepare detailed metadata for this angle (for chatbot understanding)
            angle_data = {
                "session_id": self.session_id,
                "angle_number": angle_num,
                "timestamp": datetime.now().isoformat(),

                # Image information
                "image": {
                    "filename": image_filename,
                    "local_path": str(image_path),
                    "width": img_width,
                    "height": img_height,
                    "format": "JPEG",
                    "color_space": "BGR"
                },

                # Object detection information
                "detection": {
                    "track_id": int(track_id) if track_id is not None else None,
                    "confidence": float(confidence),
                    "confidence_percentage": f"{float(confidence) * 100:.1f}%",
                    "bounding_box": {
                        "x1": float(bbox[0]),
                        "y1": float(bbox[1]),
                        "x2": float(bbox[2]),
                        "y2": float(bbox[3]),
                        "width": float(bbox[2] - bbox[0]),
                        "height": float(bbox[3] - bbox[1]),
                        "area_pixels": float((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])),
                        "center_x": float((bbox[0] + bbox[2]) / 2),
                        "center_y": float((bbox[1] + bbox[3]) / 2)
                    }
                },

                # Quality assessment
                "quality_assessment": {
                    "overall_status": quality_status,
                    "has_warnings": has_warnings,
                    "is_excellent": has_success,
                    "recommendations": recommendations,
                    "recommendation_count": len(recommendations),
                    "issues_detected": [rec for rec in recommendations if "⚠" in rec],
                    "passed_checks": [rec for rec in recommendations if "✅" in rec]
                },

                # Metadata for chatbot context
                "chatbot_summary": {
                    "description": f"Angle {angle_num} of {self.total_angles} captured",
                    "quality": quality_status,
                    "confidence_level": "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low",
                    "needs_review": has_warnings,
                    "ready_for_processing": not has_warnings
                }
            }

            # 3. Update the consolidated metadata.json file
            metadata_file = self.session_dir / "metadata.json"

            current_metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        current_metadata = json.load(f)
                except json.JSONDecodeError:
                    pass

            # Initialize metadata structure if new
            if "session_id" not in current_metadata:
                current_metadata = {
                    "session_id": self.session_id,
                    "created_at": datetime.now().isoformat(),
                    "session_info": {
                        "total_angles": self.total_angles,
                        "output_directory": str(self.session_dir),
                        "status": "in_progress"
                    },
                    "captures": {}
                }

            # Add this angle's data
            current_metadata["captures"][str(angle_num)] = angle_data

            # Update session statistics
            current_metadata["last_updated"] = datetime.now().isoformat()
            current_metadata["session_info"]["captured_count"] = len(current_metadata["captures"])
            current_metadata["session_info"]["completion_percentage"] = (len(current_metadata["captures"]) / self.total_angles) * 100

            # Check if session is complete
            if len(current_metadata["captures"]) >= self.total_angles:
                current_metadata["session_info"]["status"] = "completed"
                current_metadata["completed_at"] = datetime.now().isoformat()

            # Save to JSON file
            with open(metadata_file, 'w') as f:
                json.dump(current_metadata, f, indent=2)

            # 4. Save to MongoDB (ONLY metadata, NOT images)
            if self.collection is not None:
                try:
                    # Store the FULL metadata structure (same as JSON file)
                    # This ensures Phase 2 can read directly from MongoDB if needed
                    mongo_document = current_metadata.copy()
                    mongo_document["metadata_file_path"] = str(metadata_file)

                    # Upsert the entire session document with full details
                    self.collection.update_one(
                        {"session_id": self.session_id},
                        {"$set": mongo_document},
                        upsert=True
                    )
                    print(f"[INFO] Full session metadata saved to MongoDB (angle {angle_num})")
                except Exception as e:
                    print(f"[WARNING] Failed to save to MongoDB: {e}")

            print(f"[INFO] Image and metadata for angle {angle_num} saved.")

            return {
                "image_path": str(image_path),
                "metadata_path": str(metadata_file),
                "angle_data": angle_data
            }

    def create_thumbnail(self, frame: np.ndarray, size: int = 120) -> np.ndarray:
        """
        Tạo ảnh thumbnail vuông (mặc định 120x120) để lưu vào bộ nhớ hiển thị.
        """
        h, w = frame.shape[:2]
        aspect = w / h

        # Resize giữ nguyên tỷ lệ
        if aspect > 1:
            new_w = size
            new_h = int(size / aspect)
        else:
            new_h = size
            new_w = int(size * aspect)

        thumb = cv2.resize(frame, (new_w, new_h))

        # Tạo nền đen vuông
        thumb_square = np.zeros((size, size, 3), dtype=np.uint8)
        
        # Tính toán vị trí để đặt ảnh vào giữa
        pad_h = (size - new_h) // 2
        pad_w = (size - new_w) // 2
        
        # Gán ảnh vào nền đen
        thumb_square[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = thumb

        return thumb_square

    def draw_ui(
            self,
            camera_frame: np.ndarray,
            detection_info: Optional[Tuple] = None,
            live_recommendations: Optional[List[str]] = None
        ) -> np.ndarray:
            h, w = camera_frame.shape[:2]  
            
            # --- CẤU HÌNH UI ĐỘNG (RESPONSIVE) ---
            # Sidebar chiếm 1/3 chiều rộng tổng (hoặc cố định khoảng 350-400px)
            sidebar_w = 420 
            total_w = w + sidebar_w
            
            # Tính toán kích thước thumbnail dựa trên chiều cao màn hình
            # Dành khoảng 60% chiều cao cho danh sách ảnh, chia cho số góc
            available_h_for_list = h * 0.6
            thumb_size = int(available_h_for_list / self.total_angles) - 20
            # Giới hạn min/max để không quá xấu
            thumb_size = max(80, min(thumb_size, 140))
            
            dashboard = np.zeros((h, total_w, 3), dtype=np.uint8)
            
            # 1. Vẽ Camera
            dashboard[0:h, 0:w] = camera_frame

            # Vẽ bbox trên camera
            if detection_info:
                bbox, track_id, conf = detection_info
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(dashboard, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Label gọn gàng
                label = f"ID:{track_id} {conf:.2f}"
                t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(dashboard, (x1, y1-25), (x1+t_size[0], y1), (0,255,0), -1)
                cv2.putText(dashboard, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

            # 2. Vẽ Sidebar Background
            cv2.rectangle(dashboard, (w, 0), (total_w, h), (30, 30, 30), -1)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            sb_x = w + 20 # Margin trái của sidebar
            y = 30
            
            # Header Sidebar
            cv2.putText(dashboard, f"SESSION: {self.session_id.split('_')[1]}", (sb_x, y), font, 0.7, (255, 255, 255), 2)
            y += 30
            
            # List ảnh
            for i in range(1, self.total_angles + 1):
                # Vẽ khung chứa
                cv2.rectangle(dashboard, (sb_x, y), (sb_x + thumb_size, y + thumb_size), (60, 60, 60), 1)
                
                if i in self.captured_images:
                    data = self.captured_images[i]
                    # Resize thumb cho vừa khung dynamic
                    t_img = cv2.resize(data["thumbnail"], (thumb_size, thumb_size))
                    dashboard[y:y+thumb_size, sb_x:sb_x+thumb_size] = t_img
                    
                    # Viền xanh xác nhận
                    cv2.rectangle(dashboard, (sb_x, y), (sb_x + thumb_size, y + thumb_size), (0, 255, 0), 2)
                    
                    # --- HIỂN THỊ DATA CHI TIẾT (Theo yêu cầu) ---
                    info_x = sb_x + thumb_size + 10
                    info_y = y + 20
                    meta = data.get("metadata_obj", {})
                    
                    # Số thứ tự
                    cv2.putText(dashboard, f"#{i} DONE", (info_x, info_y), font, 0.6, (0, 255, 0), 2)
                    
                    # Conf & ID
                    if "confidence" in meta:
                        info_y += 25
                        cv2.putText(dashboard, f"Conf: {meta['confidence']:.2f}", (info_x, info_y), font, 0.5, (200, 200, 200), 1)
                    if "track_id" in meta:
                        info_y += 20
                        cv2.putText(dashboard, f"ID: {meta['track_id']}", (info_x, info_y), font, 0.5, (200, 200, 200), 1)
                        
                else:
                    # Chưa chụp
                    cv2.putText(dashboard, f"#{i}", (sb_x + thumb_size//2 - 10, y + thumb_size//2 + 10), font, 0.8, (100, 100, 100), 2)
                    cv2.putText(dashboard, "Waiting...", (sb_x + thumb_size + 10, y + thumb_size//2), font, 0.5, (100, 100, 100), 1)
                
                y += thumb_size + 15 # Padding giữa các thumb

            # Footer (Message & Status)
            # Kẻ vạch ngăn cách
            line_y = h - 150
            cv2.line(dashboard, (w, line_y), (total_w, line_y), (100, 100, 100), 1)

            msg_y = line_y + 30
            status_color = (0, 255, 255) if self.state == CaptureState.CAPTURING else (0, 165, 255)
            cv2.putText(dashboard, f"MODE: {self.state.value.upper()}", (sb_x, msg_y), font, 0.6, status_color, 2)

            # Bottom guide
            if self.state == CaptureState.CAPTURING:
                guide = "[S] Capture  [Q] Quit"
                cv2.putText(dashboard, guide, (sb_x, h - 20), font, 0.6, (255, 255, 255), 1)
            elif self.state == CaptureState.REVIEWING:
                guide = "[Ent] Save  [R] Retry"
                cv2.putText(dashboard, guide, (sb_x, h - 20), font, 0.6, (255, 255, 255), 1)
            elif self.state == CaptureState.SUMMARY:
                # Show completion message
                cv2.putText(dashboard, "ALL IMAGES CAPTURED!", (sb_x, msg_y + 35), font, 0.7, (0, 255, 0), 2)

                # Draw CLOSE button (large, clickable)
                btn_w, btn_h = 320, 50
                btn_x = sb_x + 10
                btn_y = h - 100

                # Store button coordinates for click detection
                self.close_button_rect = (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h)

                # Button color changes on hover
                btn_color = (0, 200, 0) if self.close_button_hovered else (0, 150, 0)
                cv2.rectangle(dashboard, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), btn_color, -1)
                cv2.rectangle(dashboard, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (0, 255, 0), 2)

                # Button text centered
                text = "CLOSE & EXIT"
                text_size = cv2.getTextSize(text, font, 0.9, 2)[0]
                text_x = btn_x + (btn_w - text_size[0]) // 2
                text_y = btn_y + (btn_h + text_size[1]) // 2
                cv2.putText(dashboard, text, (text_x, text_y), font, 0.9, (255, 255, 255), 2)

                # Show keyboard alternative
                cv2.putText(dashboard, "or press [Q]", (sb_x + 120, h - 20), font, 0.5, (150, 150, 150), 1)

            return dashboard

    def mouse_callback(self, event, x, y, _flags, _param):
        """
        Mouse callback handler for button clicks and hover effects.
        """
        if self.state == CaptureState.SUMMARY and self.close_button_rect:
            x1, y1, x2, y2 = self.close_button_rect

            # Check if mouse is over the button
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.close_button_hovered = True

                # Handle click
                if event == cv2.EVENT_LBUTTONDOWN:
                    print("\n[INFO] Close button clicked. Exiting...")
                    self.should_exit = True
            else:
                self.close_button_hovered = False

    def run(self) -> None:
        """
        Main capture loop with state machine.

        States:
        1. CAPTURING: Show live camera feed, press 'S' to capture
        2. REVIEWING: Show captured image with recommendations, choose keep or retake
        3. SUMMARY: All angles captured, option to retake any or exit
        """
        print("\n" + "="*60)
        print("MULTI-VIEW PRODUCT CAPTURE SYSTEM - PHASE 1")
        print("="*60)
        print(f"Target angles: {self.total_angles}")
        print(f"Session directory: {self.session_dir}")
        print(f"Min object area: {self.min_bbox_area}px²")
        print("="*60 + "\n")

        # Set up mouse callback
        window_name = "Product Capture System"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        # Flag for exit via button click
        self.should_exit = False

        try:
            while True:
                if self.state == CaptureState.CAPTURING:
                    # Read frame from camera
                    ret, frame = self.cap.read()
                    if not ret:
                        print("[ERROR] Failed to read frame from camera")
                        break

                    # Run YOLO tracking
                    results = self.model.track(
                        frame,
                        persist=True,
                        tracker="bytetrack.yaml",
                        verbose=False
                    )

                    # Get largest detection
                    detection = self.get_largest_detection(results)

                    # Generate live recommendations for real-time feedback
                    live_recs = None
                    if detection is not None:
                        bbox, track_id, confidence = detection
                        live_recs = self.generate_recommendations(frame, bbox)

                    # Draw UI with live recommendations
                    display_frame = self.draw_ui(frame, detection, live_recs)
                    cv2.imshow("Product Capture System", display_frame)

                    # Handle keyboard
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        print("\n[INFO] User requested quit. Exiting...")
                        break

                    elif key == ord('s'):
                        if detection is None:
                            print("[WARNING] No object detected! Please ensure object is visible.")
                            continue

                        bbox, track_id, confidence = detection

                        # Generate recommendations
                        self.recommendations = self.generate_recommendations(frame, bbox)

                        # Store review data
                        self.review_frame = frame.copy()
                        self.review_bbox = bbox
                        self.review_detection_info = detection

                        # Switch to REVIEW state
                        self.state = CaptureState.REVIEWING
                        print(f"[INFO] Captured angle {self.current_angle}, entering review mode")

                elif self.state == CaptureState.REVIEWING:
                    # Show the captured frame (frozen)
                    display_frame = self.draw_ui(self.review_frame, self.review_detection_info)
                    cv2.imshow("Product Capture System", display_frame)

                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        print("\n[INFO] User requested quit. Exiting...")
                        break

                    elif key == 13:  # ENTER key - Keep photo and continue
                        bbox, track_id, confidence = self.review_detection_info

                        # Save image and metadata to subfolder
                        save_result = self.save_image_and_metadata(
                            self.review_frame,
                            self.current_angle,
                            bbox,
                            track_id,
                            confidence,
                            self.recommendations
                        )

                        # Create thumbnail
                        thumbnail = self.create_thumbnail(self.review_frame)

                        angle_data = save_result["angle_data"]

                        # Store in captured_images with metadata (for UI display)
                        self.captured_images[self.current_angle] = {
                            "path": save_result["image_path"],
                            "thumbnail": thumbnail,
                            "status": "captured",
                            "metadata": save_result["metadata_path"],
                            "metadata_obj": {
                                "confidence": angle_data["detection"]["confidence"],
                                "track_id": angle_data["detection"]["track_id"],
                                "quality": angle_data["quality_assessment"]["overall_status"]
                            }
                        }

                        print(f"[SUCCESS] Angle {self.current_angle}/{self.total_angles} saved!")

                        # Move to next angle
                        self.current_angle += 1

                        if self.current_angle > self.total_angles:
                            # All angles captured - go to SUMMARY
                            self.state = CaptureState.SUMMARY
                            print("\n[SUCCESS] All angles captured! Entering summary mode.")
                        else:
                            # Return to CAPTURING for next angle
                            self.state = CaptureState.CAPTURING
                            print(f"[INFO] Ready to capture angle {self.current_angle}")

                    elif key == ord('r'):  # Retake
                        print(f"[INFO] Retaking angle {self.current_angle}")
                        self.state = CaptureState.CAPTURING

                elif self.state == CaptureState.SUMMARY:
                    # Show summary with all thumbnails
                    # Use last frame or blank frame
                    blank_frame = np.zeros((720, 960, 3), dtype=np.uint8)
                    display_frame = self.draw_ui(blank_frame)
                    cv2.imshow("Product Capture System", display_frame)

                    key = cv2.waitKey(1) & 0xFF

                    # Check if exit button was clicked
                    if self.should_exit or key == ord('q'):
                        print("\n[INFO] Session complete. Exiting...")
                        print(f"[INFO] All images saved to: {self.session_dir}")
                        break

                    # Allow retaking specific angles (1-3)
                    elif key in [ord('1'), ord('2'), ord('3')]:
                        retake_angle = int(chr(key))
                        if 1 <= retake_angle <= self.total_angles:
                            print(f"[INFO] Retaking angle {retake_angle}")
                            self.current_angle = retake_angle

                            # Remove old capture if exists
                            if retake_angle in self.captured_images:
                                del self.captured_images[retake_angle]

                            self.state = CaptureState.CAPTURING

        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt received. Shutting down...")

        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """
        Clean up resources (camera, windows, etc.).
        """
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Resources released. Goodbye!")

    def get_session_metadata(self) -> Dict[str, Any]:
        """
        Get all captured metadata for the current session.

        Returns:
            Dictionary containing session information
        """
        return {
            "session_id": self.session_id,
            "total_angles": self.total_angles,
            "captured_angles": len(self.captured_images),
            "output_directory": str(self.session_dir),
            "captures": {
                angle: {
                    "image_path": data["path"],
                    "metadata_path": data["metadata"]
                }
                for angle, data in self.captured_images.items()
            }
        }


def main():
    """
    Main entry point for the capture system.
    """
    # Configuration parameters
    TOTAL_ANGLES = 3
    MIN_BBOX_AREA = 10000
    CAMERA_ID = 0
    OUTPUT_DIR = "captured_images"
    MODEL_NAME = "yolov8n.pt"

    # Create and run the capture system
    try:
        capture_system = CaptureSystem(
            total_angles=TOTAL_ANGLES,
            min_bbox_area=MIN_BBOX_AREA,
            camera_id=CAMERA_ID,
            output_dir=OUTPUT_DIR,
            model_name=MODEL_NAME
        )

        capture_system.run()

    except Exception as e:
        print(f"[FATAL ERROR] Failed to initialize capture system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
