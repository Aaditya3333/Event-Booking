from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class TicketType(enum.Enum):
    GENERAL = "general"
    VIP = "vip"
    STUDENT = "student"
    SENIOR = "senior"
    CHILD = "child"
    GROUP = "group"
    EARLY_BIRD = "early_bird"


class TicketStatus(enum.Enum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    UNAVAILABLE = "unavailable"
    HIDDEN = "hidden"


class TicketTier(Base):
    __tablename__ = "ticket_tiers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False)
    
    # Basic Info
    name = Column(String(100), nullable=False)
    description = Column(Text)
    ticket_type = Column(String(20), default=TicketType.GENERAL.value)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Availability
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    sold_quantity = Column(Integer, default=0)
    min_per_order = Column(Integer, default=1)
    max_per_order = Column(Integer, default=10)
    
    # Schedule
    sale_start_time = Column(DateTime(timezone=True))
    sale_end_time = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(20), default=TicketStatus.AVAILABLE.value)
    is_hidden = Column(Boolean, default=False)
    
    # Features
    features = Column(JSON)  # List of features/benefits
    restrictions = Column(Text)  # Age restrictions, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="ticket_tiers")
    tickets = relationship("Ticket", back_populates="ticket_tier", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_non_negative'),
        CheckConstraint('total_quantity >= 0', name='check_total_quantity_non_negative'),
        CheckConstraint('available_quantity >= 0', name='check_available_quantity_non_negative'),
        CheckConstraint('sold_quantity >= 0', name='check_sold_quantity_non_negative'),
        CheckConstraint('min_per_order > 0', name='check_min_per_order_positive'),
        CheckConstraint('max_per_order >= min_per_order', name='check_max_per_order_ge_min'),
    )
    
    def __repr__(self):
        return f"<TicketTier(id={self.id}, name={self.name}, price={self.price})>"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_tier_id = Column(String(36), ForeignKey("ticket_tiers.id"), nullable=False)
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False)
    
    # Ticket Info
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    qr_code_url = Column(String(500))
    
    # Holder Info
    holder_name = Column(String(100), nullable=False)
    holder_email = Column(String(255), nullable=False)
    holder_phone = Column(String(20))
    
    # Status
    is_valid = Column(Boolean, default=True)
    is_used = Column(Boolean, default=False)
    checked_in_at = Column(DateTime(timezone=True))
    checked_in_by = Column(String(36), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Custom Fields
    custom_fields = Column(JSON)  # For additional ticket information
    
    # Relationships
    ticket_tier = relationship("TicketTier", back_populates="tickets")
    booking = relationship("Booking", back_populates="tickets")
    check_in = relationship("CheckIn", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_number={self.ticket_number}, is_used={self.is_used})>"
