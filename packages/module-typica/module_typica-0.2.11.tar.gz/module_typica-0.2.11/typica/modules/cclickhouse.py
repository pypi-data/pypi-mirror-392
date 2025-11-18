from clickhouse_connect import get_client
from clickhouse_connect.driver.client import Client

from typica.connection import DBConnectionMeta


class CHConnector:
    _meta: DBConnectionMeta
    _client: Client

    def __init__(self, meta: DBConnectionMeta) -> None:
        """
        Initialize the ClickHouse connector with the given connection metadata.

        :param meta: The metadata of the database connection.
        :type meta: DBConnectionMeta
        """
        self._meta = meta

    def __enter__(self) -> "CHConnector":
        """
        Connect to the ClickHouse server and return the connection object.

        :return: The connection object.
        :rtype: CHConnector
        :raises ValueError: If the connection to the ClickHouse server fails.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the connection to the ClickHouse server.

        This method is called when the context manager exits its scope.
        """
        self.close()

    def connect(self) -> None:
        """
        Establish a connection to the ClickHouse server.

        :raises ValueError: If the connection to the ClickHouse server fails.
        :raises Exception: If any other error occurs during the connection.
        """
        try:
            self._client = get_client(
                host=str(self._meta.host),
                port=int(self._meta.port),  # type: ignore
                user=self._meta.username,
                password=self._meta.password
                or "",  # cause get_client doesn't support empty password
                database=str(self._meta.database),
            )

        except Exception as e:
            raise e

    def close(self) -> None:
        """
        Close the connection to the ClickHouse server.

        This method is a no-op if the connection is already closed.
        """
        if self._client:
            self._client.close()
