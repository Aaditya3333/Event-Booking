from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.event import Event, EventImage, EventStatus
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse, EventListResponse,
    EventImageCreate, EventImageResponse, EventPublish, EventSearchParams
)
from app.auth.dependencies import get_current_user, get_current_active_user, get_organizer_user

router = APIRouter()


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new event"""
    
    # Generate unique slug if not provided
    if not event_data.slug:
        base_slug = event_data.title.lower().replace(" ", "-")
        slug = base_slug
        counter = 1
        
        while True:
            stmt = select(Event).where(Event.slug == slug)
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        event_data.slug = slug
    
    # Create event
    event = Event(
        organizer_id=current_user.id,
        title=event_data.title,
        description=event_data.description,
        short_description=event_data.short_description,
        event_type=event_data.event_type,
        venue_name=event_data.venue_name,
        venue_address=event_data.venue_address,
        city=event_data.city,
        country=event_data.country,
        is_virtual=event_data.is_virtual,
        virtual_url=event_data.virtual_url,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        doors_open=event_data.doors_open,
        max_capacity=event_data.max_capacity,
        currency=event_data.currency,
        min_price=event_data.min_price,
        max_price=event_data.max_price,
        cover_image_url=event_data.cover_image_url,
        banner_image_url=event_data.banner_image_url,
        tags=event_data.tags,
        age_restriction=event_data.age_restriction,
        accessibility_info=event_data.accessibility_info,
        terms_and_conditions=event_data.terms_and_conditions,
        slug=event_data.slug,
        meta_title=event_data.meta_title,
        meta_description=event_data.meta_description,
        allow_waitlist=event_data.allow_waitlist,
        require_approval=event_data.require_approval,
        status=EventStatus.DRAFT.value,
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return event


@router.get("/", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    is_virtual: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db)
):
    """List events with filtering and pagination"""
    
    # Build query
    query = select(Event).where(Event.status == EventStatus.PUBLISHED.value)
    
    # Apply filters
    if search:
        query = query.where(
            or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
                Event.short_description.ilike(f"%{search}%")
            )
        )
    
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    if city:
        query = query.where(Event.city.ilike(f"%{city}%"))
    
    if country:
        query = query.where(Event.country.ilike(f"%{country}%"))
    
    if start_date:
        query = query.where(Event.start_time >= start_date)
    
    if end_date:
        query = query.where(Event.end_time <= end_date)
    
    if is_virtual is not None:
        query = query.where(Event.is_virtual == is_virtual)
    
    if is_featured is not None:
        query = query.where(Event.is_featured == is_featured)
    
    # Apply sorting
    sort_column = getattr(Event, sort_by, Event.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()
    
    pages = (total + size - 1) // size
    
    return EventListResponse(
        events=events,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/my-events", response_model=EventListResponse)
async def list_my_events(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's events"""
    
    query = select(Event).where(Event.organizer_id == current_user.id)
    
    if status_filter:
        query = query.where(Event.status == status_filter)
    
    query = query.order_by(Event.created_at.desc())
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()
    
    pages = (total + size - 1) // size
    
    return EventListResponse(
        events=events,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get event by ID"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Increment view count
    event.view_count += 1
    await db.commit()
    
    return event


@router.get("/slug/{slug}", response_model=EventResponse)
async def get_event_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get event by slug"""
    
    stmt = select(Event).where(Event.slug == slug)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Increment view count
    event.view_count += 1
    await db.commit()
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check ownership
    if event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update event fields
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    await db.commit()
    await db.refresh(event)
    
    return event


@router.post("/{event_id}/publish")
async def publish_event(
    event_id: str,
    publish_data: EventPublish,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Publish event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check ownership
    if event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update event status
    if publish_data.publish_now:
        event.status = EventStatus.PUBLISHED.value
        event.published_at = datetime.utcnow()
    elif publish_data.scheduled_time:
        event.published_at = publish_data.scheduled_time
        # TODO: Schedule publishing with Celery
    
    await db.commit()
    
    return {"message": "Event published successfully"}


@router.post("/{event_id}/cancel")
async def cancel_event(
    event_id: str,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check ownership
    if event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    event.status = EventStatus.CANCELLED.value
    await db.commit()
    
    return {"message": "Event cancelled successfully"}


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check ownership
    if event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(event)
    await db.commit()
    
    return {"message": "Event deleted successfully"}
