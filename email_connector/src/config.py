from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mail_provider: str = "imap"
    mail_imap_host: str
    mail_user: str
    mail_password: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Erstelle eine globale Instanz, die in der App importiert werden kann
settings = Settings()