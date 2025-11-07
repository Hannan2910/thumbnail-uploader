import asyncio
import aiomysql
from pydantic_settings import BaseSettings

class DbSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    class Config:
        env_file = ".env"

async def create_thumbnails_table():
    """Connects to MySQL and creates the 'thumbnails' table."""
    try:
        settings = DbSettings()
    except Exception as e:
        print(f"Error loading settings from .env file: {e}")
        return

    conn = None
    try:
        conn = await aiomysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            db=settings.DB_NAME
        )
        print("Successfully connected to the database.")

        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS thumbnails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_key VARCHAR(255) NOT NULL UNIQUE,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
            """)
        print("Table 'thumbnails' created successfully or already exists.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(create_thumbnails_table())