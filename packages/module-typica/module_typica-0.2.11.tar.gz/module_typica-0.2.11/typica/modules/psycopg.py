import psycopg2
from psycopg2.errors import (
    ConnectionFailure,
    IdleInTransactionSessionTimeout,
    IdleSessionTimeout,
)
from psycopg2.extensions import connection, cursor

from typica.connection import DBConnectionMeta


class PostgreConnector:
    _meta: DBConnectionMeta
    _conn: connection
    _cursor: cursor

    def __init__(self, meta: DBConnectionMeta) -> None:
        """
        Initialize the Postgre connector with the given connection metadata.

        :param meta: The metadata of the database connection.
        :type meta: DBConnectionMeta
        """
        self._meta = meta

    def __enter__(self) -> "PostgreConnector":
        """
        Connect to the PostgreSQL server and return the connection object.

        :return: The connection object.
        :rtype: PostgreConnector
        :raises ValueError: If the connection to the PostgreSQL server fails.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.close()

    def connect(self, **kwargs) -> None:
        """
        Establish a connection to the PostgreSQL server.

        :param kwargs: Additional keyword arguments for psycopg2.connect.
        :raises ValueError: If the connection to the PostgreSQL server fails.
        :raises Exception: If any other error occurs during the connection.
        """
        try:
            self._conn = psycopg2.connect(
                dbname=self._meta.database,
                user=self._meta.username,
                password=self._meta.password,
                host=self._meta.host,
                port=self._meta.port,
                **kwargs,
            )
            self._cursor = self._conn.cursor()
        except ConnectionFailure:
            raise ValueError("PostgreSQL connection failed.")
        except (IdleInTransactionSessionTimeout, IdleSessionTimeout):
            raise ValueError("Session timed out.")
        except Exception as e:
            raise e

    def close(self) -> None:
        """
        Close the connection to the PostgreSQL server.

        This method is a no-op if the connection is already closed.
        """
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
