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
        self.mailbox = None

    def connect(self):
        self.mailbox = MailBox(self.host)
        self.mailbox.login(self.user, self.password)

    def fetch_unread_emails(self, folder: str = "INBOX", limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Ruft eine Seite von ungelesenen E-Mails ab.
        Dieser Ansatz ist effizienter und stabiler.
        """
        self.connect()
        self.mailbox.folder.set(folder)
        
        emails = []
        
        # 1. Erstelle einen Generator, der die ungelesenen Nachrichten findet.
        #    'reverse=True' ist gute Praxis, um die neuesten E-Mails zuerst zu bekommen.
        #    Es werden hier noch KEINE E-Mail-Inhalte heruntergeladen.
        message_generator = self.mailbox.fetch(A(seen=False), reverse=True)
        
        # 2. Nutze itertools.islice, um effizient eine "Seite" vom Generator zu nehmen.
        #    Dies ist der empfohlene Weg für Paging auf Iteratoren.
        #    Erst hier werden die E-Mails für die aktuelle Seite tatsächlich geholt.
        try:
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
            # Fängt mögliche Fehler bei der Kommunikation mit dem Server ab
            print(f"Fehler beim Abrufen der E-Mails: {e}")
            # Man könnte hier spezifischere Fehlerbehandlung einbauen
            return []
            
        return emails
        
    def mark_as_read(self, mail_uid: str, folder: str = "INBOX"):
        """Markiert eine einzelne E-Mail als gelesen."""
        self.connect()
        self.mailbox.folder.set(folder)
        self.mailbox.flag(mail_uid, '\\Seen', True)
    
    def move_email(self, mail_uid: str, destination_folder: str, source_folder: str = "INBOX"):
        self.connect()
        self.mailbox.folder.set(source_folder)
        self.mailbox.move(mail_uid, destination_folder)