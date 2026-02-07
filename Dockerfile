# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    ca-certificates \
    default-mysql-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Static files will be served by WhiteNoise
RUN python manage.py collectstatic --noinput

# Make scripts executable
RUN chmod +x entrypoint.sh

# Run the application via entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
