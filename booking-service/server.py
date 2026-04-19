from concurrent import futures
from datetime import datetime, timezone
import os
import logging

import grpc
import psycopg2
import requests
import booking_pb2
import booking_pb2_grpc

from message_broker import create_kafka_topic_if_not_exists, KAFKA_TOPIC


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://booking-service:booking-service@booking-service-db:5432/booking-service",
)
MONOLITH_URL = os.getenv("MONOLITH_URL", "http://monolith:8080")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def row_to_booking_response(row):
    return booking_pb2.BookingResponse(
        id=str(row[0]),
        user_id=row[1],
        hotel_id=row[2],
        promo_code=row[3] or "",
        discount_percent=float(row[4] or 0.0),
        price=float(row[5] or 0.0),
        created_at=row[6].isoformat() if row[6] else "",
    )


class BookingService(booking_pb2_grpc.BookingServiceServicer):
    def __init__(self):
        from message_broker import get_kafka_producer
        self.kafka_producer = get_kafka_producer()

    def CreateBooking(self, request, context):
        # Check if user is active before creating booking
        try:
            user_active_url = f"{MONOLITH_URL}/api/users/{request.user_id}/active"
            response = requests.get(user_active_url, timeout=5)
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Failed to check user active status. Status code: {response.status_code}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Failed to check user active status. Status code: {response.status_code}")
                return booking_pb2.BookingResponse()
            
            # If the user is not active, return an error
            if not response.text.strip().lower() == 'true':
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"User {request.user_id} is not active")
                return booking_pb2.BookingResponse()
        except requests.exceptions.RequestException as error:
            logger.error(f"Failed to check user active status: {error}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to check user active status: {error}")
            return booking_pb2.BookingResponse()
        except Exception as error:
            logger.error(f"Unexpected error when checking user active status: {error}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Unexpected error when checking user active status: {error}")
            return booking_pb2.BookingResponse()

        # Check if hotel is trusted
        try:
            hotel_trusted_url = f"{MONOLITH_URL}/api/reviews/hotel/{request.hotel_id}/trusted"
            response = requests.get(hotel_trusted_url, timeout=5)
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Failed to check hotel trusted status. Status code: {response.status_code}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Failed to check hotel trusted status. Status code: {response.status_code}")
                return booking_pb2.BookingResponse()
            
            # If the hotel is not trusted, return an error
            if not response.text.strip().lower() == 'true':
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"Hotel {request.hotel_id} is not trusted")
                return booking_pb2.BookingResponse()
        except requests.exceptions.RequestException as error:
            logger.error(f"Failed to check hotel trusted status: {error}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to check hotel trusted status: {error}")
            return booking_pb2.BookingResponse()
        except Exception as error:
            logger.error(f"Unexpected error when checking hotel trusted status: {error}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Unexpected error when checking hotel trusted status: {error}")
            return booking_pb2.BookingResponse()

        # Check if hotel is fully booked
        try:
            hotel_fully_booked_url = f"{MONOLITH_URL}/api/hotels/{request.hotel_id}/fully-booked"
            response = requests.get(hotel_fully_booked_url, timeout=5)
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Failed to check hotel fully booked status. Status code: {response.status_code}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Failed to check hotel fully booked status. Status code: {response.status_code}")
                return booking_pb2.BookingResponse()
            
            # If the hotel is fully booked, return an error
            if response.text.strip().lower() == 'true':
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                context.set_details(f"Hotel {request.hotel_id} is fully booked")
                return booking_pb2.BookingResponse()
        except requests.exceptions.RequestException as error:
            logger.error(f"Failed to check hotel fully booked status: {error}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to check hotel fully booked status: {error}")
            return booking_pb2.BookingResponse()
        except Exception as error:
            logger.error(f"Unexpected error when checking hotel fully booked status: {error}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Unexpected error when checking hotel fully booked status: {error}")
            return booking_pb2.BookingResponse()

        discount_percent = 10.0 if request.promo_code else 0.0
        price = 100.0
        created_at = datetime.now(timezone.utc)

        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO booking (user_id, hotel_id, promo_code, discount_percent, price, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            request.user_id,
                            request.hotel_id,
                            request.promo_code or None,
                            discount_percent,
                            price,
                            created_at,
                        ),
                    )
                    booking_id = cursor.fetchone()[0]
        except Exception as error:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to create booking: {error}")
            return booking_pb2.BookingResponse()

        booking_data = {
            "user_id": request.user_id,
            "hotel_id": request.hotel_id,
            "promo_code": request.promo_code,
            "discount_percent": discount_percent,
            "price": price,
            "created_at": created_at.isoformat(),
        }
        
        # Publish event to Kafka with error handling
        try:
            future = self.kafka_producer.send(
                KAFKA_TOPIC,
                value={
                    "event_type": "booking_created",
                    "booking_id": str(booking_id),
                    **booking_data
                }
            )
            # Wait for the send to complete (optional, can be async)
            record_metadata = future.get(timeout=10)
            logger.info(f"Event published to Kafka: topic={record_metadata.topic}, "
                        f"partition={record_metadata.partition}, offset={record_metadata.offset}")
        except Exception as error:
            logger.error(f"Failed to publish event to Kafka: {error}")
            # Note: We don't return an error to the client for Kafka publishing failures
            # as the booking was successfully created in the database

        return booking_pb2.BookingResponse(
            id=str(booking_id),
            **booking_data
        )

    def ListBookings(self, request, context):
        where_close = f"WHERE user_id = '{request.user_id}'" if request.user_id else ""
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""
                        SELECT id, user_id, hotel_id, promo_code, discount_percent, price, created_at
                        FROM booking
                        {where_close}
                        ORDER BY created_at DESC
                        """
                    )
                    rows = cursor.fetchall()
        except Exception as error:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list bookings: {error}")
            return booking_pb2.BookingListResponse(bookings=[])

        bookings = [row_to_booking_response(row) for row in rows]
        return booking_pb2.BookingListResponse(bookings=bookings)

    def __del__(self):
        """Cleanup Kafka producer on shutdown"""
        if hasattr(self, 'kafka_producer'):
            try:
                self.kafka_producer.flush()
                self.kafka_producer.close()
                logger.info("Kafka producer closed successfully")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")


def serve():
    create_kafka_topic_if_not_exists()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServiceServicer_to_server(BookingService(), server)
    server.add_insecure_port("[::]:9090")
    server.start()
    print("gRPC server started on port 9090")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
