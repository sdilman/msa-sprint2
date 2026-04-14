from concurrent import futures
import grpc
import booking_pb2
import booking_pb2_grpc
import uuid
from datetime import datetime


class BookingService(booking_pb2_grpc.BookingServiceServicer):
    def CreateBooking(self, request, context):
        return booking_pb2.BookingResponse(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            hotel_id=request.hotel_id,
            promo_code=request.promo_code,
            discount_percent=10.0 if request.promo_code else 0.0,
            price=100.0,
            created_at=datetime.utcnow().isoformat()
        )

    def ListBookings(self, request, context):
        booking = booking_pb2.BookingResponse(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            hotel_id="hotel-1",
            promo_code="",
            discount_percent=0.0,
            price=100.0,
            created_at=datetime.utcnow().isoformat()
        )
        return booking_pb2.BookingListResponse(bookings=[booking])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServiceServicer_to_server(BookingService(), server)
    server.add_insecure_port("[::]:9090")
    server.start()
    print("gRPC server started on port 9090")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
