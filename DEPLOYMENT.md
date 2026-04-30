# Event Booking System - Deployment Guide

## Render Deployment (Recommended)

This guide covers deploying the Event Booking System on Render.com - a modern cloud platform for web applications.

### Quick Start with Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Create Render Account**
   - Sign up at https://render.com
   - Connect your GitHub repository

3. **Deploy Services**
   - Render will automatically detect services from `render.yaml`
   - Services will be deployed in this order:
     1. PostgreSQL Database
     2. Backend API
     3. Frontend Static Site

### Render Configuration

The `render.yaml` file configures:
- **Backend API**: FastAPI service with PostgreSQL
- **Frontend**: React static site
- **Database**: PostgreSQL with automatic connection string

### Environment Variables

Render automatically sets:
- `DATABASE_URL` (from PostgreSQL service)
- `SECRET_KEY` (auto-generated)
- `VITE_API_URL` (points to backend URL)

### Access Your Deployed App

After deployment:
- Frontend: `https://event-booking-frontend.onrender.com`
- Backend API: `https://event-booking-api.onrender.com`
- API Docs: `https://event-booking-api.onrender.com/docs`

## Docker Deployment

This guide covers deploying the Event Booking System using Docker and Docker Compose.

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 80, 3000, 5432, 6379, 8000 available

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd event-booking-system
   ```

2. **Environment Configuration**
   
   Create a `.env` file in the root directory:
   ```env
   # Database
   POSTGRES_DB=event_booking
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres

   # Redis
   REDIS_URL=redis://redis:6379/0

   # Backend
   SECRET_KEY=your-super-secret-key-change-in-production
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/event_booking
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

   # Frontend
   VITE_API_URL=http://localhost:8000
   VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   ```

3. **Build and Start Services**
   ```bash
   docker-compose up --build
   ```

4. **Run Database Migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Nginx (Production): http://localhost:80

### Services Overview

#### 1. PostgreSQL Database
- **Port**: 5432
- **Database**: event_booking
- **User**: postgres
- **Password**: postgres

#### 2. Redis
- **Port**: 6379
- **Purpose**: Caching and Celery broker

#### 3. FastAPI Backend
- **Port**: 8000
- **Features**: REST API, Authentication, Payments
- **Health Check**: http://localhost:8000/health

#### 4. Celery Worker
- **Purpose**: Background job processing
- **Tasks**: Email notifications, payment processing

#### 5. Celery Beat
- **Purpose**: Scheduled tasks
- **Schedule**: Event reminders, cleanup tasks

#### 6. React Frontend
- **Port**: 3000
- **Features**: User interface, QR code scanning

#### 7. Nginx Reverse Proxy
- **Port**: 80
- **Purpose**: Load balancing and SSL termination

### Production Deployment

#### 1. Environment Variables
Update the `.env` file with production values:
```env
SECRET_KEY=your-production-secret-key
STRIPE_SECRET_KEY=sk_live_your_production_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_production_stripe_key
```

#### 2. SSL Configuration
Update `nginx.conf` for SSL:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;
    
    # ... rest of configuration
}
```

#### 3. Database Backups
```bash
# Backup
docker-compose exec postgres pg_dump -U postgres event_booking > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres event_booking < backup.sql
```

#### 4. Monitoring
- Use Docker logs: `docker-compose logs -f`
- Monitor resource usage: `docker stats`
- Health checks are configured for all services

### Development Mode

For development with hot reloading:
```bash
# Start only database and Redis
docker-compose up postgres redis -d

# Start backend in development
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend in development
cd frontend
npm run dev
```

### Troubleshooting

#### Common Issues

1. **Port Conflicts**
   - Check if ports are in use: `netstat -tulpn | grep :80`
   - Update ports in docker-compose.yml if needed

2. **Database Connection**
   - Ensure PostgreSQL is healthy: `docker-compose ps postgres`
   - Check logs: `docker-compose logs postgres`

3. **Build Failures**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild: `docker-compose up --build --force-recreate`

4. **Permission Issues**
   - Fix file permissions: `chmod -R 755 .`
   - Check Docker user permissions

#### Health Checks

All services include health checks. Monitor status:
```bash
docker-compose ps
```

#### Logs

View logs for specific services:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs celery-worker
```

### Scaling

#### Horizontal Scaling
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
  
  celery-worker:
    deploy:
      replicas: 2
```

#### Resource Limits
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Security Considerations

1. **Change Default Passwords**
   - Update PostgreSQL password
   - Use strong secret keys

2. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Limit database exposure

3. **Environment Variables**
   - Store secrets securely
   - Use Docker secrets for production
   - Don't commit .env files

4. **Regular Updates**
   - Keep Docker images updated
   - Monitor security advisories
   - Update dependencies regularly

### Backup Strategy

1. **Database Backups**
   - Daily automated backups
   - Offsite storage
   - Test restoration procedures

2. **File Backups**
   - Upload directory backups
   - Configuration backups
   - Version control

### Performance Optimization

1. **Database Optimization**
   - Index optimization
   - Connection pooling
   - Query optimization

2. **Caching**
   - Redis caching layer
   - Browser caching
   - CDN for static assets

3. **Load Balancing**
   - Nginx load balancing
   - Multiple backend instances
   - Database read replicas

For production deployment, consider using Docker Swarm or Kubernetes for better orchestration and scaling capabilities.
