FROM python:3.12-slim
# Install OS-level dependencies required by:
# - `gcc` (often needed for building python packages with native extensions)
# - `postgresql-client` (provides `pg_dump`/`psql` used by scripts/backup.py)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for safer container execution.
RUN useradd --create-home --shell /bin/bash appuser

# Create a directory where nginx will serve uploaded images from.
RUN mkdir -p /images && chown appuser:appuser /images

# Install Python dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code.
COPY src/ /app/src/

# Ensure the app user owns the working directory.
RUN chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# The python server listens on 8000 inside the container.
EXPOSE 8000

# Run the HTTP server (no framework; uses http.server).
CMD ["python", "src/app.py"]
