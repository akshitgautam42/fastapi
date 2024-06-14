# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/scripts:${PATH}"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install python-dotenv  # Install dotenv module

# Copy the application code
COPY . .

# Expose the port on which the FastAPI application will run (default is 8000)
EXPOSE 8000

# Command to run the FastAPI application with Uvicorn, loading environment variables from .env
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--env-file", ".env"]
