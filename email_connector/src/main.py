from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any

from .config import settings
from .adapters.imap_adapter import IMAPAdapter
from .adapters.base_adapter import BaseMailAdapter

app = FastAPI(title="Email Connector Service")

def get_adapter() -> BaseMailAdapter:
    """Factory-Funktion, die den passenden Adapter basierend auf der Konfiguration zurückgibt."""
    if settings.mail_provider == "imap":
        return IMAPAdapter()
    # Hier könnten später andere Adapter hinzugefügt werden
    # elif settings.mail_provider == "google":
    #     return GoogleAdapter()
    else:
        raise ValueError(f"Ungültiger Mail-Provider: {settings.mail_provider}")

adapter = get_adapter()

@app.get("/emails/unread", response_model=List[Dict[str, Any]])
def get_unread_emails(
    limit: int = Query(50, gt=0, le=100), 
    offset: int = Query(0, ge=0)
):
    """Ruft eine Seite von ungelesenen E-Mails aus dem Posteingang ab."""
    try:
        return adapter.fetch_unread_emails(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/mark-as-read")
def mark_email_as_read(uid: str):
    """Markiert eine E-Mail anhand ihrer UID als gelesen."""
    try:
        adapter.mark_as_read(uid)
        return {"status": "success", "message": f"Email {uid} wurde als gelesen markiert."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/emails/move")
def move_email_to_folder(uid: str, destination: str):
    """Verschiebt eine E-Mail anhand ihrer UID in einen Zielordner."""
    try:
        adapter.move_email(uid, destination)
        return {"status": "success", "message": f"Email {uid} wurde nach {destination} verschoben."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))