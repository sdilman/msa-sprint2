import os
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import json


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_BOOKING_TOPIC", "booking-events")


def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all'
    )

def create_kafka_topic_if_not_exists():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        topic = NewTopic(
            name=KAFKA_TOPIC,
            num_partitions=3,
            replication_factor=1
        )
        admin_client.create_topics(new_topics=[topic])
    except TopicAlreadyExistsError:
        pass  # Топик уже существует