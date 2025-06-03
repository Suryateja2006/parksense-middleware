FROM python:3.9-slim as builder

WORKDIR /app

# Install only essential build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
FROM python:3.9-slim as runtime

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY app.py .
COPY best.pt .

# Clean up and install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean autoclean \
    && apt-get autoremove -y

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default port if $PORT not set
ENV PORT=8000

CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT} --timeout 120 app:app"]