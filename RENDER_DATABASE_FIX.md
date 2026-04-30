# Fix: Render Free Database Limit

## Problem
Render only allows **one free PostgreSQL database** per account. You're getting an error because you're trying to create multiple databases.

## Solution: Single Database Approach

### Option 1: Use Existing Database (Recommended)

1. **Keep the first database** you created
2. **Delete the second database creation attempt**
3. **Use the same database URL** for both backend services

### Option 2: Delete and Recreate

1. Go to Render Dashboard → Databases
2. **Delete** any existing databases
3. **Create one new database** with these settings:
   - Name: `event-booking-db`
   - Database Name: `eventbooking`
   - User: `eventbooking_user`
   - Plan: Free

### Option 3: Use SQLite for Development

If you need multiple environments, temporarily use SQLite:

1. **Backend Service**: No DATABASE_URL needed (uses SQLite)
2. **Frontend Service**: Point to local backend for testing

## Updated Deployment Steps

### Step 1: Create One Database
- Only create **one** PostgreSQL database
- Copy the connection string
- Use this for all services

### Step 2: Create Backend API
- Use the single database URL
- No need to create multiple databases

### Step 3: Create Frontend
- Point to the backend that uses the single database

## Environment Variable Fix

For your backend service, use this DATABASE_URL format:
```
DATABASE_URL=postgresql://eventbooking_user:YOUR_PASSWORD@event-booking-db-db-user.a1.render.com:5432/eventbooking
```

## What This Means

- ✅ **One database** for all your services
- ✅ **Free tier** works within Render limits
- ✅ **Shared data** between frontend and backend
- ✅ **No additional cost**

## Next Steps

1. **Delete any existing databases** (if you have multiple)
2. **Create one new database**
3. **Update backend service** to use the single database URL
4. **Deploy both services** using the same database

This approach works perfectly within Render's free tier limitations!
