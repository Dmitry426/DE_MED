import psycopg2

from med_results_parser.core.abstract_connector import DBConnector
from med_results_parser.settings.logger import get_logger

logger = get_logger("DBConnector")


class PostgresConnector(DBConnector):
    """
    Concrete implementation of DBConnector for PostgreSQL.
    """

    def __init__(self, db_name, user, password, host="localhost", port=5432):
        """
        Initialize the PostgreSQL connector.

        Parameters:
            db_name (str): Database name.
            user (str): Username for authentication.
            password (str): Password for authentication.
            host (str, optional): Database host. Defaults to "localhost".
            port (int, optional): Database port. Defaults to 5432.
        """
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        """
        Establish a connection to the PostgreSQL database.
        """
        try:
            logger.info("Connecting to PostgreSQL database...")
            self.connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            logger.info("Successfully connected to PostgreSQL database.")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise

    def execute_query(self, query, params=None):
        """
        Execute a SQL query.

        Parameters:
            query (str): The SQL query to execute.
            params (tuple, optional): Parameters for the SQL query.

        Returns:
            list: Query results for SELECT queries, or None for other queries.
        """
        if not self.connection:
            logger.error("No database connection. Call `connect` first.")
            return None

        try:
            with self.connection.cursor() as cursor:
                logger.info(f"Executing query: {query}")
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                    logger.info(f"Query returned {len(result)} rows.")
                    return result
                self.connection.commit()
                logger.info("Query executed successfully.")
        except Exception as e:
            logger.error(f"An error occurred while executing the query: {e}")
            self.connection.rollback()
            raise

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")
        else:
            logger.warning("No connection to close.")

    def __enter__(self):
        """
        Context manager entry point. Connect to the database.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point. Ensure the connection is closed.
        """
        self.close()
