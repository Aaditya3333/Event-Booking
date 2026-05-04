from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(enum.Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Payment Details
    payment_id = Column(String(100), unique=True, nullable=False, index=True)  # Stripe payment ID
    payment_method = Column(String(20), default=PaymentMethod.STRIPE.value)
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    
    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    fee_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2))
    
    # Stripe-specific
    stripe_intent_id = Column(String(100))
    stripe_charge_id = Column(String(100))
    stripe_customer_id = Column(String(100))
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    
    # Payment metadata
    payment_metadata = Column(JSON)  # Additional payment information
    failure_reason = Column(Text)
    
    # Relationships
    booking = relationship("Booking", back_populates="payments")
    user = relationship("User", back_populates="payments")
    refunds = relationship("PaymentRefund", back_populates="payment", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_amount_non_negative'),
        CheckConstraint('fee_amount >= 0', name='check_fee_amount_non_negative'),
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, payment_id={self.payment_id}, status={self.status})>"


class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    
    # Refund Details
    refund_id = Column(String(100), unique=True, nullable=False, index=True)  # Stripe refund ID
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default="pending")
    
    # Reason
    reason = Column(String(100))
    reason_description = Column(Text)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Refund metadata
    refund_metadata = Column(JSON)
    
    # Relationships
    payment = relationship("Payment", back_populates="refunds")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_refund_amount_positive'),
    )
    
    def __repr__(self):
        return f"<PaymentRefund(id={self.id}, refund_id={self.refund_id}, amount={self.amount})>"
