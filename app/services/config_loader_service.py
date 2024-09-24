import yaml

from app.interfaces.config_loader_interface import ConfigLoaderInterface


class ConfigLoaderService(ConfigLoaderInterface):
    def __init__(self, path: str) -> None:
        self.config = self.load_config(path)

    @staticmethod
    def load_config(path: str) -> dict:
        """Load configuration file."""
        with open(path, 'r') as file:
            return yaml.safe_load(file)
