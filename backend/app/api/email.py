from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.email import email_service
import time

router = APIRouter()

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    from_name: Optional[str] = "EventBooking System"

class BookingEmailRequest(BaseModel):
    to_email: str
    event_title: str
    event_date: str
    event_time: str
    event_location: str
    ticket_quantity: int
    ticket_type: str
    total_amount: float
    booking_id: Optional[str] = None

@router.post("/send")
async def send_email(email_request: EmailRequest):
    """Send a generic email"""
    try:
        # For now, just log the email details
        print(f"📧 Email Request:")
        print(f"   To: {email_request.to_email}")
        print(f"   Subject: {email_request.subject}")
        print(f"   From: {email_request.from_name}")
        print(f"   Body Length: {len(email_request.body)} characters")
        
        return {
            "success": True,
            "message": "Email logged successfully",
            "to_email": email_request.to_email,
            "subject": email_request.subject
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/booking-confirmation")
async def send_booking_confirmation(booking_request: BookingEmailRequest):
    """Send booking confirmation email"""
    try:
        # Generate booking ID if not provided
        booking_id = booking_request.booking_id or f"BK{int(time.time())}"
        
        # Send booking confirmation email
        success = await email_service.send_booking_confirmation(
            to_email=booking_request.to_email,
            event_title=booking_request.event_title,
            event_date=booking_request.event_date,
            event_time=booking_request.event_time,
            event_location=booking_request.event_location,
            ticket_quantity=booking_request.ticket_quantity,
            ticket_type=booking_request.ticket_type,
            total_amount=booking_request.total_amount,
            booking_id=booking_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Booking confirmation email sent successfully",
                "booking_id": booking_id,
                "to_email": booking_request.to_email
            }
        else:
            return {
                "success": False,
                "message": "Failed to send booking confirmation email",
                "booking_id": booking_id,
                "to_email": booking_request.to_email
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
