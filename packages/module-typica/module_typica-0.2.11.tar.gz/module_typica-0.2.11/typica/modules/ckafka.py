from confluent_kafka import Consumer, Producer

from typica.connection import KafkaMeta


class KafkaConnector:
    consumer: Consumer
    producer: Producer

    def __init__(self, meta: KafkaMeta) -> None:
        """
        Initialize the Kafka connector with the given connection metadata.

        :param meta: The metadata for Kafka connection.
        :type meta: KafkaMeta
        """
        self._meta: KafkaMeta = meta

    def initizalize_producer(self, **kwargs) -> None:
        """
        Initialize a Kafka producer.

        :raises Exception: If the connection to the Kafka server fails.
        """
        try:
            self.producer = Producer(self._meta.confluent_config(**kwargs))
        except Exception as e:
            raise e

    def initizalize_consumer(self, **kwargs) -> None:
        """
        Initialize a Kafka consumer.

        :raises Exception: If the connection to the Kafka server fails.
        """

        try:
            self.consumer = Consumer(self._meta.confluent_config(**kwargs))
        except Exception as e:
            raise e

    def close(self) -> None:
        """
        Close the connection to the Kafka server.

        This method is a no-op if the connection is already closed.
        """
        if hasattr(self, "consumer") and self.consumer:
            self.consumer.close()
