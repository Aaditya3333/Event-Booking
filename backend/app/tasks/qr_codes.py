from celery import Task
from app.celery_app import celery_app
from app.config import settings
import segno
import os
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class QRCodeTask(Task):
    """Base class for QR code tasks with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"QR code task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=QRCodeTask, bind=True, max_retries=3)
def generate_ticket_qr_code(self, ticket_id: str, ticket_number: str, booking_id: str):
    """Generate QR code for a ticket"""
    
    try:
        # Create QR code data
        qr_data = {
            "ticket_id": ticket_id,
            "ticket_number": ticket_number,
            "booking_id": booking_id,
            "type": "ticket"
        }
        
        # Convert to JSON string
        import json
        qr_string = json.dumps(qr_data)
        
        # Generate QR code
        qr = segno.make(qr_string, error='H')
        
        # Create directory if it doesn't exist
        qr_dir = Path(settings.upload_dir) / "qr_codes"
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Save QR code
        qr_filename = f"{ticket_id}.png"
        qr_path = qr_dir / qr_filename
        
        # Save with higher resolution for better scanning
        qr.save(qr_path, scale=10)
        
        # Generate public URL
        qr_url = f"{settings.upload_dir}/qr_codes/{qr_filename}"
        
        logger.info(f"QR code generated for ticket {ticket_number}")
        
        return qr_url
        
    except Exception as exc:
        logger.error(f"Failed to generate QR code for ticket {ticket_number}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=QRCodeTask, bind=True, max_retries=3)
def generate_event_qr_code(self, event_id: str, event_title: str):
    """Generate QR code for event check-in"""
    
    try:
        # Create QR code data
        qr_data = {
            "event_id": event_id,
            "event_title": event_title,
            "type": "event_checkin"
        }
        
        # Convert to JSON string
        import json
        qr_string = json.dumps(qr_data)
        
        # Generate QR code
        qr = segno.make(qr_string, error='H')
        
        # Create directory if it doesn't exist
        qr_dir = Path(settings.upload_dir) / "event_qr_codes"
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Save QR code
        qr_filename = f"event_{event_id}.png"
        qr_path = qr_dir / qr_filename
        
        # Save with higher resolution for better scanning
        qr.save(qr_path, scale=10)
        
        # Generate public URL
        qr_url = f"{settings.upload_dir}/event_qr_codes/{qr_filename}"
        
        logger.info(f"QR code generated for event {event_title}")
        
        return qr_url
        
    except Exception as exc:
        logger.error(f"Failed to generate QR code for event {event_title}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=QRCodeTask, bind=True, max_retries=3)
def batch_generate_ticket_qr_codes(self, ticket_data_list):
    """Generate QR codes for multiple tickets in batch"""
    
    results = []
    
    for ticket_data in ticket_data_list:
        try:
            ticket_id = ticket_data['ticket_id']
            ticket_number = ticket_data['ticket_number']
            booking_id = ticket_data['booking_id']
            
            # Create QR code data
            qr_data = {
                "ticket_id": ticket_id,
                "ticket_number": ticket_number,
                "booking_id": booking_id,
                "type": "ticket"
            }
            
            # Convert to JSON string
            import json
            qr_string = json.dumps(qr_data)
            
            # Generate QR code
            qr = segno.make(qr_string, error='H')
            
            # Create directory if it doesn't exist
            qr_dir = Path(settings.upload_dir) / "qr_codes"
            qr_dir.mkdir(parents=True, exist_ok=True)
            
            # Save QR code
            qr_filename = f"{ticket_id}.png"
            qr_path = qr_dir / qr_filename
            
            # Save with higher resolution for better scanning
            qr.save(qr_path, scale=10)
            
            # Generate public URL
            qr_url = f"{settings.upload_dir}/qr_codes/{qr_filename}"
            
            results.append({
                "ticket_id": ticket_id,
                "qr_url": qr_url,
                "success": True
            })
            
            logger.info(f"QR code generated for ticket {ticket_number}")
            
        except Exception as exc:
            logger.error(f"Failed to generate QR code for ticket {ticket_data.get('ticket_number', 'unknown')}: {exc}")
            results.append({
                "ticket_id": ticket_data.get('ticket_id'),
                "qr_url": None,
                "success": False,
                "error": str(exc)
            })
    
    return results


@celery_app.task
def cleanup_old_qr_codes():
    """Clean up old QR code files"""
    
    try:
        qr_dir = Path(settings.upload_dir) / "qr_codes"
        event_qr_dir = Path(settings.upload_dir) / "event_qr_codes"
        
        import time
        current_time = time.time()
        
        # Clean up QR codes older than 30 days
        max_age = 30 * 24 * 60 * 60  # 30 days in seconds
        
        for directory in [qr_dir, event_qr_dir]:
            if directory.exists():
                for file_path in directory.glob("*.png"):
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age:
                        file_path.unlink()
                        logger.info(f"Deleted old QR code: {file_path}")
        
        logger.info("QR code cleanup completed")
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old QR codes: {exc}")


def validate_qr_code(qr_data: str) -> dict:
    """Validate QR code data and return parsed information"""
    
    try:
        import json
        data = json.loads(qr_data)
        
        # Check required fields
        if "type" not in data:
            raise ValueError("Missing type field")
        
        if data["type"] == "ticket":
            required_fields = ["ticket_id", "ticket_number", "booking_id"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
        
        elif data["type"] == "event_checkin":
            required_fields = ["event_id", "event_title"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
        
        else:
            raise ValueError("Invalid QR code type")
        
        return data
        
    except json.JSONDecodeError:
        raise ValueError("Invalid QR code format")
    except Exception as exc:
        raise ValueError(f"QR code validation failed: {exc}")
