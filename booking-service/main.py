import grpc
import logging
import requests
import os
from concurrent import futures
from sqlalchemy.orm import Session

import booking_pb2
import booking_pb2_grpc
from database import get_db, Booking, create_tables, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monolith service configuration
MONOLITH_URL = os.getenv('MONOLITH_URL', 'http://hotelio-monolith:8080')

class BookingServiceServicer(booking_pb2_grpc.BookingServiceServicer):
    """Implementation of BookingService gRPC service based on Java logic"""
    
    def CreateBooking(self, request, context):
        """Create a new booking with validation logic from Java service"""
        logger.info(f"Creating booking: userId={request.user_id}, hotelId={request.hotel_id}, promoCode={request.promo_code}")
        
        try:
            # Validate user and hotel (simplified for now - in real implementation would call other services)
            self._validate_user(request.user_id)
            self._validate_hotel(request.hotel_id)
            
            # Calculate base price and discount
            base_price = self._resolve_base_price(request.user_id)
            discount = self._resolve_promo_discount(request.promo_code, request.user_id)
            
            final_price = base_price - discount
            logger.info(f"Final price calculated: base={base_price}, discount={discount}, final={final_price}")
            
            # Create booking in database
            db = SessionLocal()
            try:
                booking = Booking(
                    user_id=request.user_id,
                    hotel_id=request.hotel_id,
                    promo_code=request.promo_code if request.promo_code else None,
                    discount_percent=discount,
                    price=final_price
                )
                
                db.add(booking)
                db.commit()
                db.refresh(booking)
            finally:
                db.close()
            
            # Return response
            return booking_pb2.BookingResponse(
                id=booking.id,
                user_id=booking.user_id,
                hotel_id=booking.hotel_id,
                promo_code=booking.promo_code if booking.promo_code else "",
                discount_percent=booking.discount_percent,
                price=booking.price,
                created_at=booking.created_at.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return booking_pb2.BookingResponse()
    
    def ListBookings(self, request, context):
        """List bookings for a user"""
        logger.info(f"Listing bookings for user: {request.user_id}")
        
        try:
            db = SessionLocal()
            try:
                if request.user_id:
                    bookings = db.query(Booking).filter(Booking.user_id == request.user_id).all()
                else:
                    bookings = db.query(Booking).all()
                
                booking_responses = []
                for booking in bookings:
                    booking_responses.append(booking_pb2.BookingResponse(
                        id=booking.id,
                        user_id=booking.user_id,
                        hotel_id=booking.hotel_id,
                        promo_code=booking.promo_code if booking.promo_code else "",
                        discount_percent=booking.discount_percent,
                        price=booking.price,
                        created_at=booking.created_at.isoformat()
                    ))
            finally:
                db.close()
            
            return booking_pb2.BookingListResponse(bookings=booking_responses)
            
        except Exception as e:
            logger.error(f"Error listing bookings: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return booking_pb2.BookingListResponse()
    
    def _validate_user(self, user_id):
        """Validate user by calling monolith user service via REST HTTP"""
        if not user_id:
            raise ValueError("User ID is required")
        
        try:
            # Check if user is active
            response = requests.get(f"{MONOLITH_URL}/api/users/{user_id}/active", timeout=5)
            if not response.ok:
                raise ValueError(f"Failed to validate user active status: {response.status_code}")
            if not response.json():
                raise ValueError("User is inactive")
            
            # Check if user is blacklisted
            response = requests.get(f"{MONOLITH_URL}/api/users/{user_id}/blacklisted", timeout=5)
            if not response.ok:
                raise ValueError(f"Failed to validate user blacklist status: {response.status_code}")
            if response.json():
                raise ValueError("User is blacklisted")
                
            logger.debug(f"User {user_id} validated successfully")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling user service: {str(e)}")
            raise ValueError("User service unavailable")
    
    def _validate_hotel(self, hotel_id):
        """Validate hotel by calling monolith hotel and review services via REST HTTP"""
        if not hotel_id:
            raise ValueError("Hotel ID is required")
        
        try:
            # Check if hotel is operational
            response = requests.get(f"{MONOLITH_URL}/api/hotels/{hotel_id}/operational", timeout=5)
            if not response.ok:
                raise ValueError(f"Failed to validate hotel operational status: {response.status_code}")
            if not response.json():
                raise ValueError("Hotel is not operational")
            
            # Check if hotel is trusted based on reviews
            response = requests.get(f"{MONOLITH_URL}/api/reviews/hotel/{hotel_id}/trusted", timeout=5)
            if not response.ok:
                raise ValueError(f"Failed to validate hotel trust status: {response.status_code}")
            if not response.json():
                raise ValueError("Hotel is not trusted based on reviews")
            
            # Check if hotel is fully booked
            response = requests.get(f"{MONOLITH_URL}/api/hotels/{hotel_id}/fully-booked", timeout=5)
            if not response.ok:
                raise ValueError(f"Failed to validate hotel booking status: {response.status_code}")
            if response.json():
                raise ValueError("Hotel is fully booked")
                
            logger.debug(f"Hotel {hotel_id} validated successfully")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling hotel service: {str(e)}")
            raise ValueError("Hotel service unavailable")
    
    def _resolve_base_price(self, user_id):
        """Resolve base price by calling monolith user service to get user status"""
        try:
            # Get user status from monolith
            response = requests.get(f"{MONOLITH_URL}/api/users/{user_id}/status", timeout=5)
            if not response.ok:
                logger.warning(f"Failed to get user status: {response.status_code}, using default price")
                return 100.0
            
            user_status = response.text.strip('"')
            is_vip = user_status and user_status.upper() == "VIP"
            
            base_price = 80.0 if is_vip else 100.0
            logger.debug(f"User {user_id} has status '{user_status}', base price {base_price}")
            return base_price
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling user service for status: {str(e)}, using default price")
            return 100.0
    
    def _resolve_promo_discount(self, promo_code, user_id):
        """Resolve promo code discount by calling monolith promo service via REST HTTP"""
        if not promo_code:
            return 0.0
        
        try:
            # Validate promo code with monolith
            response = requests.post(
                f"{MONOLITH_URL}/api/promos/validate",
                params={"code": promo_code, "userId": user_id},
                timeout=5
            )
            
            if not response.ok:
                logger.info(f"Promo code '{promo_code}' validation failed: {response.status_code}")
                return 0.0
            
            promo_data = response.json()
            discount = promo_data.get("discount", 0.0)
            
            if discount > 0:
                logger.debug(f"Promo code '{promo_code}' applied with discount {discount}")
            else:
                logger.info(f"Promo code '{promo_code}' is invalid or not applicable for user {user_id}")
            
            return discount
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling promo service: {str(e)}")
            return 0.0

def serve():
    """Start the gRPC server"""
    # Create database tables
    create_tables()
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServiceServicer_to_server(BookingServiceServicer(), server)
    
    # Use port 9090 as specified in docker-compose
    server.add_insecure_port('[::]:9090')
    
    logger.info("Starting booking service on port 9090")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()