from pydantic import ConfigDict
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly load .env
load_dotenv()

class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS:bool=False
    MAIL_SSL_TLS:bool=True
    USE_CREDENTIALS:bool=True
    VALIDATE_CERTS:bool=True
    TEMPLATE_FOLDER: Path=Path(__file__).parent.parent / 'services' / 'templates'

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

settings = Settings()
