import polars as pl

from med_results_parser.core.exel_handler import ExcelFileHandler
from med_results_parser.core.postgers_connector import PostgresConnector
from med_results_parser.services.medical_data import MedicalDataService
from med_results_parser.services.service_layer import MedicalDataServiceLayer
from med_results_parser.settings.config import settings
from med_results_parser.settings.logger import get_logger

logger = get_logger(__name__)


def prepare_data(result):
    """
    Prepares the data for insertion into the database.

    Parameters:
        result (DataFrame): The processed Polars DataFrame.

    Returns:
        list[tuple]: Prepared data as a list of tuples.
    """
    result_table = result.select([
        pl.col("Телефон"),
        pl.col("Имя"),
        pl.col("Расшифровка анализа").alias("Название анализа"),
        pl.col("Заключение")
    ])
    return [tuple(row) for row in result_table.iter_rows()]

def insert_result_to_db(med_data, table_name, schema, data, column_names):
    """
    Creates the table if not exists and inserts the data.

    Parameters:
        med_data (MedicalDataService): The service object for database operations.
        table_name (str): The name of the database table.
        schema (str): The SQL schema for the table.
        data (list[tuple]): The data to be inserted.
        column_names (list[str]): The column names for the data.
    """
    try:
        med_data.create_table(table_name, schema)
    except Exception as e:
        logger.error(f"Error creating table '{table_name}': {e}")

    try:
        med_data.save_insert_data(
            table_name=table_name,
            data=data,
            column_names=column_names
        )
        logger.info(f"Data inserted successfully into '{table_name}'.")
    except Exception as e:
        logger.error(f"Failed to insert data into '{table_name}': {e}")


def main():
    try:
        db_connector = PostgresConnector(
            db_name=settings.db.db_name,
            user=settings.db.db_user,
            password=settings.db.db_password,
            host=settings.db.host,
            port=settings.db.port,
        )
        handler = ExcelFileHandler()
        med_data = MedicalDataService(db_connector)
        medical_service = MedicalDataServiceLayer(med_data, handler, settings)

        result = medical_service.load_and_process_data()
        data = prepare_data(result)

        table_name = "public.dvde_med_results"
        schema = """
            "Телефон" VARCHAR(30) NOT NULL,
            "Имя" VARCHAR(255) NOT NULL,
            "Название анализа" VARCHAR(255) NOT NULL,
            "Заключение" TEXT
        """

        insert_result_to_db(
            med_data=med_data,
            table_name=table_name,
            schema=schema,
            data=data,
            column_names=["Телефон", "Имя", "Название анализа", "Заключение"]
        )

        handler.write((settings.project_path / 'result.xlsx'), result)
        logger.info("Data saved to Excel successfully.")

    except Exception as ex:
        logger.error(f"Failed to process data: {ex}")

if __name__ == "__main__":
    main()
