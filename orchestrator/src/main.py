import requests
import time
import json
import os
from apscheduler.schedulers.blocking import BlockingScheduler

# --- Konstanten und Konfiguration ---
EMAIL_CONNECTOR_URL = "http://email-connector:8000"
OLLAMA_URL = "http://ollama:11434/api/chat"
MODEL_CONFIG_PATH = "/app/config/model_config.json"

# Globale Variable für die geladene Modellkonfiguration
MODEL_CONFIG = {}

def load_model_configuration():
    """Lädt die Modell-Konfiguration aus der JSON-Datei beim Start."""
    global MODEL_CONFIG
    try:
        print(f"Lade Modell-Konfiguration von: {MODEL_CONFIG_PATH}")
        with open(MODEL_CONFIG_PATH, 'r') as f:
            MODEL_CONFIG = json.load(f)
        print("Modell-Konfiguration erfolgreich geladen.")
    except FileNotFoundError:
        print(f"FATAL: Konfigurationsdatei nicht gefunden unter {MODEL_CONFIG_PATH}. Service kann nicht starten.")
        exit(1)
    except json.JSONDecodeError:
        print(f"FATAL: Konfigurationsdatei {MODEL_CONFIG_PATH} ist kein valides JSON. Service kann nicht starten.")
        exit(1)

def get_model_for_task(task: str) -> str:
    """
    Wählt das passende Modell für einen gegebenen Task basierend auf dem verfügbaren VRAM.
    """
    # Lese VRAM aus Environment-Variable, mit Fallback auf "8"
    gpu_vram = os.getenv("GPU_VRAM", "8")
    
    # Prüfe, ob eine Konfiguration für den VRAM-Wert existiert
    if gpu_vram not in MODEL_CONFIG:
        print(f"WARNUNG: Keine Konfiguration für GPU_VRAM={gpu_vram} gefunden. Verwende Fallback (8GB).")
        gpu_vram = "8"
        
    config_for_vram = MODEL_CONFIG[gpu_vram]
    
    # Wähle das Modell für den spezifischen Task aus, mit Fallback
    model = config_for_vram.get(task)
    if not model:
        print(f"WARNUNG: Kein Modell für Task '{task}' in {gpu_vram}GB-Konfig gefunden. Verwende 'classification'-Modell als Fallback.")
        model = config_for_vram.get("classification")
        
    print(f"Modell für Task '{task}' bei {gpu_vram}GB VRAM ausgewählt: {model}")
    return model

def analyze_email_category(email_text: str) -> dict:
    """
    Sendet den E-Mail-Text an den Ollama-Service und bittet um eine Klassifizierung.
    """
    # Holen Sie sich das Modell dynamisch für die Aufgabe "Klassifizierung"
    classification_model = get_model_for_task("classification")
    
    truncated_text = (email_text[:4000] + '...') if len(email_text) > 4000 else email_text
    
    system_prompt = (
        'Du bist ein Experte für Textklassifizierung. Deine Aufgabe ist es, den Text des Benutzers zu analysieren '
        'und ihn einer der folgenden drei Kategorien zuzuordnen: "Job-Angebot", "Newsletter" oder "Sonstiges".\n'
        'Antworte ausschließlich mit einem validen JSON-Objekt, das genau zwei Schlüssel enthält: "category" und "reason".'
    )

    payload = {
        "model": classification_model,
        "messages": [
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": truncated_text }
        ],
        "format": "json",
        "stream": False
    }

    print(f"  > Sende E-Mail zur Analyse an Ollama Chat API (Modell: {classification_model})...")
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        response_data = response.json()
        message_content = response_data.get("message", {}).get("content", "{}")
        analysis_result = json.loads(message_content)
        
        return analysis_result

    except requests.exceptions.RequestException as e:
        print(f"  ! Fehler bei der Kommunikation mit Ollama: {e}")
    except json.JSONDecodeError as e:
        print(f"  ! Fehler beim Parsen der LLM-Antwort: {e}")
        print(f"  > Rohe Antwort von Ollama: {response.text}")

    return {"category": "error", "reason": "Analyse fehlgeschlagen"}

# Die Funktion fetch_and_process_emails bleibt exakt gleich wie in Ihrer Version.
def fetch_and_process_emails():
    print("\n--- [Orchestrator] Starte E-Mail-Abruf-Zyklus ---")
    try:
        response = requests.get(f"{EMAIL_CONNECTOR_URL}/emails/unread?limit=5")
        response.raise_for_status()
        emails = response.json()
        if not emails:
            print("Keine neuen ungelesenen E-Mails gefunden.")
            return
        print(f"Erfolgreich {len(emails)} E-Mails abgerufen. Starte Analyse...")
        for i, email in enumerate(emails, 1):
            print(f"\nVerarbeite E-Mail {i}/{len(emails)} (UID: {email.get('uid')}) - Betreff: {email.get('subject')}")
            email_content = email.get("text", "")
            if not email_content:
                print("  - E-Mail hat keinen Textinhalt. Überspringe.")
                continue
            analysis = analyze_email_category(email_content)
            category = analysis.get("category", "Unbekannt")
            reason = analysis.get("reason", "Keine Begründung.")
            print(f"  ==> Ergebnis: Kategorie = '{category}', Begründung = '{reason}'")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abruf der E-Mails vom Connector: {e}")
    print("\n--- [Orchestrator] Zyklus beendet ---")


if __name__ == "__main__":
    print("Orchestration Service wird gestartet.")
    
    # Lade die Konfiguration, bevor der Scheduler startet
    load_model_configuration()
    
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_process_emails, 'interval', seconds=120, id='email_fetch_job')
    
    print("Führe initialen E-Mail-Abruf aus...")
    fetch_and_process_emails()
    
    print("Scheduler startet... Nächster Lauf in 2 Minuten.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass