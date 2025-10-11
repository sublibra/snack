from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://snack_user:snack_password@localhost:5432/snack_db"
    
    # JWT Configuration
    secret_key: str = "your-super-secret-jwt-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # File Upload
    max_file_size: int = 10485760  # 10MB in bytes
    upload_dir: str = "./uploads"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"


settings = Settings()