from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    booking_id: str = Field(..., description="ID of the booking")
    payment_method: str = Field(default=PaymentMethod.STRIPE.value)
    amount: Optional[Decimal] = None  # Will be calculated from booking if not provided


class PaymentIntentCreate(BaseModel):
    booking_id: str = Field(..., description="ID of the booking")
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")
    save_payment_method: bool = Field(default=False, description="Save payment method for future use")


class PaymentIntentResponse(BaseModel):
    client_secret: str = Field(..., description="Stripe client secret for payment confirmation")
    payment_intent_id: str = Field(..., description="Stripe payment intent ID")
    amount: Decimal = Field(..., description="Payment amount in cents")
    currency: str = Field(..., description="Payment currency")


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    booking_id: str
    user_id: str
    payment_id: str
    payment_method: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    fee_amount: Decimal
    net_amount: Optional[Decimal] = None
    stripe_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


class PaymentRefundCreate(BaseModel):
    payment_id: str = Field(..., description="ID of the payment")
    amount: Optional[Decimal] = Field(None, description="Refund amount (full refund if not provided)")
    reason: str = Field(default="Customer requested", description="Reason for refund")


class PaymentRefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    payment_id: str
    refund_id: str
    amount: Decimal
    currency: str
    status: str
    reason: Optional[str] = None
    reason_description: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None


class PaymentMethodCreate(BaseModel):
    type: str = Field(..., description="Payment method type (card, sepa_debit, etc.)")
    card: Optional[dict] = Field(None, description="Card details for card payments")
    sepa_debit: Optional[dict] = Field(None, description="SEPA debit details")
    billing_details: Optional[dict] = Field(None, description="Billing details")


class PaymentMethodResponse(BaseModel):
    id: str
    type: str
    card: Optional[dict] = None
    sepa_debit: Optional[dict] = None
    billing_details: Optional[dict] = None
    created_at: datetime


class PaymentListResponse(BaseModel):
    payments: List[PaymentResponse]
    total: int
    page: int
    size: int
    pages: int


class PaymentSummary(BaseModel):
    total_payments: int
    total_amount: Decimal
    successful_payments: int
    failed_payments: int
    refunded_amount: Decimal
    pending_amount: Decimal


class WebhookEvent(BaseModel):
    id: str
    object: str = "event"
    api_version: str
    created: int
    data: dict
    livemode: bool
    pending_webhooks: int
    request: Optional[str] = None
    type: str
