from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Booking Service", version="1.0.0")

# Pydantic models based on proto file
class BookingRequest(BaseModel):
    user_id: str
    hotel_id: str
    promo_code: Optional[str] = None

class BookingResponse(BaseModel):
    id: str
    user_id: str
    hotel_id: str
    promo_code: Optional[str] = None
    discount_percent: float
    price: float
    created_at: str

class BookingListRequest(BaseModel):
    user_id: str

class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]

# In-memory storage for demo purposes
bookings_db = {}

@app.post("/booking", response_model=BookingResponse)
async def create_booking(booking_request: BookingRequest):
    """Create a new booking"""
    # Generate unique ID
    booking_id = str(uuid.uuid4())
    
    # Stub logic - in real implementation, this would calculate actual price and discount
    discount_percent = 10.0 if booking_request.promo_code else 0.0
    price = 100.0 * (1 - discount_percent / 100)  # Base price with discount
    
    booking = BookingResponse(
        id=booking_id,
        user_id=booking_request.user_id,
        hotel_id=booking_request.hotel_id,
        promo_code=booking_request.promo_code,
        discount_percent=discount_percent,
        price=price,
        created_at=datetime.now().isoformat()
    )
    
    # Store booking
    if booking_request.user_id not in bookings_db:
        bookings_db[booking_request.user_id] = []
    bookings_db[booking_request.user_id].append(booking)
    
    return booking

@app.get("/bookings/{user_id}", response_model=BookingListResponse)
async def list_bookings(user_id: str):
    """Get all bookings for a user"""
    user_bookings = bookings_db.get(user_id, [])
    return BookingListResponse(bookings=user_bookings)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)