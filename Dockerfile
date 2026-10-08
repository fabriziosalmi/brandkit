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
COPY requirements.txt requirements.lock* ./
RUN pip install --no-cache-dir -r requirements.txt

# Create dedicated non-root user and setup runtime directories
RUN useradd -u 1000 -m -s /bin/bash brandkit \
    && mkdir -p /app/static/uploads/cache /home/brandkit/.u2net \
    && chown -R brandkit:brandkit /app /home/brandkit

# Copy project code with proper ownership
COPY --chown=brandkit:brandkit . .

# Set U2NET home for model downloads
ENV U2NET_HOME=/home/brandkit/.u2net

# Switch to dedicated non-root user
USER brandkit

# Expose port
EXPOSE 8000

# Entrypoint
CMD ["bash", "entrypoint.sh"]