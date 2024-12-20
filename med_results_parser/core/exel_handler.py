import os
from pathlib import Path

import polars as pl

from med_results_parser.core.abstract_handler import FileHandlerBase
from med_results_parser.settings.logger import get_logger

logger = get_logger("ExcelFileHandler")


class ExcelFileHandler(FileHandlerBase):
    """
    Concrete implementation of FileHandlerBase for Excel (.xlsx) files.
    """

    def read(self, file_path: Path, sheet_name=None):
        """
        Read an Excel file.

        Parameters:
            file_path (str): Path to the Excel file.
            sheet_name (str, optional): Name of the sheet to read. Defaults to the first sheet.

        Returns:
            pl.DataFrame: Polars DataFrame containing the data.
        """
        try:
            logger.info(f"Reading Excel file: {file_path}")
            df = pl.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Successfully read Excel file: {file_path}")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except KeyError:
            logger.error(f"Sheet '{sheet_name}' does not exist in {file_path}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return None

    def write(self, file_path, data):
        """
        Write data to an Excel file.

        Parameters:
            file_path (str): Path to save the Excel file.
            data (pl.DataFrame): Polars DataFrame to write.
        """
        try:
            logger.info(f"Writing to Excel file: {file_path}")
            data.write_excel(file_path)
            logger.info(f"Successfully wrote to Excel file: {file_path}")
        except Exception as e:
            logger.error(f"An error occurred while writing to Excel file: {e}")

    def delete(self, file_path):
        """
        Delete an Excel file.

        Parameters:
            file_path (str): Path to the file to delete.
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            else:
                logger.warning(f"File does not exist: {file_path}")
        except Exception as e:
            logger.error(f"An error occurred while deleting the file: {e}")
