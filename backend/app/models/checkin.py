from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class CheckInStatus(enum.Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ALREADY_CHECKED_IN = "already_checked_in"
    INVALID_TICKET = "invalid_ticket"
    EXPIRED = "expired"


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False)
    checked_in_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Check-in Details
    status = Column(String(20), default=CheckInStatus.SUCCESSFUL.value)
    check_in_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Location
    check_in_location = Column(String(200))
    device_id = Column(String(100))  # Device used for check-in
    
    # Additional Info
    notes = Column(Text)
    checkin_metadata = Column(JSON)  # Additional check-in information
    
    # Relationships
    ticket = relationship("Ticket", back_populates="check_in")
    staff_member = relationship("User", foreign_keys=[checked_in_by])
    
    def __repr__(self):
        return f"<CheckIn(id={self.id}, ticket_id={self.ticket_id}, status={self.status})>"
