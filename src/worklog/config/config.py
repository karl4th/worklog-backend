from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    DB_HOST: str
    DB_PORT: int

    ANTHROPIC_API_KEY: str
    TELEGRAM_API_KEY: str
    WHATSAPP_API_KEY: str

    JWT_SECRET_KEY: str

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

    model_config = SettingsConfigDict(env_file=".env.dev")

settings = Settings()