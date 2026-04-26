# Use a stable slim Python base (smaller + fewer surprises)
FROM python:3.10-slim

# Prevent Python from writing .pyc files & buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (FIXED)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Make sure model path exists (avoid runtime crash)
RUN mkdir -p /app/static/models

# Expose port
EXPOSE 8080

# Run app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "--worker-class", "gevent", "app:app"]