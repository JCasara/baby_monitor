from abc import ABC, abstractmethod

import numpy as np

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detection_interface import DetectionInterface
from app.interfaces.state_manager_interface import StateManagerInterface


class DetectorInterface(ABC):
    def __init__(self, camera_service: CameraInterface, detection_service: DetectionInterface, state_manager: StateManagerInterface):
        self.camera_service: CameraInterface = camera_service
        self.detection_service: DetectionInterface = detection_service
        self.state_manager: StateManagerInterface = state_manager
          
    @abstractmethod
    async def process_frame(self) -> np.ndarray:
        """Process frame by performing detections."""
        pass
