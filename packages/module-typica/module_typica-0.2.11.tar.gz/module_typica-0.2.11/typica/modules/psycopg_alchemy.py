from sqlalchemy import (
    URL,
    Connection,
    CursorResult,
    Engine,
    create_engine,
    text,
)
from sqlalchemy.exc import TimeoutError

from typica.connection import DBConnectionMeta


class PostgreConnector:
    _meta: DBConnectionMeta
    _engine: Engine
    _conn: Connection

    def __init__(self, meta: DBConnectionMeta) -> None:
        """
        Initialize the Postgre connector with the given connection metadata.

        :param meta: The metadata of the database connection.
        :type meta: DBConnectionMeta
        """
        self._meta = meta

    def __enter__(self) -> Connection:
        """
        Connect to the PostgreSQL server and return the connection object.

        :return: The connection object.
        :rtype: Connection
        :raises ValueError: If the connection to the PostgreSQL server fails.
        """
        self.connect()
        return self._conn

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Close the connection to the PostgreSQL server.

        This method is called when the context manager exits its scope.
        """
        self.close()

    def execute_text(self, sql: str) -> CursorResult:
        try:
            res = self._conn.execute(text(sql))
            return res
        except Exception as e:
            raise e

    def connect(self) -> Connection:
        """
        Establish a connection to the PostgreSQL server.

        :return: The connection object.
        :rtype: Connection
        :raises ValueError: If the connection to the PostgreSQL server fails.
        :raises Exception: If any other error occurs during the connection.
        """
        try:
            self._engine = create_engine(
                URL.create(
                    drivername="postgresql",
                    username=self._meta.username,
                    password=self._meta.password,
                    host=self._meta.host,
                    port=int(self._meta.port),  # type: ignore
                    database=self._meta.database,
                )
            )
            self._conn = self._engine.connect()

            return self._conn
        except TimeoutError:
            raise ValueError("PostgreSQL connection timed out.")
        except Exception as e:
            raise e

    def close(self) -> None:
        """
        Close the connection to the PostgreSQL server.

        This method is a no-op if the connection is already closed.
        """
        if self._conn:
            self._conn.close()
