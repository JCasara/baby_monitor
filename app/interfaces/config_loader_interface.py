from abc import ABC, abstractmethod


class ConfigLoaderInterface(ABC):
    @staticmethod
    @abstractmethod
    def load_config(path: str) -> dict:
        """Load configuration file."""
        pass
