from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    MONGO_PASS: str
    VERSION: str = "1.0.0"
    APP_MODE: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    OWNER_ROLE_ID: str
    MEMBER_ROLE_ID: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=False,        
        extra="ignore"  
    )
settings = Settings()