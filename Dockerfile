# ---------- STAGE 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ---------- STAGE 2: Runtime ----------
FROM python:3.11-slim

# Set UTC timezone
ENV TZ=UTC

WORKDIR /app

# Install system dependencies (cron + tzdata)
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Copy python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app ./app
COPY scripts ./scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Copy key files
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

# Set permissions for cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose API port
EXPOSE 8080

# Start cron + API
CMD service cron start && \
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
