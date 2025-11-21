# # Base image with Python 3.11
# FROM python:3.11-slim

# # Install system dependencies: graphviz, wkhtmltopdf, and common build tools
# RUN apt-get update && apt-get install -y \
#     graphviz \
#     wkhtmltopdf \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory in container
# WORKDIR /app

# # Copy backend code
# COPY . /app

# # Install Python dependencies
# RUN pip install --no-cache-dir -r app/requirements.txt

# # Expose port for FastAPI
# EXPOSE 8000

# # Command to run the app
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# New 02

# # Base image with Python 3.11 (Bookworm has wkhtmltopdf in repo)
# FROM python:3.11-slim-bookworm

# # Install system dependencies: graphviz, wkhtmltopdf, and common build tools
# RUN apt-get update && apt-get install -y \
#     graphviz \
#     wkhtmltopdf \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory in container
# WORKDIR /app

# # Copy backend code
# COPY . /app

# # Install Python dependencies
# RUN pip install --no-cache-dir -r app/requirements.txt

# # Expose port for FastAPI
# EXPOSE 8000

# # Command to run the app
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# New 03

FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    graphviz \
    wkhtmltopdf \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# venv outside /app so mounted source doesn't overwrite
ENV VENV_PATH=/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app

# ✅ Correct path to requirements.txt
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy rest of source code
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
