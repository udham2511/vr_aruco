# Camera handling for AR application

from typing import Tuple, Optional
import cv2
import numpy as np

from utils.exceptions import CameraError
from config.settings import ARConfig


class CameraManager:
    def __init__(self, camera_index: int = ARConfig.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize camera with error handling"""

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise CameraError(f"Cannot open camera {self.camera_index}")

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ARConfig.WINDOW_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ARConfig.WINDOW_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, ARConfig.MAX_FPS)

        # Verify actual dimensions
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"Camera initialized: {actual_width}x{actual_height}")

        self.is_initialized = True

    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from camera"""

        if not self.is_initialized or self.cap is None:
            return None

        ret, frame = self.cap.read()

        return frame if ret else None

    def get_dimensions(self) -> Tuple[int, int]:
        """Get camera frame dimensions"""

        if not self.is_initialized:
            return (ARConfig.WINDOW_WIDTH, ARConfig.WINDOW_HEIGHT)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        return (width, height)

    def release(self) -> None:
        """Release camera resources"""

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.is_initialized = False
