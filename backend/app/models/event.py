from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class EventStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class EventType(enum.Enum):
    CONFERENCE = "conference"
    CONCERT = "concert"
    FESTIVAL = "festival"
    WORKSHOP = "workshop"
    SPORTS = "sports"
    THEATER = "theater"
    OTHER = "other"


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organizer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Basic Info
    title = Column(String(200), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Event Details
    event_type = Column(String(50), default=EventType.OTHER.value)
    status = Column(String(20), default=EventStatus.DRAFT.value)
    
    # Location
    venue_name = Column(String(200))
    venue_address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    is_virtual = Column(Boolean, default=False)
    virtual_url = Column(String(500))
    
    # Schedule
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    doors_open = Column(DateTime(timezone=True))
    
    # Capacity
    max_capacity = Column(Integer)
    current_capacity = Column(Integer, default=0)
    
    # Pricing
    currency = Column(String(3), default="USD")
    min_price = Column(Numeric(10, 2))
    max_price = Column(Numeric(10, 2))
    
    # Media
    cover_image_url = Column(String(500))
    banner_image_url = Column(String(500))
    
    # Additional Info
    tags = Column(JSON)  # Use JSON for SQLite compatibility
    age_restriction = Column(String(20))
    accessibility_info = Column(Text)
    terms_and_conditions = Column(Text)
    
    # SEO
    slug = Column(String(200), unique=True, index=True)
    meta_title = Column(String(200))
    meta_description = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Settings
    allow_waitlist = Column(Boolean, default=True)
    require_approval = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # Analytics
    view_count = Column(Integer, default=0)
    booking_count = Column(Integer, default=0)
    
    # Relationships
    organizer = relationship("User", back_populates="events")
    images = relationship("EventImage", back_populates="event", cascade="all, delete-orphan")
    ticket_tiers = relationship("TicketTier", back_populates="event", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, status={self.status})>"


class EventImage(Base):
    __tablename__ = "event_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False)
    
    url = Column(String(500), nullable=False)
    alt_text = Column(String(200))
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="images")
    
    def __repr__(self):
        return f"<EventImage(id={self.id}, event_id={self.event_id}, is_primary={self.is_primary})>"
