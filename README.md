# Intelligenter E-Mail Assistent mit lokalen LLMs

Dieses Projekt ist der Prototyp für einen intelligenten E-Mail-Assistenten, der eine Microservice-Architektur mit lokal gehosteten Large Language Models (LLMs) über die [Ollama](https://ollama.com/)-Plattform kombiniert. Ziel ist es, wiederkehrende und zeitaufwendige E-Mail-Aufgaben zu automatisieren.

## ✨ Kernidee

Die Anwendung verbindet sich mit einem E-Mail-Konto, analysiert eingehende E-Mails mithilfe spezialisierter, lokaler LLMs und führt basierend auf den Analyseergebnissen Aktionen aus. Durch den lokalen Betrieb der Modelle bleiben alle Daten privat und unter voller Kontrolle. Die Microservice-Architektur sorgt für Entkopplung, Skalierbarkeit und einfache Wartbarkeit der einzelnen Komponenten.

## 🚀 Features

### Aktueller Fokus (MVP)
*   **Newsletter-Erkennung & -Bereinigung**: Identifiziert Newsletter und verschiebt sie zur späteren Abmeldung oder Löschung.
*   **Extraktion von Job-Angeboten**: Erkennt E-Mails von Recruitern und extrahiert strukturierte Informationen (Firma, Position, Ansprechpartner).

### Zukünftige Erweiterungen (Roadmap)
*   **Intelligente Löschfunktion**: Löscht irrelevante E-Mails basierend auf Inhaltsanalyse, nicht nur auf dem Alter.
*   **Spam-Filter-Optimierung**: Analysiert den Spam-Ordner auf fälschlicherweise einsortierte E-Mails ("False Positives").
*   **Automatisierte Triage**: Kategorisiert E-Mails in "Dringend", "Wichtig", "Info" etc.
*   **Zusammenfassungen**: Erstellt per Klick Zusammenfassungen von langen Konversationen.
*   **Antwort-Entwürfe**: Generiert Vorschläge für Standardantworten.

## 🏛️ Architektur

Die Anwendung folgt einem Microservice-Ansatz, der über `docker-compose` orchestriert wird.

```mermaid
graph TD
    subgraph "E-Mail Backend"
        MailServer[IMAP / Google / Microsoft API]
    end

    subgraph "Anwendung"
        UI(User Interface) --> API_Gateway{API Gateway}
        API_Gateway --> Orchestrator
        
        Orchestrator --> EmailConnector[Email Connector Service]
        Orchestrator --> LLM_Service[LLM Inference Service]
        Orchestrator --> ActionService[Action Service]

        EmailConnector <--> MailServer
        ActionService --> EmailConnector

        LLM_Service --> Ollama[Ollama Container (GPU)]
    end

    User[Benutzer] --> UI
```

*   **Ollama Service**: Stellt die Ollama-API bereit und lädt Modelle basierend auf der verfügbaren GPU-VRAM-Grösse.
*   **Email Connector Service**: Eine dedizierte API-Schnittstelle zum E-Mail-Konto. Bietet Adapter für IMAP, Google API etc. und kümmert sich um die technische Kommunikation (Abrufen, Verschieben, Markieren).
*   **Orchestration Service (in Entwicklung)**: Das Gehirn der Anwendung. Holt E-Mails über den Connector, entscheidet, welche Analyse nötig ist, und delegiert an den LLM- und Action-Service.
*   **Action Service (in Entwicklung)**: Führt Aktionen wie "Verschieben in den Papierkorb" oder "Als gelesen markieren" über den Email Connector aus.
*   **UI / API Gateway (in Entwicklung)**: Dient der Konfiguration und der manuellen Überprüfung ("Human-in-the-Loop").

## 🛠️ Technologie-Stack

*   **Backend**: Python 3.11+
*   **API-Framework**: FastAPI
*   **KI / LLMs**: [Ollama](https://ollama.com/) mit Modellen wie Llama3, Mistral, Phi-3
*   **Containerisierung**: Docker & Docker Compose
*   **Message Queue / State**: Redis
*   **Entwicklungsumgebung**: VS Code mit Devcontainern

## ⚙️ Setup & Inbetriebnahme

Dieses Projekt ist für die Entwicklung in **VS Code Devcontainern** optimiert.

### Voraussetzungen
1.  [Git](https://git-scm.com/)
2.  [Docker Desktop](https://www.docker.com/products/docker-desktop/)
3.  [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (falls eine NVIDIA GPU genutzt wird)
4.  [Visual Studio Code](https://code.visualstudio.com/)
5.  Die **[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)**-Erweiterung in VS Code.

### Installationsschritte

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/DEIN-BENUTZERNAME/email-processor.git
    cd email-processor
    ```

2.  **Konfigurationsdatei erstellen:**
    Erstellen Sie eine `.env`-Datei im Hauptverzeichnis. Sie können die Vorlage `env.example` kopieren:
    ```bash
    cp .env.example .env
    ```
    Passen Sie die Werte in der `.env`-Datei an Ihre Umgebung an:

    ```dotenv
    # VRAM der verfügbaren GPU in GB (z.B. 8, 12, 16, 24)
    GPU_VRAM=16

    # --- Email Connector Konfiguration ---
    MAIL_PROVIDER=imap
    # Für Gmail: imap.gmail.com, für GMX: imap.gmx.net, etc.
    MAIL_IMAP_HOST=imap.gmail.com
    MAIL_USER=deine-email@example.com
    # WICHTIG: Hier ein App-spezifisches Passwort verwenden!
    MAIL_PASSWORD=dein-app-passwort
    ```

### Entwicklungs-Workflow

Dieses Projekt nutzt den zentralen Devcontainer-Ansatz für eine optimale Übersicht.

1.  Öffnen Sie das **Hauptverzeichnis** (`email-processor/`) in VS Code.
2.  Öffnen Sie die Befehlspalette (`Ctrl+Shift+P` oder `Cmd+Shift+P`).
3.  Wählen Sie den Befehl **`Dev Containers: Open Folder in Container`**.
4.  Wählen Sie das gewünschte Service Verzeichnis (z.B. `email_connector`).
5.  VS Code startet nun die gesamte `docker-compose`-Umgebung und verbindet das Fenster mit dem ausgewählten Service-Container.

## 🤝 Mitwirken

Beiträge sind herzlich willkommen! Bitte erstellen Sie einen Fork des Repositories und senden Sie einen Pull Request. Für größere Änderungen eröffnen Sie bitte zuerst ein Issue, um zu diskutieren, was Sie ändern möchten.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die `LICENSE`-Datei für Details.