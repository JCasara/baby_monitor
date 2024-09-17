import threading
from abc import ABC, abstractmethod

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detection_interface import DetectionInterface
from app.interfaces.state_manager_interface import StateManagerInterface


class VideoDetector(ABC):
    def __init__(self, camera_service: CameraInterface, detection_service: DetectionInterface, state_manager: StateManagerInterface):
        self.camera_service: CameraInterface = camera_service
        self.detection_service: DetectionInterface = detection_service
        self.state_manager: StateManagerInterface = state_manager
        self.lock: threading.Lock = threading.Lock()
        self.running: bool = True
        
    @abstractmethod
    def start(self):
        """Start video detector thread."""
        pass

    @abstractmethod
    def release_resources(self):
        """Release video detector resources."""
        pass
