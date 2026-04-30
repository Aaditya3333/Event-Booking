from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List
import uuid
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.event import Event
from app.models.booking import Booking, BookingItem, BookingStatus
from app.models.ticket import TicketTier
from app.schemas.booking import (
    BookingCreate, BookingResponse, BookingListResponse,
    BookingSummary, BookingCancel
)
from app.auth.dependencies import get_current_user, get_current_active_user
from app.config import settings

router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking"""
    
    try:
        event_uuid = uuid.UUID(booking_data.event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    # Get event
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if event is published
    if event.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not available for booking"
        )
    
    # Check event date
    if event.start_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book events that have already started"
        )
    
    # Validate ticket tiers and calculate total
    booking_items = []
    total_amount = Decimal('0')
    
    for item_data in booking_data.items:
        try:
            tier_uuid = uuid.UUID(item_data.ticket_tier_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticket tier ID format"
            )
        
        # Get ticket tier
        tier_stmt = select(TicketTier).where(TicketTier.id == tier_uuid)
        tier_result = await db.execute(tier_stmt)
        ticket_tier = tier_result.scalar_one_or_none()
        
        if not ticket_tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ticket tier {item_data.ticket_tier_id} not found"
            )
        
        # Check if ticket tier belongs to the event
        if ticket_tier.event_id != event_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket tier does not belong to this event"
            )
        
        # Check availability
        if ticket_tier.available_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough tickets available for {ticket_tier.name}"
            )
        
        # Check quantity limits
        if item_data.quantity < ticket_tier.min_per_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum {ticket_tier.min_per_order} tickets required for {ticket_tier.name}"
            )
        
        if item_data.quantity > ticket_tier.max_per_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {ticket_tier.max_per_order} tickets allowed for {ticket_tier.name}"
            )
        
        # Check sale time
        now = datetime.utcnow()
        if ticket_tier.sale_start_time and now < ticket_tier.sale_start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tickets for {ticket_tier.name} are not yet on sale"
            )
        
        if ticket_tier.sale_end_time and now > ticket_tier.sale_end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tickets for {ticket_tier.name} are no longer on sale"
            )
        
        # Calculate item total
        item_total = ticket_tier.price * item_data.quantity
        total_amount += item_total
        
        booking_items.append({
            "ticket_tier_id": tier_uuid,
            "quantity": item_data.quantity,
            "unit_price": ticket_tier.price,
            "total_price": item_total
        })
    
    # Calculate service fee (10% of total)
    service_fee = total_amount * Decimal('0.1')
    total_with_fee = total_amount + service_fee
    
    # Generate booking number
    booking_number = f"BK-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        event_id=event_uuid,
        booking_number=booking_number,
        status=BookingStatus.PENDING.value,
        total_amount=total_with_fee,
        currency=event.currency,
        service_fee=service_fee,
        customer_name=booking_data.customer_name,
        customer_email=booking_data.customer_email,
        customer_phone=booking_data.customer_phone,
        notes=booking_data.notes,
        special_requests=booking_data.special_requests,
        expiry_time=datetime.utcnow() + timedelta(minutes=15)  # 15 minutes expiry
    )
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    # Create booking items
    for item_data in booking_items:
        booking_item = BookingItem(
            booking_id=booking.id,
            ticket_tier_id=item_data["ticket_tier_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"]
        )
        db.add(booking_item)
        
        # Update ticket tier availability
        tier_stmt = select(TicketTier).where(TicketTier.id == item_data["ticket_tier_id"])
        tier_result = await db.execute(tier_stmt)
        ticket_tier = tier_result.scalar_one()
        
        ticket_tier.available_quantity -= item_data["quantity"]
        ticket_tier.sold_quantity += item_data["quantity"]
    
    await db.commit()
    
    # Refresh booking with items
    stmt = select(Booking).options(
        selectinload(Booking.items)
    ).where(Booking.id == booking.id)
    result = await db.execute(stmt)
    booking = result.scalar_one()
    
    return booking


@router.get("/my-bookings", response_model=BookingListResponse)
async def get_my_bookings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's bookings"""
    
    query = select(Booking).where(Booking.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Booking.status == status_filter)
    
    query = query.order_by(Booking.created_at.desc())
    
    # Count total
    count_query = select(func.count(Booking.id)).where(Booking.user_id == current_user.id)
    if status_filter:
        count_query = count_query.where(Booking.status == status_filter)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    pages = (total + size - 1) // size
    
    return BookingListResponse(
        bookings=bookings,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get booking by ID"""
    
    try:
        booking_uuid = uuid.UUID(booking_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format"
        )
    
    stmt = select(Booking).options(
        selectinload(Booking.items)
    ).where(Booking.id == booking_uuid)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check ownership
    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return booking


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    cancel_data: BookingCancel,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a booking"""
    
    try:
        booking_uuid = uuid.UUID(booking_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format"
        )
    
    stmt = select(Booking).options(
        selectinload(Booking.items)
    ).where(Booking.id == booking_uuid)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check ownership
    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if booking can be cancelled
    if booking.status in [BookingStatus.CANCELLED.value, BookingStatus.REFUNDED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    if booking.status == BookingStatus.COMPLETED.value:
        # Check event start time
        stmt = select(Event).where(Event.id == booking.event_id)
        result = await db.execute(stmt)
        event = result.scalar_one()
        
        if event.start_time <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel bookings for events that have already started"
            )
    
    # Process cancellation
    from app.tasks.bookings import cancel_booking
    cancel_booking.delay(str(booking.id), cancel_data.reason)
    
    # If refund requested, process payment refund
    if cancel_data.refund_requested:
        from app.models.payment import Payment
        payment_stmt = select(Payment).where(
            and_(
                Payment.booking_id == booking.id,
                Payment.status == "completed"
            )
        )
        payment_result = await db.execute(payment_stmt)
        payment = payment_result.scalar_one_or_none()
        
        if payment:
            from app.tasks.payments import refund_payment
            refund_payment.delay(payment.payment_id, reason=cancel_data.reason)
    
    return {"message": "Booking cancellation processed"}


@router.get("/{booking_id}/summary", response_model=BookingSummary)
async def get_booking_summary(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get booking summary"""
    
    try:
        booking_uuid = uuid.UUID(booking_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format"
        )
    
    stmt = select(Booking).options(
        selectinload(Booking.event),
        selectinload(Booking.items)
    ).where(Booking.id == booking_uuid)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check ownership
    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    tickets_count = sum(item.quantity for item in booking.items)
    
    return BookingSummary(
        event_id=str(booking.event_id),
        event_title=booking.event.title,
        booking_number=booking.booking_number,
        total_amount=booking.total_amount,
        currency=booking.currency,
        status=booking.status,
        created_at=booking.created_at,
        tickets_count=tickets_count
    )
