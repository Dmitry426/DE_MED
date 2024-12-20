from decimal import Decimal

import polars as pl

from med_results_parser.core.postgers_connector import PostgresConnector
from med_results_parser.settings.logger import get_logger

logger = get_logger("Service_layer")


class MedicalDataService:
    """
    Service layer for interacting with medical data in the database.
    """

    def __init__(self, db_connector: PostgresConnector):
        """
        Initialize the MedicalDataService with a database connector.

        Parameters:
            db_connector (PostgresConnector): An instance of the PostgresConnector.
        """
        self.db_connector = db_connector

    def create_table(self, table_name: str, schema: str):
        """
        Creates a table in the database if it does not already exist.

        Parameters:
            table_name (str): Name of the table to create.
            schema (str): SQL schema for the table.
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});"
        try:
            with self.db_connector as connector:
                connector.execute_query(query)
                logger.info(f"Table '{table_name}' created or already exists.")
        except Exception as e:
            logger.error(f"Failed to create table '{table_name}': {e}")
            raise

    def save_insert_data(
        self, table_name: str, data: list[tuple], column_names: list[str]
    ):
        """
        Inserts data into the specified table.

        Parameters:
            table_name (str): Name of the table to insert data into.
            data (list[tuple]): List of tuples containing the data to insert.
            column_names (list[str]): List of column names for the data.
        """
        columns = ", ".join(f'"{col}"' for col in column_names)
        placeholders = ", ".join(["%s"] * len(column_names))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

        try:
            with self.db_connector as connector:
                for record in data:
                    connector.execute_query(query, params=record)
                logger.info(f"Inserted {len(data)} rows into table '{table_name}'.")
        except Exception as e:
            logger.error(f"Failed to insert data into '{table_name}': {e}")
            raise

    def load_table_data(
        self, table_name: str, query: str, column_names: list[str]
    ) -> pl.DataFrame:
        """
        Load data from a database table.

        Parameters:
            table_name (str): Name of the table to load data from.
            query (str): SQL query to fetch the data.
            column_names (list[str]): List of column names to process results.

        Returns:
            pl.DataFrame: A Polars DataFrame containing the fetched data.
        """
        try:
            with self.db_connector as connector:
                results = connector.execute_query(query)
                logger.info(f"Fetched {len(results)} rows from table '{table_name}'.")

            processed_results = [
                {
                    column: float(value) if isinstance(value, Decimal) else value
                    for column, value in zip(column_names, row)
                }
                for row in results
            ]

            return pl.DataFrame(processed_results)
        except Exception as e:
            logger.error(f"Error fetching data from '{table_name}': {e}")
            raise
