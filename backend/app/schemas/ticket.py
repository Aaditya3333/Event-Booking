from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.ticket import TicketType, TicketStatus


class TicketTierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    ticket_type: str = TicketType.GENERAL.value
    price: Decimal = Field(..., ge=0)
    currency: str = "USD"
    total_quantity: int = Field(..., gt=0)
    available_quantity: int = Field(..., ge=0)
    min_per_order: int = Field(1, gt=0)
    max_per_order: int = Field(10, gt=0)
    sale_start_time: Optional[datetime] = None
    sale_end_time: Optional[datetime] = None
    status: str = TicketStatus.AVAILABLE.value
    is_hidden: bool = False
    features: Optional[List[str]] = []
    restrictions: Optional[str] = None


class TicketTierCreate(TicketTierBase):
    pass


class TicketTierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    ticket_type: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = None
    total_quantity: Optional[int] = Field(None, gt=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    min_per_order: Optional[int] = Field(None, gt=0)
    max_per_order: Optional[int] = Field(None, gt=0)
    sale_start_time: Optional[datetime] = None
    sale_end_time: Optional[datetime] = None
    status: Optional[str] = None
    is_hidden: Optional[bool] = None
    features: Optional[List[str]] = None
    restrictions: Optional[str] = None


class TicketTierResponse(TicketTierBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    event_id: str
    sold_quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TicketBase(BaseModel):
    holder_name: str = Field(..., min_length=1, max_length=100)
    holder_email: str = Field(..., max_length=255)
    holder_phone: Optional[str] = Field(None, max_length=20)
    custom_fields: Optional[dict] = None


class TicketCreate(TicketBase):
    ticket_tier_id: str
    booking_id: str


class TicketResponse(TicketBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    ticket_tier_id: str
    booking_id: str
    ticket_number: str
    qr_code_url: Optional[str] = None
    is_valid: bool
    is_used: bool
    checked_in_at: Optional[datetime] = None
    checked_in_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class TicketCheckIn(BaseModel):
    ticket_number: str
    check_in_location: Optional[str] = None
    device_id: Optional[str] = None
    notes: Optional[str] = None


class TicketCheckInResponse(BaseModel):
    success: bool
    message: str
    ticket: Optional[TicketResponse] = None


class TicketValidationResponse(BaseModel):
    is_valid: bool
    ticket: Optional[TicketResponse] = None
    error_message: Optional[str] = None


class TicketAvailability(BaseModel):
    ticket_tier_id: str
    available_quantity: int
    total_quantity: int
    sold_quantity: int
    is_available: bool
    sale_status: str
