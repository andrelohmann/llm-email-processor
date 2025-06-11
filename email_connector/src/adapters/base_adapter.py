from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMailAdapter(ABC):

    @abstractmethod
    def fetch_unread_emails(self, folder: str = "INBOX", limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Ruft eine Seite von ungelesenen E-Mails ab."""
        pass

    @abstractmethod
    def mark_as_read(self, mail_uid: str, folder: str = "INBOX"):
        """Markiert eine E-Mail als gelesen."""
        pass

    @abstractmethod
    def move_email(self, mail_uid: str, destination_folder: str, source_folder: str = "INBOX"):
        """Verschiebt eine E-Mail in einen anderen Ordner."""
        pass