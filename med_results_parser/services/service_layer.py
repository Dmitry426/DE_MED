from pathlib import Path

from med_results_parser.serialziers.med_serializer import AnalysisModel
from med_results_parser.services.data_processing import DataProcessLayer
from med_results_parser.settings.logger import get_logger

logger = get_logger("Service_layer")


class MedicalDataServiceLayer:
    def __init__(self, med_data_service, data_handler, conf):
        self.db_connector = med_data_service
        self.data_handler = data_handler
        self.settings = conf

    def process_polars_mde(self, f_path: Path, sheet_name: str, model):
        """
        Process and validate medical data from an Excel file.

        Args:
            f_path (Path): Path to the Excel file.
            sheet_name (str): Name of the sheet to read.
            model (Type[BaseModel]): Pydantic model for validation.

        Returns:
            pl.DataFrame: Validated Polars DataFrame.
        """
        try:
            df = self.data_handler.read(f_path, sheet_name=sheet_name)
            logger.info("File read successfully.")
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise ValueError(f"Error reading file at {f_path}: {e}")

        try:
            validated_df = DataProcessLayer.validate_polars_df(df, model)
            logger.info("Data validated successfully.")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise ValueError(f"Data validation failed: {e}")

        return validated_df

    def load_and_process_data(self):
        """
        Load and process medical data from the database and perform analysis.

        Returns:
            pl.DataFrame: Processed data with outliers and conclusions.
        """
        try:
            patient_data = self.db_connector.load_table_data(
                table_name="de.med_name",
                query="SELECT id, name, phone FROM de.med_name;",
                column_names=["id", "name", "phone"],
            )
            logger.info("Patient data loaded successfully.")

            analysis_data = self.db_connector.load_table_data(
                table_name="de.med_an_name",
                query="""
                SELECT id, name, is_simple, min_value, max_value FROM de.med_an_name;
                """,
                column_names=["id", "name", "is_simple", "min_value", "max_value"],
            )
            logger.info("Analysis metadata loaded successfully.")

            processed_analysis_data = DataProcessLayer.process_med_an_name_data(
                analysis_data
            )
            logger.info("Analysis metadata processed successfully.")

            file_path = Path(
                self.settings.project_path / self.settings.med_data.file_name
            )
            validated_data = self.process_polars_mde(
                f_path=file_path, sheet_name="hard", model=AnalysisModel
            )

            outliers = DataProcessLayer.get_outliers_with_details(
                validated_data, processed_analysis_data
            )
            logger.info("Outliers identified successfully.")

            res = DataProcessLayer.merge_with_patients(outliers, patient_data)
            logger.info("Data merged successfully.")

            return res
        except Exception as e:
            logger.error(f"Error during data processing: {e}")
            raise
