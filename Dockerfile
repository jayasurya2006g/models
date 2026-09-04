FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with CPU-only PyTorch to save ~4GB
# This significantly reduces image size and memory footprint
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    rm -rf /root/.cache

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Memory and performance optimizations for Render free tier (512MB limit)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV TORCH_HOME=/tmp

# Run with single worker to save memory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
