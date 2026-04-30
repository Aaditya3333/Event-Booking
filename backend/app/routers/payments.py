from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List
import uuid
import stripe
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.ticket import TicketTier
from app.schemas.payment import (
    PaymentCreate, PaymentIntentCreate, PaymentIntentResponse,
    PaymentResponse, PaymentRefundCreate, PaymentRefundResponse,
    PaymentListResponse, WebhookEvent
)
from app.schemas.booking import BookingCreate, BookingResponse
from app.auth.dependencies import get_current_user, get_current_active_user
from app.config import settings

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe payment intent"""
    
    try:
        booking_uuid = uuid.UUID(payment_data.booking_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format"
        )
    
    # Get booking
    stmt = select(Booking).options(
        selectinload(Booking.user),
        selectinload(Booking.event)
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
    
    # Check booking status
    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pay for booking with status: {booking.status}"
        )
    
    # Create or get Stripe customer
    customer_id = None
    if payment_data.save_payment_method or booking.user.stripe_customer_id:
        if booking.user.stripe_customer_id:
            customer_id = booking.user.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=booking.user.email,
                name=booking.user.full_name,
                metadata={"user_id": str(booking.user.id)}
            )
            customer_id = customer.id
            
            # Update user with Stripe customer ID
            booking.user.stripe_customer_id = customer_id
            await db.commit()
    
    # Calculate amount in cents
    amount_cents = int(float(booking.total_amount) * 100)
    
    # Create payment intent
    intent_metadata = {
        "booking_id": str(booking.id),
        "user_id": str(booking.user.id),
        "event_id": str(booking.event_id)
    }
    
    payment_intent_params = {
        "amount": amount_cents,
        "currency": booking.currency.lower(),
        "metadata": intent_metadata,
        "automatic_payment_methods": {"enabled": True}
    }
    
    if customer_id:
        payment_intent_params["customer"] = customer_id
    
    if payment_data.payment_method_id:
        payment_intent_params["payment_method"] = payment_data.payment_method_id
        payment_intent_params["confirm"] = True
        payment_intent_params["return_url"] = f"{settings.allowed_origins[0]}/booking/{booking.id}"
    
    try:
        payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    
    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        user_id=booking.user_id,
        payment_id=payment_intent.id,
        payment_method="stripe",
        status=PaymentStatus.PENDING.value,
        amount=booking.total_amount,
        currency=booking.currency,
        stripe_intent_id=payment_intent.id,
        stripe_customer_id=customer_id
    )
    
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    return PaymentIntentResponse(
        client_secret=payment_intent.client_secret,
        payment_intent_id=payment_intent.id,
        amount=booking.total_amount,
        currency=booking.currency
    )


@router.post("/confirm-payment", response_model=PaymentResponse)
async def confirm_payment(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm payment and update booking status"""
    
    try:
        # Get payment intent from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    
    # Find payment record
    stmt = select(Payment).where(Payment.payment_id == payment_intent_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found"
        )
    
    # Check ownership
    if payment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update payment status based on Stripe
    if payment_intent.status == "succeeded":
        payment.status = PaymentStatus.COMPLETED.value
        payment.processed_at = datetime.utcnow()
        payment.stripe_charge_id = payment_intent.charges.data[0].id if payment_intent.charges.data else None
        payment.net_amount = payment_intent.amount / 100  # Convert from cents
        
        await db.commit()
        
        # Trigger booking confirmation
        from app.tasks.bookings import confirm_booking_after_payment
        confirm_booking_after_payment.delay(str(payment.booking_id))
        
    elif payment_intent.status in ["requires_payment_method", "requires_confirmation", "requires_action"]:
        payment.status = PaymentStatus.PENDING.value
        await db.commit()
    
    elif payment_intent.status == "canceled":
        payment.status = PaymentStatus.CANCELLED.value
        payment.processed_at = datetime.utcnow()
        await db.commit()
        
        # Cancel booking
        from app.tasks.bookings import cancel_booking
        cancel_booking.delay(str(payment.booking_id), "Payment canceled")
    
    await db.refresh(payment)
    return payment


@router.get("/my-payments", response_model=PaymentListResponse)
async def get_my_payments(
    page: int = 1,
    size: int = 20,
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's payments"""
    
    query = select(Payment).where(Payment.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Payment.status == status_filter)
    
    query = query.order_by(Payment.created_at.desc())
    
    # Count total
    count_query = select(Payment.id).where(Payment.user_id == current_user.id)
    if status_filter:
        count_query = count_query.where(Payment.status == status_filter)
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    payments = result.scalars().all()
    
    pages = (total + size - 1) // size
    
    return PaymentListResponse(
        payments=payments,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment by ID"""
    
    try:
        payment_uuid = uuid.UUID(payment_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment ID format"
        )
    
    stmt = select(Payment).where(Payment.id == payment_uuid)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check ownership
    if payment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return payment


@router.post("/refund", response_model=PaymentRefundResponse)
async def create_refund(
    refund_data: PaymentRefundCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a refund"""
    
    try:
        payment_uuid = uuid.UUID(refund_data.payment_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment ID format"
        )
    
    # Find payment record
    stmt = select(Payment).where(Payment.id == payment_uuid)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check ownership
    if payment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check payment status
    if payment.status != PaymentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund completed payments"
        )
    
    # Process refund
    from app.tasks.payments import refund_payment
    refund_amount = int(float(refund_data.amount) * 100) if refund_data.amount else None
    
    try:
        # Create refund in Stripe
        refund_params = {
            "payment_intent": payment.stripe_intent_id,
            "reason": refund_data.reason
        }
        
        if refund_amount:
            refund_params["amount"] = refund_amount
        
        refund = stripe.Refund.create(**refund_params)
        
        # Create refund record
        from app.models.payment import PaymentRefund
        payment_refund = PaymentRefund(
            payment_id=payment.id,
            refund_id=refund.id,
            amount=refund_amount / 100 if refund_amount else float(payment.amount),
            reason=refund_data.reason,
            status="succeeded",
            processed_at=datetime.utcnow()
        )
        
        db.add(payment_refund)
        
        # Update payment status
        if not refund_amount or refund_amount >= int(float(payment.amount) * 100):
            payment.status = PaymentStatus.REFUNDED.value
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED.value
        
        await db.commit()
        await db.refresh(payment_refund)
        
        return payment_refund
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhooks"""
    
    body = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No signature provided"
        )
    
    try:
        event = stripe.Webhook.construct_event(
            body, signature, settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload: {str(e)}"
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid signature: {str(e)}"
        )
    
    # Process webhook event
    from app.tasks.payments import process_payment_webhook
    process_payment_webhook.delay(event)
    
    return {"status": "received"}
