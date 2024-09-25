from abc import ABC, abstractmethod

import numpy as np


class CameraInterface(ABC):
    @abstractmethod
    def __init__(self, video_config: dict):
        pass
        self.frame_count: int = 0
        self.fps: float = 0
        self.start_time: float = 0
        self.frame_rate: float = 0

    @abstractmethod
    def _set_camera_properties(self, video_config: dict) -> None:
        """Sets camera properties."""
        pass

    @abstractmethod
    def capture_frame(self) -> np.ndarray:
        """Capture a frame from the camera using opencv."""
        pass

    @abstractmethod
    def release_resources(self) -> None:
        """Release camera resources."""
        pass
