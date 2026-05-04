import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@eventbooking.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
    
    async def send_booking_confirmation(
        self, 
        to_email: str, 
        event_title: str, 
        event_date: str, 
        event_time: str, 
        event_location: str,
        ticket_quantity: int,
        ticket_type: str,
        total_amount: float,
        booking_id: str
    ) -> bool:
        """Send booking confirmation email"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = f"Booking Confirmation - {event_title}"
            
            # HTML email body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 2rem;">🎉 Booking Confirmed!</h1>
                        <p style="margin: 10px 0 0 0; font-size: 1.1rem;">Your tickets have been successfully booked</p>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 30px; border-radius: 10px; margin: 20px 0;">
                        <h2 style="color: #1f2937; margin-bottom: 20px;">Event Details</h2>
                        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
                            <h3 style="color: #1f2937; margin: 0 0 15px 0;">{event_title}</h3>
                            <div style="display: grid; gap: 10px; font-size: 0.95rem;">
                                <div><strong>📅 Date:</strong> {event_date}</div>
                                <div><strong>🕐 Time:</strong> {event_time}</div>
                                <div><strong>📍 Location:</strong> {event_location}</div>
                                <div><strong>🎫 Tickets:</strong> {ticket_quantity} × {ticket_type}</div>
                                <div><strong>💰 Total Amount:</strong> ${total_amount}</div>
                                <div><strong>🆔 Booking ID:</strong> {booking_id}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #fef3c7; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #92400e; margin: 0 0 10px 0;">📧 Important Information</h3>
                        <ul style="color: #92400e; margin: 0; padding-left: 20px;">
                            <li>Please arrive 30 minutes before the event</li>
                            <li>Bring a valid ID for verification</li>
                            <li>Tickets are non-refundable</li>
                            <li>Check your profile for QR codes</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; display: inline-block; font-weight: bold;">
                            🎫 EventBooking System
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #6b7280; font-size: 0.85rem; margin-top: 20px;">
                        <p>This is an automated confirmation email. Please do not reply to this message.</p>
                        <p>For support, contact: support@eventbooking.com</p>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML body
            msg.attach(HTMLMIMEText(html_body, 'html'))
            
            # Send email (simulation for now)
            print(f"📧 Email prepared for: {to_email}")
            print(f"📧 Subject: {msg['Subject']}")
            print(f"📧 Event: {event_title}")
            print(f"📧 Booking ID: {booking_id}")
            print(f"📧 Total: ${total_amount}")
            print("📧 Email content ready for delivery")
            
            # In production, uncomment the actual SMTP sending:
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.sender_email, self.sender_password)
            # server.send_message(msg)
            # server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
