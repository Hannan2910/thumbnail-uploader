from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MySQL Settings
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # API and Cloudflare Settings
    SECRET_API_KEY: str
    CLOUDFLARE_R2_ACCOUNT_ID: str
    CLOUDFLARE_R2_ACCESS_KEY_ID: str
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: str
    CLOUDFLARE_R2_BUCKET_NAME: str
    CLOUDFLARE_R2_PUBLIC_URL: str

    class Config:
        env_file = ".env"

settings = Settings()