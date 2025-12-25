"""
Gesture control module for hands-free capture.

This module uses MediaPipe hand tracking to enable gesture-based controls:
- Hand gestures for capture trigger
- Gesture-based UI navigation
- Touchless interaction
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
from enum import Enum

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("[WARNING] MediaPipe not installed. Gesture control disabled.")


class GestureType(Enum):
    """Recognized gesture types."""
    NONE = "none"
    THUMBS_UP = "thumbs_up"
    PEACE_SIGN = "peace_sign"
    OK_SIGN = "ok_sign"
    FIST = "fist"
    OPEN_PALM = "open_palm"
    POINTING = "pointing"


class GestureController:
    """
    Hand gesture recognition and control.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize gesture controller.

        Args:
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError(
                "MediaPipe is required for gesture control. "
                "Install it with: pip install mediapipe"
            )

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        # Gesture history for stability
        self.gesture_history: List[GestureType] = []
        self.history_size = 5

    def process_frame(
        self,
        frame: np.ndarray,
        draw_landmarks: bool = True
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Process frame for hand detection and gesture recognition.

        Args:
            frame: Input BGR frame
            draw_landmarks: Whether to draw hand landmarks on frame

        Returns:
            Tuple of (annotated_frame, hand_data_list)
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame
        results = self.hands.process(rgb_frame)

        # Annotated frame
        annotated_frame = frame.copy()

        # Hand data
        hand_data_list = []

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                # Draw landmarks
                if draw_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )

                # Extract hand data
                hand_data = self._extract_hand_data(
                    hand_landmarks,
                    handedness,
                    frame.shape[:2]
                )

                hand_data_list.append(hand_data)

        return annotated_frame, hand_data_list

    def _extract_hand_data(
        self,
        landmarks,
        handedness,
        image_shape: Tuple[int, int]
    ) -> Dict:
        """
        Extract structured data from hand landmarks.

        Args:
            landmarks: MediaPipe hand landmarks
            handedness: Hand classification (left/right)
            image_shape: Image (height, width)

        Returns:
            Dictionary with hand data
        """
        h, w = image_shape

        # Get landmark positions
        landmark_positions = []
        for landmark in landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            z = landmark.z
            landmark_positions.append((x, y, z))

        # Recognize gesture
        gesture = self._recognize_gesture(landmark_positions)

        # Update gesture history
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)

        # Get stable gesture (most common in history)
        stable_gesture = max(set(self.gesture_history), key=self.gesture_history.count)

        return {
            "handedness": handedness.classification[0].label,
            "confidence": handedness.classification[0].score,
            "landmarks": landmark_positions,
            "gesture": gesture,
            "stable_gesture": stable_gesture,
            "palm_center": self._get_palm_center(landmark_positions)
        }

    def _recognize_gesture(self, landmarks: List[Tuple[int, int, float]]) -> GestureType:
        """
        Recognize gesture from landmark positions.

        Args:
            landmarks: List of (x, y, z) landmark positions

        Returns:
            Recognized gesture type
        """
        # Finger tip indices: thumb=4, index=8, middle=12, ring=16, pinky=20
        # Finger base indices: thumb=2, index=5, middle=9, ring=13, pinky=17

        # Count extended fingers
        extended_fingers = self._count_extended_fingers(landmarks)

        # Recognize based on extended fingers
        if extended_fingers == 0:
            return GestureType.FIST

        elif extended_fingers == 5:
            return GestureType.OPEN_PALM

        elif extended_fingers == 1:
            # Check if it's thumb up or pointing
            if self._is_thumb_extended(landmarks):
                return GestureType.THUMBS_UP
            else:
                return GestureType.POINTING

        elif extended_fingers == 2:
            # Check if it's peace sign or OK sign
            if self._is_peace_sign(landmarks):
                return GestureType.PEACE_SIGN
            elif self._is_ok_sign(landmarks):
                return GestureType.OK_SIGN

        return GestureType.NONE

    def _count_extended_fingers(self, landmarks: List[Tuple[int, int, float]]) -> int:
        """
        Count number of extended fingers.

        Args:
            landmarks: List of landmark positions

        Returns:
            Number of extended fingers (0-5)
        """
        count = 0

        # Thumb (special case - check x-coordinate)
        if self._is_thumb_extended(landmarks):
            count += 1

        # Other fingers (check y-coordinate)
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky
        finger_bases = [5, 9, 13, 17]

        for tip_idx, base_idx in zip(finger_tips, finger_bases):
            if landmarks[tip_idx][1] < landmarks[base_idx][1]:  # Tip is above base
                count += 1

        return count

    def _is_thumb_extended(self, landmarks: List[Tuple[int, int, float]]) -> bool:
        """Check if thumb is extended."""
        # Thumb tip (4) should be further from palm than thumb base (2)
        thumb_tip = landmarks[4]
        thumb_base = landmarks[2]
        wrist = landmarks[0]

        dist_tip = np.linalg.norm(np.array(thumb_tip[:2]) - np.array(wrist[:2]))
        dist_base = np.linalg.norm(np.array(thumb_base[:2]) - np.array(wrist[:2]))

        return dist_tip > dist_base * 1.2

    def _is_peace_sign(self, landmarks: List[Tuple[int, int, float]]) -> bool:
        """Check if gesture is peace sign (index and middle fingers extended)."""
        index_extended = landmarks[8][1] < landmarks[5][1]
        middle_extended = landmarks[12][1] < landmarks[9][1]
        ring_folded = landmarks[16][1] > landmarks[13][1]
        pinky_folded = landmarks[20][1] > landmarks[17][1]

        return index_extended and middle_extended and ring_folded and pinky_folded

    def _is_ok_sign(self, landmarks: List[Tuple[int, int, float]]) -> bool:
        """Check if gesture is OK sign (thumb and index touching)."""
        thumb_tip = np.array(landmarks[4][:2])
        index_tip = np.array(landmarks[8][:2])

        distance = np.linalg.norm(thumb_tip - index_tip)

        # If thumb and index are close, it's OK sign
        return distance < 30

    def _get_palm_center(self, landmarks: List[Tuple[int, int, float]]) -> Tuple[int, int]:
        """
        Calculate palm center position.

        Args:
            landmarks: List of landmark positions

        Returns:
            (x, y) palm center coordinates
        """
        # Use landmarks 0 (wrist), 5, 9, 13, 17 (finger bases)
        palm_points = [landmarks[i][:2] for i in [0, 5, 9, 13, 17]]

        center_x = int(np.mean([p[0] for p in palm_points]))
        center_y = int(np.mean([p[1] for p in palm_points]))

        return (center_x, center_y)

    def close(self):
        """Release resources."""
        if hasattr(self, 'hands'):
            self.hands.close()


# Example usage and gesture mapping
GESTURE_ACTIONS = {
    GestureType.THUMBS_UP: "capture",
    GestureType.PEACE_SIGN: "confirm",
    GestureType.FIST: "cancel",
    GestureType.OPEN_PALM: "menu",
    GestureType.POINTING: "select"
}


def demo_gesture_control():
    """Demo gesture control with webcam."""
    if not MEDIAPIPE_AVAILABLE:
        print("[ERROR] MediaPipe not available. Cannot run demo.")
        return

    controller = GestureController()
    cap = cv2.VideoCapture(0)

    print("[INFO] Starting gesture control demo...")
    print("Gestures:")
    print("  - Thumbs up: Capture")
    print("  - Peace sign: Confirm")
    print("  - Fist: Cancel")
    print("  - Open palm: Menu")
    print("  - Pointing: Select")
    print("\nPress 'q' to quit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame
            annotated_frame, hand_data_list = controller.process_frame(frame)

            # Display gestures
            y_offset = 30
            for hand_data in hand_data_list:
                gesture = hand_data["stable_gesture"]
                handedness = hand_data["handedness"]

                text = f"{handedness}: {gesture.value}"
                cv2.putText(
                    annotated_frame,
                    text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                # Show action
                if gesture in GESTURE_ACTIONS:
                    action = GESTURE_ACTIONS[gesture]
                    cv2.putText(
                        annotated_frame,
                        f"Action: {action}",
                        (10, y_offset + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )

                y_offset += 80

            cv2.imshow("Gesture Control Demo", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        controller.close()


if __name__ == "__main__":
    demo_gesture_control()
