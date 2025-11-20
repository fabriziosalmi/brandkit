# Use official Python image
FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies for rembg + OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libwebp-dev \
    libopencv-core-dev \
    libopencv-imgproc-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install background removal + computer vision deps
RUN pip install --no-cache-dir rembg onnxruntime opencv-python-headless numpy

# Install Python backend requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Entrypoint
CMD ["bash", "entrypoint.sh"]