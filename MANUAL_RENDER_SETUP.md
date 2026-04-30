# Manual Render Setup Guide

Since the automatic render.yaml is causing Dockerfile issues, let's set up the services manually on Render.

## Step 1: Create PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. **Name**: event-booking-db
3. **Database Name**: eventbooking
4. **User**: eventbooking_user
5. **Plan**: Free
6. Click "Create Database"
7. Wait for it to be ready (2-3 minutes)
8. Copy the **Connection String** from the database dashboard

## Step 2: Create Backend API Service

1. Go to Render Dashboard → New → Web Service
2. **Connect GitHub**: Select your Event-Booking repository
3. **Name**: event-booking-api
4. **Root Directory**: backend
5. **Runtime**: Python
6. **Plan**: Free
7. **Build Command**: `pip install -r requirements.txt`
8. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
9. **Health Check Path**: `/health`

10. **Add Environment Variables**:
    - `DATABASE_URL`: (paste the connection string from Step 1)
    - `SECRET_KEY`: (generate a random key, e.g., from https://randomkeygen.com)
    - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
    - `ALGORITHM`: `HS256`
    - `CORS_ORIGINS`: `https://event-booking-frontend.onrender.com`

11. Click "Create Web Service"
12. Wait for deployment (3-5 minutes)

## Step 3: Create Frontend Service

1. Go to Render Dashboard → New → Web Service
2. **Connect GitHub**: Select your Event-Booking repository
3. **Name**: event-booking-frontend
4. **Root Directory**: frontend
5. **Runtime**: Static
6. **Plan**: Free
7. **Build Command**: `npm run build`
8. **Publish Directory**: `dist`

9. **Add Environment Variables**:
    - `VITE_API_URL`: `https://event-booking-api.onrender.com`

10. Click "Create Web Service"
11. Wait for deployment (2-3 minutes)

## Step 4: Test Your Application

Once all services are deployed:

1. **Frontend URL**: `https://event-booking-frontend.onrender.com`
2. **Backend API**: `https://event-booking-api.onrender.com`
3. **API Documentation**: `https://event-booking-api.onrender.com/docs`

## Step 5: Verify Everything Works

1. Test the frontend loads
2. Try login with: `test@example.com` / `test123`
3. Browse events and try booking
4. Check if email notifications work

## Troubleshooting

If something fails:

1. **Check Logs**: Go to each service → Logs
2. **Check Environment Variables**: Make sure all are set correctly
3. **Database Connection**: Verify the DATABASE_URL is correct
4. **Build Failures**: Check the build logs for specific errors

## Alternative: Use render-simple.yaml

If you want to try automatic deployment again, rename `render-simple.yaml` to `render.yaml` and redeploy.

The manual setup gives you more control and better error visibility!
