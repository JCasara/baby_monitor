from abc import ABC, abstractmethod


class DetectorInterface(ABC):
    @abstractmethod
    def detect_faces(self, frame):
        pass

    @abstractmethod
    def detect_persons(self, frame):
        pass
