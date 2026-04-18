from concurrent import futures
from datetime import datetime, timezone
import os

import grpc
import psycopg2
import booking_pb2
import booking_pb2_grpc

from message_broker import create_kafka_topic_if_not_exists, KAFKA_TOPIC


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://booking-service:booking-service@booking-service-db:5432/booking-service",
)


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
    def CreateBooking(self, request, context):
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
        
        self.kafka_producer.send(
            KAFKA_TOPIC,
            value={
                "event_type": "booking_created",
                "booking_id": str(booking_id),
                **booking_data}
        )

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
