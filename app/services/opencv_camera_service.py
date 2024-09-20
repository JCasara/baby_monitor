import threading
import time
from collections import deque

import cv2

from app.interfaces.camera_interface import CameraInterface
from app.utils.opencv_utils import display_fps


class OpenCVCameraService(CameraInterface):
    def __init__(self, video_config: dict):
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")

        self.running: bool = True
        self.lock: threading.Lock = threading.Lock()

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, video_config.get('image_width', 640))
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, video_config.get('image_height', 480))
        self.video_capture.set(cv2.CAP_PROP_FPS, video_config.get('frame_rate', 30))
        self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*video_config.get('fourcc', 'MJPG')))

        # Store actual camera properties
        self.frame_rate: int = int(self.video_capture.get(cv2.CAP_PROP_FPS))

        # Print actual camera property values
        print(f"Height x Width: {self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)} x {self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"Frame Rate: {self.video_capture.get(cv2.CAP_PROP_FPS)}")
        print(f"FOURCC: {self.video_capture.get(cv2.CAP_PROP_FOURCC)}")

        # self.scale_factor: int = video_config.get('scale_factor', 0.5)
        self.buffer_size: int = video_config.get('buffer_size', 100)
        self.frame_buffer: deque = deque(maxlen=self.buffer_size)

        self.frame_count: int = 0
        self.fps: float = 0
        self.start_time: float = time.time()

        self.frame_callback = None

    def _calculate_fps(self) -> None:
        """Calculate frame rate."""
        self.frame_count += 1
        elapsed_time: float = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time
 
    def _capture_frame(self) -> None:
        """Capture a frame from the camera using opencv."""
        while self.running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Error: Failed to capture image.")
                continue
            
            frame = cv2.flip(frame, 1) # Mirror image about y-axis

            self._calculate_fps()
            display_fps(frame, self.fps)

            with self.lock:
                self.frame_buffer.append(frame)
                if self.frame_callback:
                    self.frame_callback()

    def set_frame_callback(self, callback):
        """Sets a callback function to indicate when the frame is ready."""
        self.frame_callback = callback

    def start(self) -> None:
        """Start stream thread."""
        self.thread: threading.Thread = threading.Thread(target=self._capture_frame)
        self.thread.daemon = True
        self.thread.start()

    def release_resources(self) -> None:
        """Release camera resources."""
        self.running = False
        self.thread.join()
        self.video_capture.release()
        cv2.destroyAllWindows()
