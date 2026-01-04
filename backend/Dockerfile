# Use Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for dlib and face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgthread-2.0-0 \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Install dlib first as it takes longer to compile
RUN pip install --no-cache-dir dlib && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directories
RUN mkdir -p database/faces database/images database/encodings

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
