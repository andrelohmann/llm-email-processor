FROM python:3.11-slim

WORKDIR /app

# KORREKTUR: Wir installieren curl, damit der Healthcheck funktioniert.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Quellcode
COPY ./src /app/src

# Starte die Anwendung
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]