from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.event import EventStatus, EventType


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    event_type: str = EventType.OTHER.value
    venue_name: Optional[str] = Field(None, max_length=200)
    venue_address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_virtual: bool = False
    virtual_url: Optional[str] = Field(None, max_length=500)
    start_time: datetime
    end_time: datetime
    doors_open: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, gt=0)
    currency: str = "USD"
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    banner_image_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = []
    age_restriction: Optional[str] = Field(None, max_length=20)
    accessibility_info: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    slug: Optional[str] = Field(None, max_length=200)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    allow_waitlist: bool = True
    require_approval: bool = False


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    event_type: Optional[str] = None
    venue_name: Optional[str] = Field(None, max_length=200)
    venue_address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_virtual: Optional[bool] = None
    virtual_url: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    doors_open: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, gt=0)
    currency: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    banner_image_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    age_restriction: Optional[str] = Field(None, max_length=20)
    accessibility_info: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    slug: Optional[str] = Field(None, max_length=200)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    allow_waitlist: Optional[bool] = None
    require_approval: Optional[bool] = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    organizer_id: str
    status: EventStatus
    current_capacity: int
    is_featured: bool
    view_count: int
    booking_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    size: int
    pages: int


class EventImageBase(BaseModel):
    url: str = Field(..., max_length=500)
    alt_text: Optional[str] = Field(None, max_length=200)
    is_primary: bool = False
    sort_order: int = 0


class EventImageCreate(EventImageBase):
    pass


class EventImageResponse(EventImageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    event_id: str
    created_at: datetime


class EventPublish(BaseModel):
    publish_now: bool = True
    scheduled_time: Optional[datetime] = None


class EventSearchParams(BaseModel):
    query: Optional[str] = None
    event_type: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    is_virtual: Optional[bool] = None
    is_featured: Optional[bool] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = "desc"
