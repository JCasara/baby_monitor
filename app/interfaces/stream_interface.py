from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from .camera_interface import CameraInterface


class StreamInterface(ABC):
    def __init__(self, camera_service: CameraInterface):
        self.camera_service = camera_service

    @abstractmethod
    def start(self) -> None:
        """Start the streamer"""
        pass

    @abstractmethod
    def get_frame(self) -> Optional[np.ndarray]:
        """Get camera frame"""
        pass

    @abstractmethod
    def release_resources(self) -> None:
        """Release stream resources""" 
        pass
