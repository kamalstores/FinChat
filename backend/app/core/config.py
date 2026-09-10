from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "super_secret_key"
    ALGORITHM: str = "HS256"
    BASE_URL: str
    
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    PINECONE_HOST: str
    PINECONE_INDEX_HOST: str
    PINECONE_INDEX_NAME: str
    PINECONE_API_KEY: str
    
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    class Config:
        env_file = ".env.local"
        
    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def POSTGRES_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()