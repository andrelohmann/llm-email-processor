#!/bin/bash

echo "--- Custom Ollama Entrypoint ---"

# 1. Starte den Ollama-Server im Hintergrund
ollama serve &
pid=$!

echo "Warte, bis der Ollama-Server bereit ist..."
while ! curl -s -o /dev/null http://127.0.0.1:11434; do
  sleep 1
done
echo "Ollama-Server ist online."

echo "GPU_VRAM ist auf '$GPU_VRAM' gesetzt. Lese Modell-Konfiguration..."

if ! jq -e ".[\"$GPU_VRAM\"]" /app/model_config.json > /dev/null; then
  echo "WARNUNG: Keine spezifische Konfiguration für GPU_VRAM=$GPU_VRAM gefunden. Verwende Fallback (8GB)."
  GPU_VRAM=8
fi

# KORREKTUR: Robusterer jq-Befehl, der den 'comment'-Key explizit ignoriert.
# Er konvertiert das Objekt in Key-Value-Paare, filtert das Kommentar-Paar heraus
# und gibt dann nur die restlichen Werte (die Modellnamen) zurück.
models_to_pull=$(jq -r ".[\"$GPU_VRAM\"] | to_entries | map(select(.key != \"comment\")) | .[].value" /app/model_config.json)

echo "Folgende Modelle werden heruntergeladen:"
echo "$models_to_pull"
for model in $models_to_pull; do
    echo "--- Lade Modell herunter: $model ---"
    ollama pull "$model"
    echo "--- Modell $model fertig ---"
done

echo "Alle konfigurierten Modelle wurden heruntergeladen."
echo "--- Der Container läuft jetzt und bedient Anfragen ---"

wait $pid