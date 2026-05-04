from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time
import uuid
from contextlib import asynccontextmanager

from app.config import settings
# from app.database import init_db, close_db
from app.routers import events, tickets, payments
from app.api import email
import simple_auth
# from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - using simple auth, no database needed
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A comprehensive event booking and ticketing system",
    lifespan=lifespan,
)

# CORS middleware - explicitly allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.eventbooking.com"]
)

# Rate limiting middleware - disabled for now
# app.add_middleware(RateLimitMiddleware)
# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Serve frontend static files
try:
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="frontend")
except Exception:
    # Fallback if frontend not built
    pass


@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    """Add request ID and timing information to responses"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    return {
        "message": "Event Booking System API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time()
    }


# Include routers
app.include_router(simple_auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(email.router, prefix="/api/email", tags=["email"])
# app.include_router(events.router, prefix="/api/events", tags=["events"])
# app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
# app.include_router(payments.router, prefix="/api/payments", tags=["payments"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
