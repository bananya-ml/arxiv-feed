from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Research Paper Processing API"
    API_VERSION: str = "1.0.0"
    CONTACT_NAME: str = "Your Name"
    CONTACT_EMAIL: str = "bhatnagarananya64@outlook.com"
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000"
    CORS_METHODS: str = "GET,POST,PUT,DELETE"
    CORS_HEADERS: str = "*"
    ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def cors_methods_list(self) -> List[str]:
        return [method.strip() for method in self.CORS_METHODS.split(",")]

    @property
    def cors_headers_list(self) -> List[str]:
        return [header.strip() for header in self.CORS_HEADERS.split(",")] if self.CORS_HEADERS != "*" else ["*"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()