FROM python:3.9-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Explicitly copy your model
COPY best.pt ./best.pt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT}", "app:app"]