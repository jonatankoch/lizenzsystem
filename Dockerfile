FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Systempakete (später wichtig für psycopg2/Postgres, schadet jetzt nicht)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektcode kopieren
COPY app ./app

# Port für Uvicorn
EXPOSE 8000

# Startkommando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
