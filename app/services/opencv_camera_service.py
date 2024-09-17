import threading
from collections import deque
from typing import Optional

import cv2
import numpy as np

from app.interfaces.camera_interface import CameraInterface


class OpenCVCameraService(CameraInterface):
    def __init__(self, video_config):
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")

        self.lock = threading.Lock()

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, video_config.get('frame_width', 640))
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, video_config.get('frame_height', 480))
        self.video_capture.set(cv2.CAP_PROP_FPS, video_config.get('frame_rate', 30))
        self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        self.scale_factor = video_config.get('scale_factor')
        self.buffer_size = video_config.get('buffer_size')
        self.frame_rate = video_config.get('frame_rate')
        self.frame_buffer = deque(maxlen=self.buffer_size)

    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from the camera using opencv."""
        ret, frame = self.video_capture.read()
        if not ret:
            print("Error: Failed to capture image.")
            return None
        
        # Mirror image about y-axis
        frame = cv2.flip(frame, 1)
        # TODO: shouldn't frame buffer be updated here?
        # TODO: Also, shouldn't camera service be its own thread?
        return frame

    def release_resources(self) -> None:
        """Release camera resources."""
        self.video_capture.release()
        # cv2.destroyAllWindows()
