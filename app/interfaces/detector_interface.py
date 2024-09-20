import threading
from abc import ABC, abstractmethod
from collections import deque

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detection_interface import DetectionInterface
from app.interfaces.state_manager_interface import StateManagerInterface


class DetectorInterface(ABC):
    def __init__(self, camera_service: CameraInterface, detection_service: DetectionInterface, state_manager: StateManagerInterface):
        self.camera_service: CameraInterface = camera_service
        self.detection_service: DetectionInterface = detection_service
        self.state_manager: StateManagerInterface = state_manager
        self.lock: threading.Lock = threading.Lock()
        self.running: bool = True
        self.frame_buffer: deque = deque()
        
    @abstractmethod
    def frame_available(self):
        """Call this method when a new frame is added to the buffer."""
        pass

    @abstractmethod
    def start(self):
        """Start video detector thread."""
        pass

    @abstractmethod
    def release_resources(self):
        """Release video detector resources."""
        pass
