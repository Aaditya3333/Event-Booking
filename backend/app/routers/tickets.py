from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.event import Event
from app.models.ticket import TicketTier, Ticket
from app.models.booking import Booking
from app.schemas.ticket import (
    TicketTierCreate, TicketTierUpdate, TicketTierResponse,
    TicketResponse, TicketCheckIn, TicketCheckInResponse,
    TicketValidationResponse, TicketAvailability
)
from app.auth.dependencies import get_current_user, get_organizer_user

router = APIRouter()


@router.post("/tiers", response_model=TicketTierResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_tier(
    tier_data: TicketTierCreate,
    event_id: str,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new ticket tier for an event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    # Check if event exists and user has permission
    stmt = select(Event).where(Event.id == event_uuid)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create ticket tier
    ticket_tier = TicketTier(
        event_id=event_uuid,
        name=tier_data.name,
        description=tier_data.description,
        ticket_type=tier_data.ticket_type,
        price=tier_data.price,
        currency=tier_data.currency,
        total_quantity=tier_data.total_quantity,
        available_quantity=tier_data.available_quantity,
        min_per_order=tier_data.min_per_order,
        max_per_order=tier_data.max_per_order,
        sale_start_time=tier_data.sale_start_time,
        sale_end_time=tier_data.sale_end_time,
        status=tier_data.status,
        is_hidden=tier_data.is_hidden,
        features=tier_data.features,
        restrictions=tier_data.restrictions,
    )
    
    db.add(ticket_tier)
    await db.commit()
    await db.refresh(ticket_tier)
    
    return ticket_tier


@router.get("/tiers", response_model=List[TicketTierResponse])
async def list_ticket_tiers(
    event_id: str,
    include_hidden: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List ticket tiers for an event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    query = select(TicketTier).where(TicketTier.event_id == event_uuid)
    
    if not include_hidden:
        query = query.where(TicketTier.is_hidden == False)
    
    query = query.order_by(TicketTier.sort_order.asc(), TicketTier.created_at.asc())
    
    result = await db.execute(query)
    ticket_tiers = result.scalars().all()
    
    return ticket_tiers


@router.get("/tiers/{tier_id}", response_model=TicketTierResponse)
async def get_ticket_tier(
    tier_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get ticket tier by ID"""
    
    try:
        tier_uuid = uuid.UUID(tier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket tier ID format"
        )
    
    stmt = select(TicketTier).where(TicketTier.id == tier_uuid)
    result = await db.execute(stmt)
    ticket_tier = result.scalar_one_or_none()
    
    if not ticket_tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket tier not found"
        )
    
    return ticket_tier


@router.put("/tiers/{tier_id}", response_model=TicketTierResponse)
async def update_ticket_tier(
    tier_id: str,
    tier_data: TicketTierUpdate,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update ticket tier"""
    
    try:
        tier_uuid = uuid.UUID(tier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket tier ID format"
        )
    
    stmt = select(TicketTier).options(selectinload(TicketTier.event)).where(TicketTier.id == tier_uuid)
    result = await db.execute(stmt)
    ticket_tier = result.scalar_one_or_none()
    
    if not ticket_tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket tier not found"
        )
    
    # Check ownership
    if ticket_tier.event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = tier_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket_tier, field, value)
    
    await db.commit()
    await db.refresh(ticket_tier)
    
    return ticket_tier


@router.delete("/tiers/{tier_id}")
async def delete_ticket_tier(
    tier_id: str,
    current_user: User = Depends(get_organizer_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete ticket tier"""
    
    try:
        tier_uuid = uuid.UUID(tier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket tier ID format"
        )
    
    stmt = select(TicketTier).options(selectinload(TicketTier.event)).where(TicketTier.id == tier_uuid)
    result = await db.execute(stmt)
    ticket_tier = result.scalar_one_or_none()
    
    if not ticket_tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket tier not found"
        )
    
    # Check ownership
    if ticket_tier.event.organizer_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if tickets have been sold
    if ticket_tier.sold_quantity > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete ticket tier with sold tickets"
        )
    
    await db.delete(ticket_tier)
    await db.commit()
    
    return {"message": "Ticket tier deleted successfully"}


@router.get("/my-tickets", response_model=List[TicketResponse])
async def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's tickets"""
    
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.ticket_tier))
        .join(Booking)
        .where(
            Booking.user_id == current_user.id,
            Booking.status == "confirmed"
        )
        .order_by(Ticket.created_at.desc())
    )
    
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ticket by ID"""
    
    try:
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket ID format"
        )
    
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.ticket_tier),
            selectinload(Ticket.booking)
        )
        .where(Ticket.id == ticket_uuid)
    )
    
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check ownership
    if ticket.booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ticket


@router.post("/validate/{ticket_number}", response_model=TicketValidationResponse)
async def validate_ticket(
    ticket_number: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate ticket for check-in"""
    
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.ticket_tier),
            selectinload(Ticket.booking)
        )
        .where(Ticket.ticket_number == ticket_number)
    )
    
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        return TicketValidationResponse(
            is_valid=False,
            error_message="Ticket not found"
        )
    
    # Check if ticket is valid
    if not ticket.is_valid:
        return TicketValidationResponse(
            is_valid=False,
            error_message="Ticket is invalid"
        )
    
    if ticket.is_used:
        return TicketValidationResponse(
            is_valid=False,
            error_message="Ticket already used"
        )
    
    # Check event date
    if ticket.ticket_tier.event.start_time > datetime.utcnow():
        return TicketValidationResponse(
            is_valid=False,
            error_message="Event has not started yet"
        )
    
    return TicketValidationResponse(
        is_valid=True,
        ticket=ticket
    )


@router.post("/checkin", response_model=TicketCheckInResponse)
async def check_in_ticket(
    check_in_data: TicketCheckIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check in ticket"""
    
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.ticket_tier),
            selectinload(Ticket.booking)
        )
        .where(Ticket.ticket_number == check_in_data.ticket_number)
    )
    
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        return TicketCheckInResponse(
            success=False,
            message="Ticket not found"
        )
    
    if ticket.is_used:
        return TicketCheckInResponse(
            success=False,
            message="Ticket already checked in",
            ticket=ticket
        )
    
    if not ticket.is_valid:
        return TicketCheckInResponse(
            success=False,
            message="Ticket is invalid",
            ticket=ticket
        )
    
    # Check in ticket
    ticket.is_used = True
    ticket.checked_in_at = datetime.utcnow()
    ticket.checked_in_by = current_user.id
    
    # Create check-in record
    from app.models.checkin import CheckIn, CheckInStatus
    
    check_in = CheckIn(
        ticket_id=ticket.id,
        checked_in_by=current_user.id,
        status=CheckInStatus.SUCCESSFUL.value,
        check_in_location=check_in_data.check_in_location,
        device_id=check_in_data.device_id,
        notes=check_in_data.notes,
    )
    
    db.add(check_in)
    await db.commit()
    await db.refresh(ticket)
    
    return TicketCheckInResponse(
        success=True,
        message="Ticket checked in successfully",
        ticket=ticket
    )


@router.get("/availability/{event_id}", response_model=List[TicketAvailability])
async def get_ticket_availability(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get ticket availability for an event"""
    
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    stmt = select(TicketTier).where(TicketTier.event_id == event_uuid)
    result = await db.execute(stmt)
    ticket_tiers = result.scalars().all()
    
    availability = []
    for tier in ticket_tiers:
        is_available = (
            tier.status == "available" and
            tier.available_quantity > 0 and
            tier.total_quantity > tier.sold_quantity
        )
        
        availability.append(TicketAvailability(
            ticket_tier_id=str(tier.id),
            available_quantity=tier.available_quantity,
            total_quantity=tier.total_quantity,
            sold_quantity=tier.sold_quantity,
            is_available=is_available,
            sale_status=tier.status
        ))
    
    return availability
