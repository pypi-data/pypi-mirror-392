import json
import re
from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar, Union

from deprecated import deprecated
from pydantic import AliasChoices, BaseModel, Field, model_validator

from .utils import ConnectionTypes

connectionType = TypeVar("connectionType", ConnectionTypes, str, None)


@deprecated(version="0.2.0", reason="Use EndpointMeta instead")
class HostMeta(BaseModel):
    host: Optional[str] = Field("localhost", description="Connection host")
    port: Optional[int] = Field(8000, description="Connection port")


class EndpointMeta(BaseModel):
    host: Optional[str] = Field(
        "localhost",
        description="Connection host",
        validation_alias=AliasChoices(
            "host", "hostname", "ip", "ip_address", "idAddress"
        ),
    )
    port: Optional[str | int] = Field(8000, description="Connection port")
    endpoint: Optional[str] = Field(
        "localhost:8000",
        description="Endpoint Connection",
        validation_alias=AliasChoices(
            "endpoint", "endpoint_uri", "endpoint_url"
        ),
    )

    @property
    def port_int(self) -> int | None:
        if self.port and isinstance(self.port, str):
            return int(self.port)
        return self.port or None


class AuthMeta(BaseModel):
    username: Optional[str] = Field(
        None,
        description="Database username",
        validation_alias=AliasChoices(
            "username",
            "user",
            "user_name",
            "user_access",
            "userName",
            "userAccess",
        ),
    )
    password: Optional[str] = Field(
        None,
        description="Database password",
        validation_alias=AliasChoices(
            "password",
            "pw",
            "pass",
            "password_access",
            "secret",
            "secret_pass",
            "passwordAccess",
            "secretPass",
        ),
    )


class URIConnectionMeta(BaseModel):
    uri: Optional[str] = Field("", description="Database connection URI")


@deprecated(
    version="0.1.11",
    reason="use DatabaseConnectionMeta or QueueConnectionMeta instead",
)
class ConnectionMeta(HostMeta):
    """
    Base connection metadata model
    """

    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    database: Optional[Union[str, int]] = Field(
        None, description="Database name"
    )
    clustersUri: Optional[List[HostMeta]] = Field(None)

    def uri_string(self, base: str = "http", with_db: bool = True) -> str:
        meta = ""
        if self.clustersUri:
            temp = []
            for cluster in self.clustersUri:
                temp.append(f"{cluster.host}:{cluster.port}")
            meta = ",".join(temp)
        else:
            meta = f"{self.host}:{self.port}"
        if self.username:
            return f"{base}://{self.username}:{self.password}@{meta}/{self.database if with_db else ''}"
        return f"{base}://{meta}/{self.database if with_db else ''}"


@deprecated(version="0.2.0", reason="Use DatabaseConnectionMeta instead")
class DatabaseConnectionMeta(HostMeta):
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    database: Optional[Union[str, int]] = Field(
        None, description="Database name"
    )
    uri: Optional[str] = Field("", description="")

    def uri_string(self, base: str = "http", with_db: bool = True) -> str:
        meta = f"{self.host}:{self.port}"
        if self.username:
            return f"{base}://{self.username}:{self.password}@{meta}/{self.database if with_db else ''}"
        return f"{base}://{meta}/{self.database if with_db else ''}"

    @model_validator(mode="after")
    def extract_uri(self):
        if self.uri:
            uri = re.sub(r"\w+:(//|/)", "", self.uri)
            metadata, others = (
                re.split(r"\/\?|\/", uri)
                if re.search(r"\/\?|\/", uri)
                else [uri, None]
            )
            if others and "&" in others:
                for other in others.split("&"):
                    if "=" in other and re.search(r"authSource", other):
                        self.database = other.split("=")[-1]
                    elif "=" not in other:
                        self.database = other
            if "@" in metadata:
                self.username, self.password, self.host, self.port = re.split(  # pyright: ignore[reportAttributeAccessIssue]
                    r"\@|\:", metadata
                )
            else:
                self.host, self.port = re.split(r"\:", metadata)  # pyright: ignore[reportAttributeAccessIssue]
            self.port = int(self.port)  # pyright: ignore[reportArgumentType]
        return self


@deprecated(version="0.2.0", reason="use DBConnectionMeta instead")
class ConnectionUriMeta(ConnectionMeta):
    """Connection with URI and connection types metadata model

    Args:
        ConnectionMeta (BaseModel): Base connection metadata model

    Returns:
        ConnectionMeta: parsed connection metadata from URI
    """

    uri: Optional[str] = Field("", description="")
    type_connection: Optional[connectionType] = Field(  # pyright: ignore[reportGeneralTypeIssues]
        None, examples=ConnectionTypes.list()
    )

    @model_validator(mode="after")
    def extract_uri(self):
        if self.uri:
            uri = re.sub(r"\w+:(//|/)", "", self.uri)
            metadata, others = (
                re.split(r"\/\?|\/", uri)
                if re.search(r"\/\?|\/", uri)
                else [uri, None]
            )
            if others and "&" in others:
                for other in others.split("&"):
                    if "=" in other and re.search(r"authSource", other):
                        self.database = other.split("=")[-1]
                    elif "=" not in other:
                        self.database = other
            if "@" in metadata:
                if "," in metadata:
                    metadata, raw_clusters = re.split(r"\@", metadata)
                    self.username, self.password = re.split(r"\:", metadata)
                    clustersUri = []
                    for cluster in raw_clusters.split(","):
                        hostData = re.split(r"\:", cluster)
                        clustersUri.append(
                            HostMeta(host=hostData[0], port=hostData[1])  # pyright: ignore[reportArgumentType]
                        )
                    self.clustersUri = clustersUri
                else:
                    self.username, self.password, self.host, self.port = (  # pyright: ignore[reportAttributeAccessIssue]
                        re.split(r"\@|\:", metadata)
                    )
            else:
                self.host, self.port = re.split(r"\:", metadata)  # pyright: ignore[reportAttributeAccessIssue]
            self.port = int(self.port)  # pyright: ignore[reportArgumentType]
        return self


class DBConnectionMeta(EndpointMeta, AuthMeta, URIConnectionMeta):
    database: Optional[str] = Field(
        None,
        description="Database name",
        validation_alias=AliasChoices(
            "database", "database_name", "db", "db_name", "index", "index_name"
        ),
    )
    space: Optional[str] = Field(
        None,
        description="Database schema / space name",
        validation_alias=AliasChoices(
            "space", "schema", "space_name", "schema_name", "table_schema"
        ),
    )
    connection_type: Optional[str] = Field(
        None,
        description="Database connection type",
        validation_alias=AliasChoices(
            "connection_type", "type", "database_type", "connector_type"
        ),
    )

    def uri_string(self, base: str = "http", with_db: bool = True) -> str:
        """
        Return a URI string for the database connection.

        :param base: The base of the URI (e.g. "http", "postgresql", etc.).
        :param with_db: Whether to include the database name in the URI.
        :return: A string representing the URI.
        """
        if self.host:
            meta = f"{self.host}:{self.port}"
            if self.username:
                return f"{base}://{self.username}:{self.password}@{meta}/{self.database if with_db and self.database else ''}"
            return f"{base}://{meta}/{self.database if with_db and self.database else ''}"
        return ""

    @model_validator(mode="after")
    def extract_uri(self):
        """
        Extracts and parses the URI to populate the connection metadata fields.

        This method processes the `uri` attribute to extract authentication and
        connection details such as username, password, host, port, and database.
        It modifies the respective attributes of the instance based on the parsed
        URI components.

        Steps involved:
        - Strips the scheme from the URI.
        - Splits the URI into metadata and additional query parameters.
        - Extracts database name from query parameters if present.
        - Parses authentication info and host details from the metadata.
        - Converts the port to an integer.

        Returns:
            The instance with populated connection metadata fields.
        """
        if self.uri:
            uri = re.sub(r"\w+:(//|/)", "", self.uri)
            metadata, others = (
                re.split(r"\/\?|\/", uri)
                if re.search(r"\/\?|\/", uri)
                else [uri, None]
            )
            if others and not self.database:
                if "&" in others:
                    for other in others.split("&"):
                        if "=" in other and re.search(r"authSource", other):
                            self.database = other.split("=")[-1]
                        elif "=" not in other:
                            self.database = other
                else:
                    self.database = others
            if "@" in metadata:
                self.username, self.password, self.host, self.port = re.split(
                    r"\@|\:", metadata
                )
            else:
                self.host, self.port = re.split(r"\:", metadata)
            if self.port:
                self.port = int(self.port)
        return self


class ClusterConnectionMeta(AuthMeta, URIConnectionMeta):
    cluster_uri: Optional[list[EndpointMeta]] = Field(
        [],
        description="List of clusters endpoint",
        validation_alias=AliasChoices(
            "cluster_uri", "cluster", "clusters", "bootstrap_servers"
        ),
    )
    database: Optional[str] = Field(
        None,
        description="Database name",
        validation_alias=AliasChoices(
            "database",
            "database_name",
            "db",
            "db_name",
            "index",
            "index_name",
            "dbName",
            "databaseName",
        ),
    )
    space: Optional[str] = Field(
        None,
        description="Database schema / space name",
        validation_alias=AliasChoices(
            "space",
            "schema",
            "space_name",
            "schema_name",
            "table_schema",
            "spaceName",
            "schemaName",
            "tableSchema",
        ),
    )
    connection_type: Optional[str] = Field(
        None,
        description="Database connection type",
        validation_alias=AliasChoices(
            "connection_type",
            "type",
            "database_type",
            "connector_type",
            "databaseType",
            "connectionType",
            "connectorType",
        ),
    )

    def uri_string(self, base: str = "http", with_db: bool = True) -> str:
        """
        Return a URI string for the database connection.

        :param base: The base of the URI (e.g. "http", "postgresql", etc.).
        :param with_db: Whether to include the database name in the URI.
        :return: A string representing the URI.
        """
        if self.cluster_uri:
            meta = ",".join([f"{c.host}:{c.port}" for c in self.cluster_uri])
            if self.username:
                return f"{base}://{self.username}:{self.password}@{meta}/{self.database if with_db and self.database else ''}"
            return f"{base}://{meta}/{self.database if with_db and self.database else ''}"
        return ""

    @model_validator(mode="after")
    def extract_uri(self):
        """
        Extract URI from connection string and fill in the respective fields.

        If the connection string is in the format of mongodb://user:password@host:port/database,
        the respective fields will be filled in. If the connection string is in the format of
        mongodb://host:port,host:port/database, the hosts will be split into a list of
        EndpointMeta objects.

        :return: The modified ClusterConnectionMeta object.
        :rtype: ClusterConnectionMeta
        """
        if self.uri:
            uri = re.sub(r"\w+:(//|/)", "", self.uri)
            clean_meta, others = (
                re.split(r"\/\?|\/", uri)
                if re.search(r"\/\?|\/", uri)
                else [uri, None]
            )
            cluster_uri = []
            if others and not self.database:
                if "&" in others:
                    for other in others.split("&"):
                        if "=" in other and re.search(r"authSource", other):
                            self.database = other.split("=")[-1]
                        elif "=" not in other:
                            self.database = other
                else:
                    self.database = others
            if "@" in clean_meta:
                auth_meta, clean_meta = re.split(r"\@", clean_meta)
                self.username, self.password = re.split(r"\:", auth_meta)

            for cluster in clean_meta.split(","):
                hostData = re.split(r"\:", cluster)
                cluster_uri.append(
                    EndpointMeta(
                        host=hostData[0],
                        port=int(hostData[1]),
                        endpoint=f"{hostData[0]}:{hostData[1]}",
                    )
                )
            self.cluster_uri = cluster_uri
        return self


class S3ConnectionMeta(EndpointMeta):
    access_key: Optional[str] = Field(
        None,
        description="S3 access key",
        validation_alias=AliasChoices(
            "access_key", "access", "user_access", "accessKey", "userAccess"
        ),
    )
    secret_key: Optional[str] = Field(
        None,
        description="S3 secret key",
        validation_alias=AliasChoices(
            "secret_key", "access_secret_key", "accessSecretKey", "accessSecret"
        ),
    )
    bucket: str = Field(
        ...,
        description="S3 bucket name",
        validation_alias=AliasChoices("bucket", "bucket_name", "bucketName"),
    )
    base_path: Optional[str] = Field("/", description="S3 base path")

    @property
    def json_meta(self) -> dict:
        """
        Return a dictionary of metadata for connecting to S3.

        :return: A dictionary with the endpoint_url, access_key, and secret_key.
        """
        return {
            "endpoint_url": f"http://{self.host}:{self.port}",
            "key": self.access_key,
            "secret": self.secret_key,
        }


class DatasetMeta(BaseModel):
    connection_meta: Optional[
        DBConnectionMeta | ClusterConnectionMeta | S3ConnectionMeta | str
    ] = Field(None, description="Connection metadata")
    name: str = Field(
        ...,
        description="Name of the dataset, it can refer to a path / to a file / a name of a / table in a database",
        validation_alias=AliasChoices(
            "name", "file_name", "fileName", "table", "tableName", "title"
        ),
    )
    tags: Optional[list[str]] = Field([], description="Tags for the dataset")


class RedisConnectionMeta(EndpointMeta, AuthMeta):
    database: int = Field(..., description="Database name")


class RMQConnectionMeta(EndpointMeta, AuthMeta):
    vhost: str = Field(
        "/",
        description="RMQ virtual host",
        validation_alias=AliasChoices(
            "vhost",
            "virtual_host",
            "virtualHost",
            "vhost_name",
            "v_host_name",
            "vHostName",
            "database",
            "db",
        ),
    )
    exchange: str = Field(
        ...,
        validation_alias=AliasChoices(
            "exchange", "exchange_name", "exchangeName"
        ),
    )
    exchange_durable: Optional[bool] = Field(
        None,
        validation_alias=AliasChoices("exchange_durable", "exchangeDurable"),
    )
    exchange_type: Optional[str] = Field(
        "topic",
        validation_alias=AliasChoices("exchange_type", "exchangTeype"),
    )
    routing_key: Optional[str] = Field(
        None,
        validation_alias=AliasChoices(
            "routing_key",
            "route_key",
            "routingKey",
            "routing_bind",
            "route_bind",
            "routeBind",
        ),
    )
    queue: Optional[str] = Field(
        None, validation_alias=AliasChoices("queue", "queue_name", "queueName")
    )
    queue_type: Optional[str] = Field(
        None, validation_alias=AliasChoices("queue_type", "queueType")
    )
    queue_durable: Optional[bool] = Field(
        None,
        validation_alias=AliasChoices(
            "queue_durable",
            "queue_durability",
            "queueDurable",
            "queueDurability",
        ),
    )
    queue_auto_delete: Optional[bool] = Field(
        None,
        validation_alias=AliasChoices("queue_auto_delete", "queueAutoDelete"),
    )
    queue_args: Optional[str] = Field(
        None,
        validation_alias=AliasChoices(
            "queue_args",
            "queueArgs",
            "queueArg",
            "queue_arg",
            "queue_argument",
            "queue_arguments",
            "queueArgument",
            "queueArguments",
            "queue_options",
            "queue_opts",
        ),
    )
    with_ssl: bool = Field(
        False,
        validation_alias=AliasChoices(
            "with_ssl",
            "queue_ssl",
            "using_ssl",
            "withSsl",
            "queueSsl",
            "usingSsl",
        ),
    )

    @property
    def queue_args_value(self) -> dict:
        if not self.queue_args:
            return {}
        try:
            return json.loads(self.queue_args)
        except json.JSONDecodeError:
            return {}

    @property
    def queue_durable_value(self) -> bool:
        if self.queue_durable is None:
            return False
        return self.queue_durable

    @property
    def queue_auto_delete_value(self) -> bool:
        if self.queue_auto_delete is None:
            return True
        return self.queue_auto_delete

    @property
    def valid_consumer(self) -> bool:
        return self.queue is not None

    @property
    def valid_producer(self) -> bool:
        return self.routing_key is not None

    def validate_use_case(self, use_case: str) -> None:
        if use_case == "consumer" and not self.valid_consumer:
            raise ValueError(
                "Invalid consumer RMQ configuration: 'queue' is required."
            )
        elif use_case == "producer" and not self.valid_producer:
            raise ValueError(
                "Invalid producer RMQ configuration: 'routing_key' is required."
            )
        elif use_case not in ("consumer", "producer"):
            raise ValueError(
                "Unknown use case. Expected 'consumer' or 'producer'."
            )


class KafkaMeta(BaseModel):
    bootstrap_servers: str | list[str] = Field(
        ...,
        validation_alias=AliasChoices(
            "bootstrap_servers", "bootstrap_server", "bootstrapServers"
        ),
    )
    group_id: Optional[str] = Field(
        "stream-engine:dummy-1.0",
        validation_alias=AliasChoices("group_id", "groupId"),
    )
    session_timeout: Optional[int] = Field(
        6000,
        description="in milliseconds",
        validation_alias=AliasChoices("session_timeout", "sessionTimeout"),
    )
    auto_offset_reset: Optional[str] = Field(
        "earliest",
        validation_alias=AliasChoices("auto_offset_reset", "autoOffsetReset"),
    )
    enable_auto_commit: Optional[bool] = Field(
        True,
        validation_alias=AliasChoices(
            "enable_auto_commit", "auto_commit", "enableAutoCommit"
        ),
    )
    topics: str | list[str] = Field(
        ...,
        validation_alias=AliasChoices(
            "topics", "topic", "topic_name", "topics_name", "topicName"
        ),
    )

    @property
    def topic_list(self) -> list[str]:
        if isinstance(self.topics, str):
            return [t.strip() for t in self.topics.split(",") if t.strip()]
        return self.topics

    @property
    def consumer_confluent_config_json(self) -> dict:
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": self.group_id,
            "session.timeout.ms": self.session_timeout,
            "auto.offset.reset": self.auto_offset_reset,
            "enable.auto.commit": self.enable_auto_commit,
        }

    @property
    def basic_confluent_config_json(self) -> dict:
        return {
            "bootstrap.servers": self.bootstrap_servers,
        }


database_meta_type = TypeVar(
    "database_meta_type", DatabaseConnectionMeta, HostMeta
)
queue_meta_type = TypeVar("queue_meta_type", DatabaseConnectionMeta, HostMeta)
connectionPayload = TypeVar(
    "connectionPayload", ConnectionMeta, ConnectionUriMeta
)


@deprecated(
    version="0.1.11", reason="use DatabaseConnector or QueueConnector instead"
)
class BaseConnection(ABC):
    def __init__(self, metadata: connectionPayload) -> None:
        self._metadata = metadata

    @abstractmethod
    def close(self) -> None:
        pass


class BaseConnector(ABC):
    def __init__(self) -> None:
        pass


@deprecated(
    version="0.1.14",
    reason="Now databaseConnector split into SQLConnector and NoSQLConnector",
)
class DatabaseConnector(BaseConnector):
    def __init__(self, meta: database_meta_type) -> None:
        self._meta: database_meta_type = meta  # pyright: ignore[reportGeneralTypeIssues]
        pass

    @abstractmethod
    def connect(self, **kwargs):
        pass

    @abstractmethod
    def get(self, table: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def get_all(self, table: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def insert(self, table: str, data: Any, **kwargs):
        pass

    @abstractmethod
    def insert_many(self, table: str, data: List[Any], **kwargs):
        pass

    @abstractmethod
    def update(self, table: str, query: Any, data: Any, **kwargs):
        pass

    @abstractmethod
    def delete(self, table: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass


class NosqlConnector(BaseConnector):
    def __init__(self, meta: database_meta_type) -> None:
        self._meta: database_meta_type = meta  # pyright: ignore[reportGeneralTypeIssues]
        pass

    @abstractmethod
    def connect(self, **kwargs):
        pass

    @abstractmethod
    def get(self, dataset: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def get_all(self, dataset: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def insert(self, dataset: str, data: Any, **kwargs):
        pass

    @abstractmethod
    def insert_many(self, dataset: str, data: List[Any], **kwargs):
        pass

    @abstractmethod
    def update(self, dataset: str, query: Any, data: Any, **kwargs):
        pass

    @abstractmethod
    def delete(self, dataset: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass


class SQLConnector(BaseConnector):
    def __init__(self, meta: database_meta_type) -> None:
        self._meta: database_meta_type = meta  # pyright: ignore[reportGeneralTypeIssues]
        pass

    @abstractmethod
    def connect(self, **kwargs):
        pass

    @abstractmethod
    def get(self, query: Any, **kwargs):
        pass

    @abstractmethod
    def get_all(self, query: Any, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass


class QueueConnector(BaseConnector):
    def __init__(self, meta: queue_meta_type) -> None:
        self._meta: queue_meta_type = meta  # pyright: ignore[reportGeneralTypeIssues]
        pass

    @abstractmethod
    def consumer_connect(self, queue: str, **kwargs):
        pass

    @abstractmethod
    def producer_connect(self, queue: str, **kwargs):
        pass

    @abstractmethod
    def consumer_close(self):
        pass

    @abstractmethod
    def producer_close(self):
        pass
