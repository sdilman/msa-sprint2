import os
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://booking-service:booking-service@localhost:5433/booking-service')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    hotel_id = Column(String, nullable=False)
    promo_code = Column(String, nullable=True)
    discount_percent = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()