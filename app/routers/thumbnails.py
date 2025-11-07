import uuid
from typing import List

import aiomysql
import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import (APIRouter, BackgroundTasks, Depends, File, HTTPException,
                     Query, UploadFile, status)

from ..config import settings
from ..database import get_db_pool
from ..dependencies import get_api_key
from ..schemas import ThumbnailResponse

router = APIRouter()

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.CLOUDFLARE_R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
    region_name="auto",
)

async def upload_to_r2_and_update_db(content: bytes, file_key: str, pool: aiomysql.Pool):
    """Background task to upload file to R2 and update the MySQL database."""
    try:
        s3_client.put_object(
            Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME, Key=file_key, Body=content
        )
    except NoCredentialsError:
        print("Error: S3 credentials not available.")
        return

    url = f"{settings.CLOUDFLARE_R2_PUBLIC_URL}/{file_key}"
    
    # MySQL-specific INSERT...ON DUPLICATE KEY UPDATE statement
    sql = """
        INSERT INTO thumbnails (file_key, url) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE url = VALUES(url), updated_at = CURRENT_TIMESTAMP;
    """
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, (file_key, url))

@router.post(
    "/upload-thumbnails",
    response_model=List[ThumbnailResponse],
    dependencies=[Depends(get_api_key)]
)
async def upload_thumbnails(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    pool: aiomysql.Pool = Depends(get_db_pool),
):
    uploaded_files = []
    for file in files:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.content_type}. Must be JPEG, PNG, or WebP.",
            )

        file_extension = file.filename.split(".")[-1]
        file_key = f"uploads/{uuid.uuid4()}.{file_extension}"
        content = await file.read()

        background_tasks.add_task(upload_to_r2_and_update_db, content, file_key, pool)
        
        url = f"{settings.CLOUDFLARE_R2_PUBLIC_URL}/{file_key}"
        uploaded_files.append({"file_key": file_key, "url": url})

    return uploaded_files

@router.get("/get-thumbnails", response_model=List[ThumbnailResponse], dependencies=[Depends(get_api_key)])
async def get_thumbnails(
    pool: aiomysql.Pool = Depends(get_db_pool),
    page: int = Query(1, ge=1, description="The page number to retrieve"),
    page_size: int = Query(10, ge=1, le=100, description="The number of records per page"),
):
    limit = page_size
    offset = (page - 1) * page_size
    
    query = "SELECT file_key, url FROM thumbnails ORDER BY created_at DESC LIMIT %s OFFSET %s"
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (limit, offset))
            rows = await cursor.fetchall()
            return rows