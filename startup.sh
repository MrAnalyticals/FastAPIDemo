#!/bin/bash
export PYTHONUNBUFFERED=1
# Use the PORT environment variable if available, otherwise default to 8000
PORT=${PORT:-8000}
uvicorn app.main:app --host 0.0.0.0 --port $PORT
