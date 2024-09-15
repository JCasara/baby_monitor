from abc import ABC, abstractmethod


class VideoStreamServerInterface(ABC):
    @abstractmethod
    def run(self) -> None:
        """Run video stream server."""
        pass
