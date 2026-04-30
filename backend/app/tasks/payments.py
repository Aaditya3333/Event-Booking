from celery import Task
from app.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import logging
import asyncio

from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
import stripe

logger = logging.getLogger(__name__)


class PaymentTask(Task):
    """Base class for payment tasks with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Payment task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=PaymentTask, bind=True, max_retries=3)
def process_payment_webhook(self, webhook_data: dict):
    """Process Stripe payment webhook"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_webhook():
            async with AsyncSessionLocal() as db:
                event_type = webhook_data.get('type')
                event_data = webhook_data.get('data', {}).get('object', {})
                
                if event_type == 'payment_intent.succeeded':
                    await handle_payment_succeeded(event_data, db)
                elif event_type == 'payment_intent.payment_failed':
                    await handle_payment_failed(event_data, db)
                elif event_type == 'payment_intent.canceled':
                    await handle_payment_canceled(event_data, db)
                elif event_type == 'charge.dispute.created':
                    await handle_dispute_created(event_data, db)
                else:
                    logger.info(f"Unhandled webhook event type: {event_type}")
                
                return True
        
        # Run async function
        result = asyncio.run(process_webhook())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to process payment webhook: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def handle_payment_succeeded(payment_intent, db: AsyncSession):
    """Handle successful payment"""
    
    payment_id = payment_intent.get('id')
    metadata = payment_intent.get('metadata', {})
    booking_id = metadata.get('booking_id')
    
    if not booking_id:
        logger.error(f"No booking_id found in payment intent {payment_id}")
        return
    
    # Find payment record
    stmt = select(Payment).where(Payment.payment_id == payment_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        logger.error(f"Payment record not found for {payment_id}")
        return
    
    # Update payment status
    payment.status = PaymentStatus.COMPLETED.value
    payment.processed_at = datetime.utcnow()
    payment.stripe_charge_id = payment_intent.get('charges', {}).get('data', [{}])[0].get('id')
    payment.net_amount = payment_intent.get('amount', 0) / 100  # Convert from cents
    
    await db.commit()
    
    # Confirm booking
    from app.tasks.bookings import confirm_booking_after_payment
    confirm_booking_after_payment.delay(booking_id)
    
    logger.info(f"Payment {payment_id} succeeded, booking {booking_id} confirmed")


async def handle_payment_failed(payment_intent, db: AsyncSession):
    """Handle failed payment"""
    
    payment_id = payment_intent.get('id')
    metadata = payment_intent.get('metadata', {})
    booking_id = metadata.get('booking_id')
    
    if not booking_id:
        logger.error(f"No booking_id found in payment intent {payment_id}")
        return
    
    # Find payment record
    stmt = select(Payment).where(Payment.payment_id == payment_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        logger.error(f"Payment record not found for {payment_id}")
        return
    
    # Update payment status
    payment.status = PaymentStatus.FAILED.value
    payment.failed_at = datetime.utcnow()
    payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message')
    
    await db.commit()
    
    # Cancel booking
    from app.tasks.bookings import cancel_booking
    cancel_booking.delay(booking_id, "Payment failed")
    
    logger.info(f"Payment {payment_id} failed, booking {booking_id} cancelled")


async def handle_payment_canceled(payment_intent, db: AsyncSession):
    """Handle canceled payment"""
    
    payment_id = payment_intent.get('id')
    metadata = payment_intent.get('metadata', {})
    booking_id = metadata.get('booking_id')
    
    if not booking_id:
        logger.error(f"No booking_id found in payment intent {payment_id}")
        return
    
    # Find payment record
    stmt = select(Payment).where(Payment.payment_id == payment_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        logger.error(f"Payment record not found for {payment_id}")
        return
    
    # Update payment status
    payment.status = PaymentStatus.CANCELLED.value
    payment.processed_at = datetime.utcnow()
    
    await db.commit()
    
    # Cancel booking
    from app.tasks.bookings import cancel_booking
    cancel_booking.delay(booking_id, "Payment canceled")
    
    logger.info(f"Payment {payment_id} canceled, booking {booking_id} cancelled")


async def handle_dispute_created(charge, db: AsyncSession):
    """Handle payment dispute"""
    
    charge_id = charge.get('id')
    payment_intent_id = charge.get('payment_intent')
    
    # Find payment record
    stmt = select(Payment).where(Payment.stripe_charge_id == charge_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        logger.error(f"Payment record not found for charge {charge_id}")
        return
    
    # Log dispute for manual review
    logger.warning(f"Payment dispute created for payment {payment.payment_id}, charge {charge_id}")
    
    # TODO: Send notification to admin for manual review


@celery_app.task(base=PaymentTask, bind=True, max_retries=3)
def refund_payment(self, payment_id: str, amount: int = None, reason: str = "Customer requested"):
    """Process payment refund"""
    
    try:
        from app.config import settings
        
        # Initialize Stripe
        stripe.api_key = settings.stripe_secret_key
        
        # Create async session
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_refund():
            async with AsyncSessionLocal() as db:
                # Find payment record
                stmt = select(Payment).where(Payment.payment_id == payment_id)
                result = await db.execute(stmt)
                payment = result.scalar_one_or_none()
                
                if not payment:
                    logger.error(f"Payment record not found for {payment_id}")
                    return False
                
                if payment.status != PaymentStatus.COMPLETED.value:
                    logger.error(f"Cannot refund payment {payment_id} with status {payment.status}")
                    return False
                
                # Calculate refund amount
                refund_amount = amount or int(float(payment.amount) * 100)  # Convert to cents
                
                # Create refund in Stripe
                refund = stripe.Refund.create(
                    payment_intent=payment.stripe_intent_id,
                    amount=refund_amount,
                    reason=reason
                )
                
                # Create refund record
                from app.models.payment import PaymentRefund
                payment_refund = PaymentRefund(
                    payment_id=payment.id,
                    refund_id=refund.id,
                    amount=refund_amount / 100,  # Convert back to dollars
                    reason=reason,
                    status="succeeded",
                    processed_at=datetime.utcnow()
                )
                
                db.add(payment_refund)
                
                # Update payment status
                if refund_amount >= int(float(payment.amount) * 100):
                    payment.status = PaymentStatus.REFUNDED.value
                else:
                    payment.status = PaymentStatus.PARTIALLY_REFUNDED.value
                
                await db.commit()
                
                logger.info(f"Refund {refund.id} processed for payment {payment_id}")
                return True
        
        # Run async function
        result = asyncio.run(process_refund())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to refund payment {payment_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=PaymentTask, bind=True, max_retries=3)
def sync_payment_status(self, payment_id: str):
    """Sync payment status with Stripe"""
    
    try:
        from app.config import settings
        
        # Initialize Stripe
        stripe.api_key = settings.stripe_secret_key
        
        # Create async session
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_sync():
            async with AsyncSessionLocal() as db:
                # Find payment record
                stmt = select(Payment).where(Payment.payment_id == payment_id)
                result = await db.execute(stmt)
                payment = result.scalar_one_or_none()
                
                if not payment:
                    logger.error(f"Payment record not found for {payment_id}")
                    return False
                
                # Get payment intent from Stripe
                payment_intent = stripe.PaymentIntent.retrieve(payment.stripe_intent_id)
                
                # Update payment status based on Stripe
                stripe_status = payment_intent.get('status')
                
                status_mapping = {
                    'succeeded': PaymentStatus.COMPLETED.value,
                    'requires_payment_method': PaymentStatus.PENDING.value,
                    'requires_confirmation': PaymentStatus.PENDING.value,
                    'requires_action': PaymentStatus.PENDING.value,
                    'processing': PaymentStatus.PROCESSING.value,
                    'canceled': PaymentStatus.CANCELLED.value,
                }
                
                new_status = status_mapping.get(stripe_status, payment.status)
                
                if new_status != payment.status:
                    payment.status = new_status
                    
                    if new_status == PaymentStatus.COMPLETED.value:
                        payment.processed_at = datetime.utcnow()
                        # Confirm booking
                        from app.tasks.bookings import confirm_booking_after_payment
                        metadata = payment_intent.get('metadata', {})
                        booking_id = metadata.get('booking_id')
                        if booking_id:
                            confirm_booking_after_payment.delay(booking_id)
                    
                    await db.commit()
                    logger.info(f"Payment {payment_id} status synced to {new_status}")
                
                return True
        
        # Run async function
        result = asyncio.run(process_sync())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to sync payment status for {payment_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def cleanup_old_payments():
    """Clean up old payment records"""
    
    try:
        # Create async session
        from app.config import settings
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def process_cleanup():
            async with AsyncSessionLocal() as db:
                # Clean up very old failed payments (older than 90 days)
                cleanup_time = datetime.utcnow() - timedelta(days=90)
                
                stmt = select(Payment).where(
                    and_(
                        Payment.status.in_([PaymentStatus.FAILED.value, PaymentStatus.CANCELLED.value]),
                        Payment.created_at < cleanup_time
                    )
                )
                
                result = await db.execute(stmt)
                old_payments = result.scalars().all()
                
                for payment in old_payments:
                    await db.delete(payment)
                
                await db.commit()
                
                logger.info(f"Cleaned up {len(old_payments)} old failed payments")
                return len(old_payments)
        
        # Run async function
        result = asyncio.run(process_cleanup())
        return result
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old payments: {exc}")
