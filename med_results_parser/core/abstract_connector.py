from abc import ABC, abstractmethod


class DBConnector(ABC):
    """
    Abstract base class for database connectors.
    """

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the database.
        """

    @abstractmethod
    def execute_query(self, query, params=None):
        """
        Execute a database query.

        Parameters:
            query (str): The SQL query to execute.
            params (tuple, optional): Parameters for the SQL query.
        """

    @abstractmethod
    def close(self):
        """
        Close the database connection.
        """
