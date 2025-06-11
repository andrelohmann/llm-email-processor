from itertools import islice
from imap_tools import MailBox, A
from typing import List, Dict, Any
from .base_adapter import BaseMailAdapter
from ..config import settings

class IMAPAdapter(BaseMailAdapter):
    def __init__(self):
        self.host = settings.mail_imap_host
        self.user = settings.mail_user
        self.password = settings.mail_password

    def fetch_unread_emails(self, folder: str = "INBOX", limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        emails = []
        try:
            # Verwendung des Context-Managers für saubere Verbindungen
            with MailBox(self.host).login(self.user, self.password, initial_folder=folder) as mailbox:
                
                # 1. Erstelle einen Generator für ungelesene Nachrichten
                # KORREKTUR: Wir fügen mark_seen=False hinzu
                message_generator = mailbox.fetch(A(seen=False), mark_seen=False, reverse=True)
                
                # 2. Nutze islice für effizientes Paging
                paginated_messages = islice(message_generator, offset, offset + limit)
                
                for msg in paginated_messages:
                    emails.append({
                        "uid": msg.uid,
                        "subject": msg.subject,
                        "from": msg.from_,
                        "date": msg.date_str,
                        "text": msg.text or msg.html
                    })
        except Exception as e:
            print(f"Fehler beim Abrufen der E-Mails: {e}")
            return []
            
        return emails
        
    def mark_as_read(self, mail_uid: str, folder: str = "INBOX"):
        with MailBox(self.host).login(self.user, self.password, initial_folder=folder) as mailbox:
            mailbox.flag(mail_uid, '\\Seen', True)
    
    def move_email(self, mail_uid: str, destination_folder: str, source_folder: str = "INBOX"):
        with MailBox(self.host).login(self.user, self.password, initial_folder=source_folder) as mailbox:
            mailbox.move(mail_uid, destination_folder)