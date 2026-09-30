FROM python:3.11-slim

# Install system libraries required by OpenCV, GL, and PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY true_label/backend/requirements.txt .
RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

# Copy backend code
COPY true_label/backend ./backend

# Pre-cache PaddleOCR lightweight PP-OCRv4 mobile models so runtime has 0 download latency & fits in 512MB RAM
# (Removed pre-cache step to bypass Render cache glitch)

ENV PYTHONPATH=/app
ENV PORT=10000

EXPOSE 10000

# Start uvicorn dynamically binding to the port provided by Render ($PORT)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

# Wipe cache completely to avoid zlib corruption
RUN pip cache purge
