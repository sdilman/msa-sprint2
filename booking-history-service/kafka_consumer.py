import os
import json
from datetime import datetime
from collections import defaultdict
from kafka import KafkaConsumer
from threading import Thread, Lock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_BOOKING_TOPIC", "booking-events")


class BookingStatsCollector:
    def __init__(self):
        self.stats_lock = Lock()
        self.user_stats = defaultdict(int)
        self.hotel_stats = defaultdict(int)
        self.daily_stats = defaultdict(int)
        self.consumer = None
        self.consumer_thread = None
        self.running = False

    def start(self):
        """Start Kafka consumer in background thread"""
        self.running = True
        self.consumer_thread = Thread(target=self._consume_messages, daemon=True)
        self.consumer_thread.start()
        logger.info("Kafka consumer started")

    def stop(self):
        """Stop Kafka consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        logger.info("Kafka consumer stopped")

    def _consume_messages(self):
        """Consume messages from Kafka and update statistics"""
        try:
            self.consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',  # Читать с начала топика
                enable_auto_commit=True,
                group_id='booking-history-service',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )

            logger.info(f"Connected to Kafka topic: {KAFKA_TOPIC}")

            for message in self.consumer:
                if not self.running:
                    break

                try:
                    event = message.value
                    self._process_event(event)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")

    def _process_event(self, event):
        """Process a single event and update statistics"""
        if event.get('event_type') != 'booking_created':
            return

        user_id = event.get('user_id')
        hotel_id = event.get('hotel_id')
        created_at = event.get('created_at')

        if not all([user_id, hotel_id, created_at]):
            logger.warning(f"Incomplete event data: {event}")
            return

        # Extract date from ISO timestamp
        try:
            date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
            date_str = date.isoformat()
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return

        # Update statistics atomically
        with self.stats_lock:
            self.user_stats[user_id] += 1
            self.hotel_stats[hotel_id] += 1
            self.daily_stats[date_str] += 1

        logger.debug(f"Processed event: user={user_id}, hotel={hotel_id}, date={date_str}")

    def get_stats(self):
        """Get current statistics"""
        with self.stats_lock:
            return {
                "by_user": dict(self.user_stats),
                "by_hotel": dict(self.hotel_stats),
                "by_date": dict(self.daily_stats),
                "total_events": sum(self.user_stats.values())
            }

    def reset_stats(self):
        """Reset all statistics (for testing)"""
        with self.stats_lock:
            self.user_stats.clear()
            self.hotel_stats.clear()
            self.daily_stats.clear()
        logger.info("Statistics reset")


# Global instance
stats_collector = BookingStatsCollector()