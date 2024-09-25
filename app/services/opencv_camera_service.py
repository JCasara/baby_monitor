import time

import cv2
import numpy as np


class OpenCVCameraService:
    def __init__(self, video_config: dict):
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")

        self._set_camera_properties(video_config)
 
        self.frame_count: int = 0
        self.fps: float = 0
        self.start_time: float = time.time()

    def _set_camera_properties(self, video_config: dict) -> None:
        """Sets camera properties."""
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, video_config.get('image_width', 640))
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, video_config.get('image_height', 480))
        self.video_capture.set(cv2.CAP_PROP_FPS, video_config.get('frame_rate', 30))
        self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*video_config.get('fourcc', 'MJPG')))

        # User Controls
        self.video_capture.set(cv2.CAP_PROP_BRIGHTNESS, 128) # Brightness
        self.video_capture.set(cv2.CAP_PROP_CONTRAST, 128)   # Contrast
        self.video_capture.set(cv2.CAP_PROP_SATURATION, 128) # Saturation
        # self.video_capture.set(cv2.CAP_PROP_HUE, 0)          # Hue
        self.video_capture.set(cv2.CAP_PROP_AUTO_WB, 1)      # White balance automatic (0 = off)
        # self.video_capture.set(cv2.CAP_PROP_GAMMA, 150)      # Gamma
        self.video_capture.set(cv2.CAP_PROP_GAIN, 0)         # Gain
        self.video_capture.set(cv2.CAP_PROP_SHARPNESS, 128)  # Sharpness
        self.video_capture.set(cv2.CAP_PROP_BACKLIGHT, 0)    # Backlight compensation

        # Camera Controls
        # (Changing Auto_Exposure to manual and keeping Absolute Exposure time short is what enables 30fps)
        self.video_capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # Auto exposure (1 = manual mode)
        self.video_capture.set(cv2.CAP_PROP_EXPOSURE, 250)    # Exposure time absolute

        # Store actual camera properties
        self.frame_rate: int = int(self.video_capture.get(cv2.CAP_PROP_FPS))

        # Print actual camera property values
        print(f"Height x Width: {self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)} x {self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"Frame Rate: {self.frame_rate}")
        print(f"FOURCC: {self.video_capture.get(cv2.CAP_PROP_FOURCC)}")


    def _calculate_fps(self) -> None:
        """Calculate frame rate."""
        self.frame_count += 1
        elapsed_time: float = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time
 
    def capture_frame(self) -> np.ndarray:
        """Capture a frame from the camera using opencv."""
        ret, frame = self.video_capture.read()
        if not ret:
            print("Error: Failed to capture image.")
            # Return an empty ndarray with the expected shape
            return np.empty((0, 0, 3), dtype=np.uint8)
        
        frame = cv2.flip(frame, 1)
        self._calculate_fps()
        return frame

    def release_resources(self) -> None:
        """Release camera resources."""
        self.video_capture.release()
        cv2.destroyAllWindows()
