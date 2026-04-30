import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./event_booking.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Stripe
    stripe_secret_key: str = "sk_test_your_stripe_secret_key"
    stripe_publishable_key: str = "pk_test_your_stripe_publishable_key"
    stripe_webhook_secret: str = "whsec_your_webhook_secret"
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "your-email@gmail.com"
    smtp_password: str = "your-app-password"
    email_from: str = "noreply@eventbooking.com"
    
    # Application
    app_name: str = "Event Booking System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002", "http://localhost:3003", "http://127.0.0.1:3003", "http://localhost:3004", "http://127.0.0.1:3004", "http://localhost:3005", "http://127.0.0.1:3005", "http://localhost:3006", "http://127.0.0.1:3006", "http://localhost:3007", "http://127.0.0.1:3007"]
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
