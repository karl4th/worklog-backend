from pydantic_settings import BaseSettings, SettingsConfigDict
import os



class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
    TELEGRAM_API_KEY: str = os.getenv("TELEGRAM_API_KEY")
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
    
    @property
    def GET_TELEGRAM_API_KEY(self):
        return self.TELEGRAM_API_KEY

    @property
    def GET_WHATSAPP_API_KEY(self):
        return self.WHATSAPP_API_KEY
    
    @property
    def GET_ANTHROPIC_API_KEY(self):
        return self.ANTHROPIC_API_KEY

    @property
    def GET_JWT_SECRET_KEY(self):
        return self.JWT_SECRET_KEY


settings = Settings()