FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

# KORREKTUR: Fügen Sie das "-u" Flag hinzu, um den Output sofort auszugeben
CMD ["python", "-u", "src/main.py"]