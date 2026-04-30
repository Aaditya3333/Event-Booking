from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.booking import BookingStatus


class BookingItemCreate(BaseModel):
    ticket_tier_id: str = Field(..., description="ID of the ticket tier")
    quantity: int = Field(..., gt=0, description="Number of tickets")


class BookingCreate(BaseModel):
    event_id: str = Field(..., description="ID of the event")
    items: List[BookingItemCreate] = Field(..., min_items=1, description="List of booking items")
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_email: str = Field(..., max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    special_requests: Optional[str] = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    event_id: str
    booking_number: str
    status: BookingStatus
    total_amount: Decimal
    currency: str
    discount_amount: Decimal
    tax_amount: Decimal
    service_fee: Decimal
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    payment_status: str
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    booking_time: datetime
    confirmation_time: Optional[datetime] = None
    cancellation_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    notes: Optional[str] = None
    special_requests: Optional[str] = None


class BookingItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    booking_id: str
    ticket_tier_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    created_at: datetime


class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    total: int
    page: int
    size: int
    pages: int


class BookingSummary(BaseModel):
    event_id: str
    event_title: str
    booking_number: str
    total_amount: Decimal
    currency: str
    status: str
    created_at: datetime
    tickets_count: int


class BookingCancel(BaseModel):
    reason: Optional[str] = "User requested"
    refund_requested: bool = False
