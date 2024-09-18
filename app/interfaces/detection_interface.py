from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np


class DetectionInterface(ABC):
    @abstractmethod
    async def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for faces detected in the frame."""
        pass

    @abstractmethod
    def _detect_faces_sync(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Synchronous detection object for faces."""
        pass

    @abstractmethod
    async def detect_objects(self, frame: np.ndarray, object_class: str) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for objects detected in the frame."""
        pass

    @abstractmethod
    def _detect_objects_sync(self, frame: np.ndarray, object_class: str) -> List[Tuple[int, int, int, int]]:
        """Synchronous detection logic for objects."""
        pass

    @abstractmethod
    async def detect_persons(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for persons detected in the frame."""
        pass

    @abstractmethod
    async def detect_dogs(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for dogs detected in the frame."""
        pass
