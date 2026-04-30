from celery import Task
from app.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import logging
import asyncio

from app.models.booking import Booking, BookingStatus
from app.models.ticket import TicketTier
from app.database import get_db, Base

logger = logging.getLogger(__name__)


class BookingTask(Task):
    """Base class for booking tasks with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Booking task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=BookingTask, bind=True, max_retries=3)
def release_expired_holds(self):
    """Release expired ticket holds and update availability"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_expired_holds():
            async with AsyncSessionLocal() as db:
                # Find expired bookings (pending status older than 15 minutes)
                expiry_time = datetime.utcnow() - timedelta(minutes=15)
                
                stmt = select(Booking).where(
                    and_(
                        Booking.status == BookingStatus.PENDING.value,
                        Booking.created_at < expiry_time
                    )
                )
                
                result = await db.execute(stmt)
                expired_bookings = result.scalars().all()
                
                for booking in expired_bookings:
                    # Update booking status
                    booking.status = BookingStatus.EXPIRED.value
                    booking.expiry_time = datetime.utcnow()
                    
                    # Release ticket quantities
                    from app.models.booking import BookingItem
                    items_stmt = select(BookingItem).where(BookingItem.booking_id == booking.id)
                    items_result = await db.execute(items_stmt)
                    booking_items = items_result.scalars().all()
                    
                    for item in booking_items:
                        # Get ticket tier and update available quantity
                        tier_stmt = select(TicketTier).where(TicketTier.id == item.ticket_tier_id)
                        tier_result = await db.execute(tier_stmt)
                        ticket_tier = tier_result.scalar_one_or_none()
                        
                        if ticket_tier:
                            ticket_tier.available_quantity += item.quantity
                            ticket_tier.sold_quantity = max(0, ticket_tier.sold_quantity - item.quantity)
                
                await db.commit()
                
                logger.info(f"Released {len(expired_bookings)} expired booking holds")
                return len(expired_bookings)
        
        # Run async function
        result = asyncio.run(process_expired_holds())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to release expired holds: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=BookingTask, bind=True, max_retries=3)
def confirm_booking_after_payment(self, booking_id: str):
    """Confirm booking after successful payment"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_booking_confirmation():
            async with AsyncSessionLocal() as db:
                # Find booking
                stmt = select(Booking).where(Booking.id == booking_id)
                result = await db.execute(stmt)
                booking = result.scalar_one_or_none()
                
                if not booking:
                    logger.error(f"Booking {booking_id} not found")
                    return False
                
                if booking.status != BookingStatus.PENDING.value:
                    logger.warning(f"Booking {booking_id} is not in pending status")
                    return False
                
                # Update booking status
                booking.status = BookingStatus.CONFIRMED.value
                booking.confirmation_time = datetime.utcnow()
                
                # Generate tickets
                from app.models.ticket import Ticket
                from app.models.booking import BookingItem
                
                items_stmt = select(BookingItem).where(BookingItem.booking_id == booking.id)
                items_result = await db.execute(items_stmt)
                booking_items = items_result.scalars().all()
                
                for item in booking_items:
                    # Generate tickets for each quantity
                    for i in range(item.quantity):
                        ticket_number = f"TKT-{booking_id[:8].upper()}-{item.ticket_tier_id[:8].upper()}-{i+1:03d}"
                        
                        ticket = Ticket(
                            ticket_tier_id=item.ticket_tier_id,
                            booking_id=booking.id,
                            ticket_number=ticket_number,
                            holder_name=booking.customer_name,
                            holder_email=booking.customer_email,
                            holder_phone=booking.customer_phone,
                            expires_at=booking.event.start_time + timedelta(hours=24)  # Expire 24h after event
                        )
                        
                        db.add(ticket)
                
                await db.commit()
                
                # Trigger QR code generation
                from app.tasks.qr_codes import batch_generate_ticket_qr_codes
                ticket_data = [
                    {
                        "ticket_id": str(ticket.id),
                        "ticket_number": ticket.ticket_number,
                        "booking_id": str(booking.id)
                    }
                    for ticket in booking.tickets
                ]
                
                batch_generate_ticket_qr_codes.delay(ticket_data)
                
                # Send confirmation email
                from app.tasks.email import send_booking_confirmation
                send_booking_confirmation.delay(
                    user_email=booking.customer_email,
                    user_name=booking.customer_name,
                    booking_data={
                        "event_title": booking.event.title,
                        "event_date": booking.event.start_time.strftime("%B %d, %Y"),
                        "venue": booking.event.venue_name or "Virtual Event",
                        "booking_number": booking.booking_number,
                        "total_amount": float(booking.total_amount),
                        "currency": booking.currency
                    }
                )
                
                logger.info(f"Booking {booking_id} confirmed and tickets generated")
                return True
        
        # Run async function
        result = asyncio.run(process_booking_confirmation())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to confirm booking {booking_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=BookingTask, bind=True, max_retries=3)
def cancel_booking(self, booking_id: str, reason: str = "User requested"):
    """Cancel booking and release tickets"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_booking_cancellation():
            async with AsyncSessionLocal() as db:
                # Find booking
                stmt = select(Booking).where(Booking.id == booking_id)
                result = await db.execute(stmt)
                booking = result.scalar_one_or_none()
                
                if not booking:
                    logger.error(f"Booking {booking_id} not found")
                    return False
                
                if booking.status in [BookingStatus.CANCELLED.value, BookingStatus.REFUNDED.value]:
                    logger.warning(f"Booking {booking_id} is already cancelled")
                    return False
                
                # Update booking status
                booking.status = BookingStatus.CANCELLED.value
                booking.cancellation_time = datetime.utcnow()
                
                # Release ticket quantities
                from app.models.booking import BookingItem
                items_stmt = select(BookingItem).where(BookingItem.booking_id == booking.id)
                items_result = await db.execute(items_stmt)
                booking_items = items_result.scalars().all()
                
                for item in booking_items:
                    # Get ticket tier and update available quantity
                    tier_stmt = select(TicketTier).where(TicketTier.id == item.ticket_tier_id)
                    tier_result = await db.execute(tier_stmt)
                    ticket_tier = tier_result.scalar_one_or_none()
                    
                    if ticket_tier:
                        ticket_tier.available_quantity += item.quantity
                        ticket_tier.sold_quantity = max(0, ticket_tier.sold_quantity - item.quantity)
                
                # Invalidate tickets
                from app.models.ticket import Ticket
                tickets_stmt = select(Ticket).where(Ticket.booking_id == booking.id)
                tickets_result = await db.execute(tickets_stmt)
                tickets = tickets_result.scalars().all()
                
                for ticket in tickets:
                    ticket.is_valid = False
                
                await db.commit()
                
                logger.info(f"Booking {booking_id} cancelled: {reason}")
                return True
        
        # Run async function
        result = asyncio.run(process_booking_cancellation())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to cancel booking {booking_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def cleanup_old_sessions():
    """Clean up old booking sessions and temporary data"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_cleanup():
            async with AsyncSessionLocal() as db:
                # Clean up very old expired bookings (older than 30 days)
                cleanup_time = datetime.utcnow() - timedelta(days=30)
                
                stmt = select(Booking).where(
                    and_(
                        Booking.status == BookingStatus.EXPIRED.value,
                        Booking.created_at < cleanup_time
                    )
                )
                
                result = await db.execute(stmt)
                old_bookings = result.scalars().all()
                
                for booking in old_bookings:
                    await db.delete(booking)
                
                await db.commit()
                
                logger.info(f"Cleaned up {len(old_bookings)} old expired bookings")
                return len(old_bookings)
        
        # Run async function
        result = asyncio.run(process_cleanup())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old sessions: {exc}")


@celery_app.task(base=BookingTask, bind=True, max_retries=3)
def update_booking_analytics(self):
    """Update booking analytics and metrics"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_analytics():
            async with AsyncSessionLocal() as db:
                # Update event booking counts
                from app.models.event import Event
                
                events_stmt = select(Event)
                events_result = await db.execute(events_stmt)
                events = events_result.scalars().all()
                
                for event in events:
                    # Count confirmed bookings
                    booking_stmt = select(Booking).where(
                        and_(
                            Booking.event_id == event.id,
                            Booking.status == BookingStatus.CONFIRMED.value
                        )
                    )
                    booking_result = await db.execute(booking_stmt)
                    confirmed_bookings = booking_result.scalars().all()
                    
                    # Update booking count
                    event.booking_count = len(confirmed_bookings)
                    
                    # Calculate current capacity
                    total_tickets = 0
                    for booking in confirmed_bookings:
                        from app.models.booking import BookingItem
                        items_stmt = select(BookingItem).where(BookingItem.booking_id == booking.id)
                        items_result = await db.execute(items_stmt)
                        items = items_result.scalars().all()
                        total_tickets += sum(item.quantity for item in items)
                    
                    event.current_capacity = total_tickets
                
                await db.commit()
                
                logger.info("Booking analytics updated successfully")
                return True
        
        # Run async function
        result = asyncio.run(process_analytics())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to update booking analytics: {exc}")
        raise self.retry(exc=exc, countdown=60)
