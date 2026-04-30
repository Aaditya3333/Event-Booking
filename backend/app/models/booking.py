from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Booking Info
    booking_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(20), default=BookingStatus.PENDING.value)
    
    # Pricing
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    service_fee = Column(Numeric(10, 2), default=0)
    
    # Customer Info
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(20))
    
    # Payment
    payment_status = Column(String(20), default="pending")
    payment_method = Column(String(50))
    payment_id = Column(String(100))  # Stripe payment ID
    
    # Timing
    booking_time = Column(DateTime(timezone=True), server_default=func.now())
    confirmation_time = Column(DateTime(timezone=True))
    cancellation_time = Column(DateTime(timezone=True))
    expiry_time = Column(DateTime(timezone=True))
    
    # Notes
    notes = Column(Text)
    special_requests = Column(Text)
    
    # Booking metadata
    booking_metadata = Column(JSON)  # Additional booking information
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
    tickets = relationship("Ticket", back_populates="booking", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_total_amount_non_negative'),
        CheckConstraint('discount_amount >= 0', name='check_discount_amount_non_negative'),
        CheckConstraint('tax_amount >= 0', name='check_tax_amount_non_negative'),
        CheckConstraint('service_fee >= 0', name='check_service_fee_non_negative'),
    )
    
    def __repr__(self):
        return f"<Booking(id={self.id}, booking_number={self.booking_number}, status={self.status})>"


class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    ticket_tier_id = Column(UUID(as_uuid=True), ForeignKey("ticket_tiers.id"), nullable=False)
    
    # Item Details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    booking = relationship("Booking")
    ticket_tier = relationship("TicketTier")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='check_unit_price_non_negative'),
        CheckConstraint('total_price >= 0', name='check_total_price_non_negative'),
    )
    
    def __repr__(self):
        return f"<BookingItem(id={self.id}, quantity={self.quantity}, unit_price={self.unit_price})>"
