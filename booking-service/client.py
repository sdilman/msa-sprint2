import grpc
import booking_pb2
import booking_pb2_grpc


channel = grpc.insecure_channel("localhost:9090")
stub = booking_pb2_grpc.BookingServiceStub(channel)

# response_create = stub.CreateBooking(
#     booking_pb2.BookingRequest(
#         user_id="user-1",
#         hotel_id="hotel-42",
#         promo_code="SALE10"
#     )
# )

# print("Create")
# print(response_create)

# response_list_user = stub.ListBookings(
#     booking_pb2.BookingRequest(
#         user_id="user-1"
#     )
# )

# print("List user")
# print(response_list_user)

response_list_all = stub.ListBookings(
    booking_pb2.BookingRequest()
)

print("List all")
print(response_list_all)
