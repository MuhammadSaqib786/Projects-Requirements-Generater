FROM python:3.11-slim

WORKDIR /app

# add curl so healthcheck can run
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libmagic1 libmagic-dev \
    ghostscript \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# expose & run uvicorn bound to 0.0.0.0 (so healthcheck can hit it)
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
