from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np


class DetectionInterface(ABC):
    @abstractmethod
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for faces detected in the frame."""
        pass

    @abstractmethod
    def detect_persons(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns a list of bounding box coordinates for persons detected in the frame."""
        pass
