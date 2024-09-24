from abc import ABC, abstractmethod


class ConfigLoaderInterface(ABC):
    def __init__(self, path: str) -> None:
        self.config = self.load_config(path)

    @staticmethod
    @abstractmethod
    def load_config(path: str) -> dict:
        """Load configuration file."""
        pass
