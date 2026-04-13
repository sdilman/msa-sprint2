import grpc
import booking_pb2
import booking_pb2_grpc

def test_create_booking():
    """Test the CreateBooking RPC"""
    with grpc.insecure_channel('localhost:9090') as channel:
        stub = booking_pb2_grpc.BookingServiceStub(channel)
        
        # Test creating a booking
        request = booking_pb2.BookingRequest(
            user_id="user123",
            hotel_id="hotel456",
            promo_code="WELCOME10"
        )
        
        try:
            response = stub.CreateBooking(request)
            print(f"Booking created successfully:")
            print(f"  ID: {response.id}")
            print(f"  User ID: {response.user_id}")
            print(f"  Hotel ID: {response.hotel_id}")
            print(f"  Promo Code: {response.promo_code}")
            print(f"  Discount: {response.discount_percent}")
            print(f"  Price: {response.price}")
            print(f"  Created At: {response.created_at}")
        except grpc.RpcError as e:
            print(f"Error creating booking: {e.details()}")

def test_list_bookings():
    """Test the ListBookings RPC"""
    with grpc.insecure_channel('localhost:9090') as channel:
        stub = booking_pb2_grpc.BookingServiceStub(channel)
        
        # Test listing bookings
        request = booking_pb2.BookingListRequest(user_id="user123")
        
        try:
            response = stub.ListBookings(request)
            print(f"\nFound {len(response.bookings)} bookings:")
            for booking in response.bookings:
                print(f"  - {booking.id}: {booking.user_id} -> {booking.hotel_id} (${booking.price})")
        except grpc.RpcError as e:
            print(f"Error listing bookings: {e.details()}")

if __name__ == '__main__':
    print("Testing Booking Service...")
    test_create_booking()
    test_list_bookings()