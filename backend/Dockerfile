# Base image with Python 3.11
FROM python:3.11-slim

# Install system dependencies: graphviz, wkhtmltopdf, and common build tools
RUN apt-get update && apt-get install -y \
    graphviz \
    wkhtmltopdf \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in container
WORKDIR /app

# Copy backend code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

# Expose port for FastAPI
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]