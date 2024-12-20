from abc import ABC, abstractmethod

from med_results_parser.settings.logger import get_logger

logger = get_logger("ExcelFileHandler")


class FileHandlerBase(ABC):
    """
    Abstract base class for file operations.
    """

    @abstractmethod
    def read(self, file_path):
        """
        Read data from a file.
        """

    @abstractmethod
    def write(self, file_path, data):
        """
        Write data to a file.
        """

    @abstractmethod
    def delete(self, file_path):
        """
        Delete a file.
        """
