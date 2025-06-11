# Base image von Ollama
FROM ollama/ollama:latest

# Metadaten für das Image
LABEL maintainer="AI Architecture Team"
LABEL description="Custom Ollama service that pulls models on startup based on GPU VRAM."

# System-Abhängigkeiten installieren, hier: jq zum Parsen von JSON
# KORREKTUR: Das Image ist Debian-basiert, daher 'apt-get' verwenden.
# Zuerst Paketlisten aktualisieren, dann installieren.
# --no-install-recommends hält das Image klein.
# Am Ende den Cache löschen, um das Image sauber zu halten.
RUN apt-get update && \
    apt-get install -y --no-install-recommends jq curl && \
    rm -rf /var/lib/apt/lists/*

# Kopiere unsere Konfigurations- und Start-Skripte in den Container
# COPY ../model_config.json /app/model_config.json
COPY entrypoint.sh /app/entrypoint.sh
COPY check_readiness.sh /app/check_readiness.sh

RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/check_readiness.sh

# Setze unser Skript als den neuen Entrypoint, der beim Container-Start ausgeführt wird
ENTRYPOINT [ "/app/entrypoint.sh" ]