FROM python:3.11-slim

WORKDIR /app

# Installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Quellcode
COPY ./src /app/src

# Starte die Anwendung
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]