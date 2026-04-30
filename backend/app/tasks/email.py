from celery import Task
from app.celery_app import celery_app
from app.config import settings
import aiosmtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)


class EmailTask(Task):
    """Base class for email tasks with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Email task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=EmailTask, bind=True, max_retries=3)
def send_welcome_email(self, user_email: str, user_name: str):
    """Send welcome email to new user"""
    
    try:
        subject = "Welcome to Event Booking System"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Event Booking System</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2c3e50;">Welcome to Event Booking System!</h1>
                <p>Hi {{ name }},</p>
                <p>Thank you for joining Event Booking System! We're excited to have you on board.</p>
                <p>With our platform, you can:</p>
                <ul>
                    <li>Discover amazing events in your area</li>
                    <li>Book tickets securely and easily</li>
                    <li>Create and manage your own events</li>
                    <li>Get QR code tickets for easy check-in</li>
                </ul>
                <p>Get started by <a href="{{ frontend_url }}/events" style="color: #3498db;">browsing events</a>!</p>
                <p>If you have any questions, feel free to contact our support team.</p>
                <p>Best regards,<br>The Event Booking Team</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            name=user_name,
            frontend_url="http://localhost:3000"
        )
        
        send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"Welcome email sent to {user_email}")
        
    except Exception as exc:
        logger.error(f"Failed to send welcome email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=EmailTask, bind=True, max_retries=3)
def send_booking_confirmation(self, user_email: str, user_name: str, booking_data: dict):
    """Send booking confirmation email"""
    
    try:
        subject = f"Booking Confirmation - {booking_data['event_title']}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Booking Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2c3e50;">Booking Confirmation!</h1>
                <p>Hi {{ name }},</p>
                <p>Your booking has been confirmed! Here are your details:</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>{{ event_title }}</h3>
                    <p><strong>Date:</strong> {{ event_date }}</p>
                    <p><strong>Venue:</strong> {{ venue }}</p>
                    <p><strong>Booking Number:</strong> {{ booking_number }}</p>
                    <p><strong>Total Amount:</strong> {{ total_amount }} {{ currency }}</p>
                </div>
                
                <p>Your tickets will be available in your account. You can also download them from your booking page.</p>
                <p>Have a great time at the event!</p>
                <p>Best regards,<br>The Event Booking Team</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            name=user_name,
            event_title=booking_data['event_title'],
            event_date=booking_data['event_date'],
            venue=booking_data['venue'],
            booking_number=booking_data['booking_number'],
            total_amount=booking_data['total_amount'],
            currency=booking_data['currency']
        )
        
        send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"Booking confirmation sent to {user_email}")
        
    except Exception as exc:
        logger.error(f"Failed to send booking confirmation to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=EmailTask, bind=True, max_retries=3)
def send_event_reminder(self, user_email: str, user_name: str, event_data: dict):
    """Send event reminder email"""
    
    try:
        subject = f"Event Reminder: {event_data['title']} is tomorrow!"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Event Reminder</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #e74c3c;">Event Reminder!</h1>
                <p>Hi {{ name }},</p>
                <p>Just a friendly reminder that you have an event tomorrow:</p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <h3>{{ event_title }}</h3>
                    <p><strong>Date:</strong> {{ event_date }}</p>
                    <p><strong>Time:</strong> {{ event_time }}</p>
                    <p><strong>Venue:</strong> {{ venue }}</p>
                    {% if is_virtual %}
                    <p><strong>Virtual Event:</strong> <a href="{{ virtual_url }}">Join Here</a></p>
                    {% endif %}
                </div>
                
                <p>Don't forget to bring your tickets! You can access them from your account.</p>
                <p>We hope you have a wonderful time!</p>
                <p>Best regards,<br>The Event Booking Team</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            name=user_name,
            event_title=event_data['title'],
            event_date=event_data['date'],
            event_time=event_data['time'],
            venue=event_data['venue'],
            is_virtual=event_data.get('is_virtual', False),
            virtual_url=event_data.get('virtual_url')
        )
        
        send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"Event reminder sent to {user_email}")
        
    except Exception as exc:
        logger.error(f"Failed to send event reminder to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=EmailTask, bind=True, max_retries=3)
def send_event_reminders(self):
    """Send event reminders for events happening in 24 hours"""
    # This would be implemented to query the database for events
    # happening in 24 hours and send reminders to all attendees
    pass


@celery_app.task(base=EmailTask, bind=True, max_retries=3)
def send_password_reset(self, user_email: str, reset_token: str):
    """Send password reset email"""
    
    try:
        subject = "Password Reset - Event Booking System"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #e74c3c;">Password Reset</h1>
                <p>You requested a password reset for your Event Booking System account.</p>
                <p>Click the link below to reset your password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ frontend_url }}/reset-password?token={{ reset_token }}" 
                       style="background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <p>Best regards,<br>The Event Booking Team</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            reset_token=reset_token,
            frontend_url="http://localhost:3000"
        )
        
        send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"Password reset email sent to {user_email}")
        
    except Exception as exc:
        logger.error(f"Failed to send password reset email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = to_email
    
    # Add HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    # Send email
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_username,
        password=settings.smtp_password,
    )
