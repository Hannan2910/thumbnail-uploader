import aiomysql
from .config import settings

DB_POOL: aiomysql.Pool = None

async def startup():
    """Initializes the aiomysql database connection pool."""
    global DB_POOL
    DB_POOL = await aiomysql.create_pool(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        db=settings.DB_NAME,
        autocommit=True
    )

async def shutdown():
    """Closes the database connection pool."""
    DB_POOL.close()
    await DB_POOL.wait_closed()

def get_db_pool() -> aiomysql.Pool:
    """Dependency to get the database pool."""
    return DB_POOL