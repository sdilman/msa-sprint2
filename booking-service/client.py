import grpc
import booking_pb2
import booking_pb2_grpc


channel = grpc.insecure_channel("localhost:9090")
stub = booking_pb2_grpc.BookingServiceStub(channel)

response = stub.CreateBooking(
    booking_pb2.BookingRequest(
        user_id="user-1",
        hotel_id="hotel-42",
        promo_code="SALE10"
    )
)

print(response)
