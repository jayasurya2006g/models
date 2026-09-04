#!/bin/bash
# Startup script for Render deployment
# Reduce memory usage by limiting Python garbage collection and thread pool

export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Run uvicorn with optimized settings
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --loop uvloop \
    --http httptools \
    --timeout-graceful-shutdown 30
