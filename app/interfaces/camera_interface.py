from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class CameraInterface(ABC):
    @abstractmethod
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture frame from camera."""
        pass

    @abstractmethod
    def release_resources(self) -> None:
        """Release camera resources."""
        pass
