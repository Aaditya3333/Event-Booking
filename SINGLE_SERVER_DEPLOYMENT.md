# Single Server Deployment Guide

## Overview
Your Event Booking System now runs on a single server with both frontend and backend served from the same FastAPI application on port 8000.

## Architecture
- **Single FastAPI Server**: Serves both API and frontend
- **Frontend**: React app built to static files
- **Backend**: FastAPI with all API endpoints
- **Port**: 8000 (everything on one port)

## Local Development
```bash
# Start the single server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000`

## Production Deployment (Render)

### Step 1: Update Render Service
Since you already have services on Render, update your backend service:

1. **Go to Render Dashboard**
2. **Select your backend service**: `event-booking-api`
3. **Update Build Settings**:
   - **Build Command**: `cd frontend && npm run build && cd .. && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 2: Environment Variables
Keep the same environment variables:
- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: Your secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
- `ALGORITHM`: `HS256`
- `CORS_ORIGINS`: `https://event-booking-api.onrender.com`

### Step 3: Deploy
1. **Push changes to GitHub** (already done)
2. **Trigger manual deploy** on Render
3. **Wait for deployment** (5-10 minutes)

### Step 4: Delete Frontend Service (Optional)
Since frontend is now served by backend, you can delete the separate frontend service to save resources.

## URLs After Deployment
- **Main Application**: `https://event-booking-api.onrender.com`
- **API Documentation**: `https://event-booking-api.onrender.com/docs`
- **Health Check**: `https://event-booking-api.onrender.com/health`

## Benefits
✅ **Simpler Architecture**: One service instead of two
✅ **No CORS Issues**: Same origin for everything
✅ **Easier Maintenance**: Single codebase to manage
✅ **Lower Resource Usage**: One service instead of two
✅ **Better Performance**: No cross-origin requests

## Testing
1. **Frontend loads** at main URL
2. **API endpoints work** at `/api/*`
3. **Login functionality** works
4. **Event browsing** works
5. **Booking flow** works

## Troubleshooting
If frontend doesn't load:
1. Check build logs for frontend build errors
2. Verify `frontend/dist` folder exists
3. Check FastAPI logs for mounting errors
4. Ensure static file serving is enabled

Your Event Booking System is now optimized for single-server deployment!
