# Manual Render Deployment Guide

## Option 1: Make Repository Public (Recommended)

1. Go to https://github.com/Aaditya3333/Event-Booking
2. Click Settings → Change repository visibility → Public
3. Retry deployment on Render

## Option 2: Manual Web Service Setup

### Backend API Service
1. Go to Render Dashboard → New → Web Service
2. Connect GitHub → Select Event-Booking repository
3. **Name**: event-booking-api
4. **Root Directory**: backend
5. **Runtime**: Python 3
6. **Build Command**: pip install -r requirements.txt
7. **Start Command**: uvicorn app.main:app --host 0.0.0.0 --port $PORT
8. **Add Environment Variables**:
   - DATABASE_URL: (create PostgreSQL database first)
   - SECRET_KEY: (generate random key)
   - CORS_ORIGINS: https://event-booking-frontend.onrender.com

### Frontend Service
1. New → Web Service
2. Connect GitHub → Select Event-Booking repository
3. **Name**: event-booking-frontend
4. **Root Directory**: frontend
5. **Runtime**: Static
6. **Build Command**: npm run build
7. **Publish Directory**: dist
8. **Add Environment Variables**:
   - VITE_API_URL: https://event-booking-api.onrender.com

### Database
1. New → PostgreSQL
2. **Name**: event-booking-db
3. **Database Name**: eventbooking
4. **User**: eventbooking_user

## Option 3: Alternative Deployment Platforms

If Render continues to have issues, try:
- Vercel (for frontend)
- Railway (for backend + database)
- Heroku (for backend + database)
- Netlify (for frontend)
