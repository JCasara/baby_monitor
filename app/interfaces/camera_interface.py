import threading
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Generator

import numpy as np


class CameraInterface(ABC):
    @abstractmethod
    def __init__(self, video_config: dict):
        self.running: bool = True
        self.lock: threading.Lock = threading.Lock()
        self.frame_buffer: deque = deque()
        self.buffer_size: int = 0
        self.video_config: dict = video_config
        self.frame_rate: int = 0

    @abstractmethod
    def generate_frames(self) -> Generator[Any, Any, Any]:
        """Generate a frame for the video server."""
        pass

    @abstractmethod
    def get_frame(self) -> None | np.ndarray:
        """Gets frame from frame_buffer."""
        pass

    @abstractmethod
    def release_resources(self) -> None:
        """Release camera resources."""
        pass

    @abstractmethod
    def set_frame_callback(self, callback) -> None:
        """Sets frame callback."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Starts camera service thread."""
        pass
