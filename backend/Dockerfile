
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

# RUN mkdir -p /app/static

# ✅ Correct path to requirements.txt
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy rest of source code
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] #dev
