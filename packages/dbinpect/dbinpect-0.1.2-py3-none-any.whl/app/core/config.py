from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis les variables d'environnement."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_file_search_paths=[
            Path.cwd(),
            Path.cwd().parent,
            Path.home(),
        ],
    )
    
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="URL de connexion à la base de données (ex: postgresql://user:pass@host:port/db)"
    )
    
    # Support pour différents types de bases de données
    DB_TYPE: Optional[str] = Field(
        default=None,
        description="Type de base de données (postgresql, mysql, sqlite, etc.)"
    )
    
    # Variables séparées pour plus de flexibilité
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    def get_database_url(self) -> str:
        """
        Construit l'URL de la base de données.
        Priorité: DATABASE_URL > variables séparées > SQLite par défaut
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Si des variables séparées sont fournies, construire l'URL
        if all([self.DB_HOST, self.DB_USER, self.DB_NAME]):
            db_type = self.DB_TYPE or "postgresql"
            port = f":{self.DB_PORT}" if self.DB_PORT else ""
            password = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
            return f"{db_type}://{self.DB_USER}{password}@{self.DB_HOST}{port}/{self.DB_NAME}"
        
        # Par défaut, utiliser SQLite en mémoire pour les tests
        return "sqlite:///:memory:"


# Instance globale des settings
settings = Settings()

