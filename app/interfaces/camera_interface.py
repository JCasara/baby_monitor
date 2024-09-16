from abc import ABC, abstractmethod
from collections import deque
from typing import Optional

import numpy as np


class CameraInterface(ABC):
    @abstractmethod
    def __init__(self, video_config):
        self.frame_buffer = deque()
        self.video_config = video_config

    @abstractmethod
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture frame from camera."""
        pass

    @abstractmethod
    def release_resources(self) -> None:
        """Release camera resources."""
        pass
