# Placeholder Dockerfile for Render
# This allows Render to clone the repository successfully
# The actual deployment will# Single Server Dockerfile - Frontend + Backend on Port 8000
FROM python:3.11-slim

# Install Node.js for frontend build
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Build frontend
COPY frontend/ /frontend/
WORKDIR /frontend
RUN npm install && npx vite build --mode production

# Copy frontend build to backend static directory
WORKDIR /app
RUN cp -r /frontend/dist /app/static/

# Copy backend code
COPY backend/ /app/

# Expose port 8000
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
