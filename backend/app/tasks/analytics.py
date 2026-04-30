from celery import Task
from app.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
import logging
import asyncio

from app.models.event import Event
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User

logger = logging.getLogger(__name__)


class AnalyticsTask(Task):
    """Base class for analytics tasks with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Analytics task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=AnalyticsTask, bind=True, max_retries=3)
def update_analytics(self):
    """Update analytics data for all events"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_analytics():
            async with AsyncSessionLocal() as db:
                # Update event statistics
                events_stmt = select(Event)
                events_result = await db.execute(events_stmt)
                events = events_result.scalars().all()
                
                for event in events:
                    await update_event_analytics(event.id, db)
                
                await db.commit()
                
                logger.info("Analytics updated for all events")
                return True
        
        # Run async function
        result = asyncio.run(process_analytics())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to update analytics: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=AnalyticsTask, bind=True, max_retries=3)
def update_event_analytics_task(self, event_id: str):
    """Update analytics for a specific event"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_event_analytics():
            async with AsyncSessionLocal() as db:
                result = await update_event_analytics(event_id, db)
                await db.commit()
                return result
        
        # Run async function
        result = asyncio.run(process_event_analytics())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to update analytics for event {event_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def update_event_analytics(event_id: str, db: AsyncSession):
    """Update analytics data for a specific event"""
    
    # Count confirmed bookings
    booking_stmt = select(func.count(Booking.id)).where(
        and_(
            Booking.event_id == event_id,
            Booking.status == BookingStatus.CONFIRMED.value
        )
    )
    booking_result = await db.execute(booking_stmt)
    confirmed_bookings_count = booking_result.scalar() or 0
    
    # Calculate total revenue
    revenue_stmt = select(func.sum(Payment.amount)).join(Booking).where(
        and_(
            Booking.event_id == event_id,
            Booking.status == BookingStatus.CONFIRMED.value,
            Payment.status == PaymentStatus.COMPLETED.value
        )
    )
    revenue_result = await db.execute(revenue_stmt)
    total_revenue = revenue_result.scalar() or 0
    
    # Calculate current capacity
    from app.models.booking import BookingItem
    capacity_stmt = select(func.sum(BookingItem.quantity)).join(Booking).where(
        and_(
            Booking.event_id == event_id,
            Booking.status == BookingStatus.CONFIRMED.value
        )
    )
    capacity_result = await db.execute(capacity_stmt)
    current_capacity = capacity_result.scalar() or 0
    
    # Update event
    event_stmt = select(Event).where(Event.id == event_id)
    event_result = await db.execute(event_stmt)
    event = event_result.scalar_one_or_none()
    
    if event:
        event.booking_count = confirmed_bookings_count
        event.current_capacity = current_capacity
        
        # Update min/max prices based on actual sales
        if total_revenue > 0 and current_capacity > 0:
            avg_price = total_revenue / current_capacity
            if event.min_price is None or avg_price < float(event.min_price):
                event.min_price = avg_price
            if event.max_price is None or avg_price > float(event.max_price):
                event.max_price = avg_price
    
    logger.info(f"Updated analytics for event {event_id}: {confirmed_bookings_count} bookings, {total_revenue} revenue")
    return True


@celery_app.task(base=AnalyticsTask, bind=True, max_retries=3)
def generate_daily_report(self):
    """Generate daily analytics report"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def generate_report():
            async with AsyncSessionLocal() as db:
                today = datetime.utcnow().date()
                start_of_day = datetime.combine(today, datetime.min.time())
                end_of_day = datetime.combine(today, datetime.max.time())
                
                # Today's statistics
                new_bookings_stmt = select(func.count(Booking.id)).where(
                    and_(
                        Booking.created_at >= start_of_day,
                        Booking.created_at <= end_of_day
                    )
                )
                new_bookings_result = await db.execute(new_bookings_stmt)
                new_bookings = new_bookings_result.scalar() or 0
                
                confirmed_bookings_stmt = select(func.count(Booking.id)).where(
                    and_(
                        Booking.status == BookingStatus.CONFIRMED.value,
                        Booking.confirmation_time >= start_of_day,
                        Booking.confirmation_time <= end_of_day
                    )
                )
                confirmed_bookings_result = await db.execute(confirmed_bookings_stmt)
                confirmed_bookings = confirmed_bookings_result.scalar() or 0
                
                # Today's revenue
                revenue_stmt = select(func.sum(Payment.amount)).where(
                    and_(
                        Payment.status == PaymentStatus.COMPLETED.value,
                        Payment.processed_at >= start_of_day,
                        Payment.processed_at <= end_of_day
                    )
                )
                revenue_result = await db.execute(revenue_stmt)
                daily_revenue = revenue_result.scalar() or 0
                
                # New users
                new_users_stmt = select(func.count(User.id)).where(
                    and_(
                        User.created_at >= start_of_day,
                        User.created_at <= end_of_day
                    )
                )
                new_users_result = await db.execute(new_users_stmt)
                new_users = new_users_result.scalar() or 0
                
                # Total statistics
                total_users_stmt = select(func.count(User.id)).where(User.is_active == True)
                total_users_result = await db.execute(total_users_stmt)
                total_users = total_users_result.scalar() or 0
                
                total_events_stmt = select(func.count(Event.id)).where(Event.status == "published")
                total_events_result = await db.execute(total_events_stmt)
                total_events = total_events_result.scalar() or 0
                
                total_bookings_stmt = select(func.count(Booking.id)).where(
                    Booking.status == BookingStatus.CONFIRMED.value
                )
                total_bookings_result = await db.execute(total_bookings_stmt)
                total_bookings = total_bookings_result.scalar() or 0
                
                total_revenue_stmt = select(func.sum(Payment.amount)).where(
                    Payment.status == PaymentStatus.COMPLETED.value
                )
                total_revenue_result = await db.execute(total_revenue_stmt)
                total_revenue = total_revenue_result.scalar() or 0
                
                report = {
                    "date": today.isoformat(),
                    "daily": {
                        "new_bookings": new_bookings,
                        "confirmed_bookings": confirmed_bookings,
                        "revenue": float(daily_revenue),
                        "new_users": new_users
                    },
                    "totals": {
                        "total_users": total_users,
                        "total_events": total_events,
                        "total_bookings": total_bookings,
                        "total_revenue": float(total_revenue)
                    }
                }
                
                logger.info(f"Daily report generated: {report}")
                return report
        
        # Run async function
        result = asyncio.run(generate_report())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to generate daily report: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=AnalyticsTask, bind=True, max_retries=3)
def generate_monthly_report(self):
    """Generate monthly analytics report"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def generate_report():
            async with AsyncSessionLocal() as db:
                now = datetime.utcnow()
                start_of_month = datetime(now.year, now.month, 1)
                
                # Monthly statistics
                monthly_bookings_stmt = select(func.count(Booking.id)).where(
                    Booking.created_at >= start_of_month
                )
                monthly_bookings_result = await db.execute(monthly_bookings_stmt)
                monthly_bookings = monthly_bookings_result.scalar() or 0
                
                monthly_revenue_stmt = select(func.sum(Payment.amount)).where(
                    and_(
                        Payment.status == PaymentStatus.COMPLETED.value,
                        Payment.processed_at >= start_of_month
                    )
                )
                monthly_revenue_result = await db.execute(monthly_revenue_stmt)
                monthly_revenue = monthly_revenue_result.scalar() or 0
                
                monthly_users_stmt = select(func.count(User.id)).where(
                    User.created_at >= start_of_month
                )
                monthly_users_result = await db.execute(monthly_users_stmt)
                monthly_users = monthly_users_result.scalar() or 0
                
                # Monthly events
                monthly_events_stmt = select(func.count(Event.id)).where(
                    and_(
                        Event.created_at >= start_of_month,
                        Event.status == "published"
                    )
                )
                monthly_events_result = await db.execute(monthly_events_stmt)
                monthly_events = monthly_events_result.scalar() or 0
                
                # Top events by revenue
                top_events_stmt = (
                    select(
                        Event.title,
                        func.sum(Payment.amount).label('revenue'),
                        func.count(Booking.id).label('bookings')
                    )
                    .join(Booking, Event.id == Booking.event_id)
                    .join(Payment, Booking.id == Payment.booking_id)
                    .where(
                        and_(
                            Payment.status == PaymentStatus.COMPLETED.value,
                            Payment.processed_at >= start_of_month
                        )
                    )
                    .group_by(Event.id, Event.title)
                    .order_by(func.sum(Payment.amount).desc())
                    .limit(10)
                )
                top_events_result = await db.execute(top_events_stmt)
                top_events = [
                    {
                        "title": row.title,
                        "revenue": float(row.revenue),
                        "bookings": row.bookings
                    }
                    for row in top_events_result
                ]
                
                report = {
                    "month": now.strftime("%Y-%m"),
                    "monthly": {
                        "new_bookings": monthly_bookings,
                        "revenue": float(monthly_revenue),
                        "new_users": monthly_users,
                        "new_events": monthly_events
                    },
                    "top_events": top_events
                }
                
                logger.info(f"Monthly report generated: {report}")
                return report
        
        # Run async function
        result = asyncio.run(generate_report())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to generate monthly report: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def export_analytics_data():
    """Export analytics data for external analysis"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def export_data():
            async with AsyncSessionLocal() as db:
                # Export events data
                events_stmt = select(Event).where(Event.status == "published")
                events_result = await db.execute(events_stmt)
                events = events_result.scalars().all()
                
                events_data = []
                for event in events:
                    events_data.append({
                        "id": str(event.id),
                        "title": event.title,
                        "event_type": event.event_type,
                        "city": event.city,
                        "country": event.country,
                        "start_time": event.start_time.isoformat(),
                        "max_capacity": event.max_capacity,
                        "current_capacity": event.current_capacity,
                        "booking_count": event.booking_count,
                        "view_count": event.view_count,
                        "created_at": event.created_at.isoformat()
                    })
                
                # Export bookings data
                bookings_stmt = select(Booking).where(Booking.status == BookingStatus.CONFIRMED.value)
                bookings_result = await db.execute(bookings_stmt)
                bookings = bookings_result.scalars().all()
                
                bookings_data = []
                for booking in bookings:
                    bookings_data.append({
                        "id": str(booking.id),
                        "event_id": str(booking.event_id),
                        "user_id": str(booking.user_id),
                        "booking_number": booking.booking_number,
                        "total_amount": float(booking.total_amount),
                        "currency": booking.currency,
                        "booking_time": booking.booking_time.isoformat(),
                        "confirmation_time": booking.confirmation_time.isoformat() if booking.confirmation_time else None
                    })
                
                export_data = {
                    "events": events_data,
                    "bookings": bookings_data,
                    "exported_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Analytics data exported: {len(events_data)} events, {len(bookings_data)} bookings")
                return export_data
        
        # Run async function
        result = asyncio.run(export_data())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to export analytics data: {exc}")
