from abc import ABC, abstractmethod


class CameraInterface(ABC):
    @abstractmethod
    def capture_frame(self):
        pass

    @abstractmethod
    def release_resources(self):
        pass
