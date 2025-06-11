#!/bin/bash

# --- check_readiness.sh ---
# Dieses Skript prüft, ob der Ollama-Service nicht nur läuft, sondern auch
# alle für die konfigurierte VRAM-Größe benötigten Modelle geladen hat.

# Stellt sicher, dass das Skript im Fehlerfall abbricht
set -e

# --- 1. Prüfung: Läuft der Ollama Server überhaupt? ---
echo "[Healthcheck] Prüfe, ob Ollama API unter http://127.0.0.1:11434 erreichbar ist..."
if ! curl -s -f http://127.0.0.1:11434/ > /dev/null; then
    echo "[Healthcheck] FEHLER: Ollama API antwortet nicht."
    exit 1
fi
echo "[Healthcheck] OK: Ollama API ist erreichbar."


# --- 2. Prüfung: Sind alle benötigten Modelle geladen? ---

# Lese VRAM-Konfiguration, mit Fallback auf 8GB
VRAM_TO_CHECK=${GPU_VRAM:-8}
echo "[Healthcheck] Prüfe Modelle für VRAM-Größe: ${VRAM_TO_CHECK}GB"

# Hole die Liste der benötigten Modelle aus der Konfigurationsdatei
# Wir verwenden den robusten jq-Befehl, der Kommentare ignoriert.
# Der Pfad /app/model_config.json entspricht dem Zielpfad im Container.
REQUIRED_MODELS=$(jq -r ".[\"$VRAM_TO_CHECK\"] | to_entries | map(select(.key != \"comment\")) | .[].value" /app/model_config.json)
if [ -z "$REQUIRED_MODELS" ]; then
    echo "[Healthcheck] FEHLER: Konnte keine Modelle für VRAM=${VRAM_TO_CHECK} aus der Konfigurationsdatei lesen."
    exit 1
fi
echo "[Healthcheck] Benötigte Modelle: $REQUIRED_MODELS"

# Hole die Liste der tatsächlich verfügbaren Modelle von der Ollama API
AVAILABLE_MODELS=$(curl -s http://127.0.0.1:11434/api/tags | jq -r '.models[].name')
echo "[Healthcheck] Verfügbare Modelle: $AVAILABLE_MODELS"

# Prüfe für jedes benötigte Modell, ob es in der Liste der verfügbaren Modelle enthalten ist
for model in $REQUIRED_MODELS; do
    if ! echo "$AVAILABLE_MODELS" | grep -q -w "$model"; then
        echo "[Healthcheck] WARTEN: Modell '$model' ist noch nicht verfügbar."
        # Wir geben Exit-Code 1 zurück, damit Docker es erneut versucht
        exit 1
    fi
done

# --- 3. Erfolg: Alle Prüfungen bestanden ---
echo "[Healthcheck] ERFOLG: Alle benötigten Modelle sind geladen. Service ist bereit!"
# Exit-Code 0 signalisiert Docker, dass der Container "healthy" ist.
exit 0