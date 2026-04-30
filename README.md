# Event Booking & Ticketing System

A full-stack event booking and ticketing system built with FastAPI (backend) and React (frontend).

## Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Primary database with ACID compliance
- **SQLAlchemy 2.0** - Async ORM for database operations
- **Alembic** - Database migrations
- **Celery + Redis** - Background job processing
- **JWT Authentication** - Secure user authentication
- **Stripe** - Payment processing

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

### Infrastructure
- **Docker** - Containerization
- **Nginx/Traefik** - Reverse proxy
- **Redis** - Caching and session store

## Features

- Event creation and management
- Multi-tier ticket pricing
- Real-time seat availability
- Secure payment processing
- QR code ticket generation
- Mobile-friendly check-in system
- User authentication and authorization
- Admin dashboard
- Email notifications

## Quick Start

1. Clone the repository
2. Set up environment variables
3. Run with Docker Compose
4. Access the application

## Development

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
alembic upgrade head
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## License

MIT License
