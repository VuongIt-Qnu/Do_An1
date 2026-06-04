# =============================================================================
# Dockerfile — Flask Backend
# Multi-stage build for production optimization
# =============================================================================

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# ── Development stage ─────────────────────────────────────────────
FROM base AS development
ENV FLASK_ENV=development
CMD ["python", "run.py"]

# ── Production stage ──────────────────────────────────────────────
FROM base AS production
ENV FLASK_ENV=production
# Use gunicorn for production (4 worker processes)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
