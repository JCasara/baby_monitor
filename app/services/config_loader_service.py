import yaml

from app.interfaces.config_loader_interface import ConfigLoaderInterface


class ConfigLoaderService(ConfigLoaderInterface):
    @staticmethod
    def load_config(path: str) -> dict:
        with open(path, 'r') as file:
            return yaml.safe_load(file)
