# Use Python 3.12 slim image for minimal footprint
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for efficient layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Expose container application port
EXPOSE 8000

# Native Python-based Healthcheck (No curl or additional packages required)
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; res = urllib.request.urlopen('http://localhost:8000/health'); sys.exit(0 if res.getcode() == 200 else 1)"

# Entry point using Uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
