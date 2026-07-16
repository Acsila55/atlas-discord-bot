# --- Builder Stage ---
FROM python:3.12-slim AS builder

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into a local directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Runtime ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Update path to include the installed packages
ENV PATH=/root/.local/bin:$PATH

# Run as a non-root user for security (best practice)
RUN useradd -m botuser
USER botuser

# Start your bot
CMD ["python", "main.py"]
