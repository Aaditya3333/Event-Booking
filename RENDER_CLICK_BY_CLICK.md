# Render Deployment - Click by Click Guide

## Before You Start
- Make sure your GitHub repo is public
- Have your GitHub login ready
- This should take 10-15 minutes total

## Step 1: Create PostgreSQL Database (2 minutes)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"PostgreSQL"**
4. Fill in the form:
   - **Name**: `event-booking-db`
   - **Database Name**: `eventbooking`
   - **User**: `eventbooking_user`
   - **Plan**: Free
5. Click **"Create Database"**
6. Wait for it to be ready (green status)
7. **IMPORTANT**: Copy the **Internal Database URL** from the database dashboard
   - Look for "Connection" section
   - Copy the `postgresql://...` string

## Step 2: Create Backend API Service (5 minutes)

1. Go back to Render Dashboard
2. Click **"New +"** → **"Web Service"**
3. **Connect GitHub**:
   - Click "Connect Account"
   - Authorize Render to access your GitHub
   - Select **"Event-Booking"** repository
4. **Configure Service**:
   - **Name**: `event-booking-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python`
   - **Plan**: `Free`
5. **Build Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Health Check**:
   - **Health Check Path**: `/health`
7. **Environment Variables** (click "Add Environment Variable"):
   - `DATABASE_URL`: `[paste the database URL from Step 1]`
   - `SECRET_KEY`: `your-super-secret-key-change-this-in-production`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
   - `ALGORITHM`: `HS256`
   - `CORS_ORIGINS`: `https://event-booking-frontend.onrender.com`
8. Click **"Create Web Service"**
9. Wait for deployment (3-5 minutes)

## Step 3: Create Frontend Service (3 minutes)

1. Go to Render Dashboard
2. Click **"New +"** → **"Web Service"**
3. **Connect GitHub**: Select the same "Event-Booking" repository
4. **Configure Service**:
   - **Name**: `event-booking-frontend`
   - **Root Directory**: `frontend`
   - **Runtime**: `Static`
   - **Plan**: `Free`
5. **Build Settings**:
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`
6. **Environment Variables**:
   - `VITE_API_URL`: `https://event-booking-api.onrender.com`
7. Click **"Create Web Service"**
8. Wait for deployment (2-3 minutes)

## Step 4: Test Everything (2 minutes)

Once all services are green:

1. **Frontend URL**: `https://event-booking-frontend.onrender.com`
2. **Backend API**: `https://event-booking-api.onrender.com`
3. **API Documentation**: `https://event-booking-api.onrender.com/docs`

**Test the Application**:
1. Open the frontend URL
2. Try to login: `test@example.com` / `test123`
3. Browse events and try booking
4. Check if everything works

## Troubleshooting

If something fails:

1. **Check Logs**: Go to the service → "Logs" tab
2. **Build Errors**: Check the "Events" tab for build failures
3. **Database Connection**: Verify DATABASE_URL is correct
4. **Environment Variables**: Make sure all are set without typos

## Success!

When everything works:
- 🎉 Your Event Booking System is live!
- 🌐 Frontend: `https://event-booking-frontend.onrender.com`
- 🔧 Backend: `https://event-booking-api.onrender.com`
- 📚 API Docs: `https://event-booking-api.onrender.com/docs`

## What You Get

- ✅ Free hosting (no cost)
- ✅ SSL certificates (HTTPS)
- ✅ Automatic deployments
- ✅ Custom domain support (later)
- ✅ Monitoring and logs

Just follow these steps exactly and you'll have your app live in minutes!
