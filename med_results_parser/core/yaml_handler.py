import yaml

from med_results_parser.core.abstract_handler import FileHandlerBase
from med_results_parser.settings.logger import get_logger

logger = get_logger("DBConnector")


class YamlFileHandler(FileHandlerBase):
    """
    Concrete implementation of FileHandlerBase for handling YAML files.
    """

    def read(self, file_path):
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error reading YAML file: {file_path} - {e}")
            return None

    def write(self, file_path, data):
        pass

    def delete(self, file_path):
        pass
