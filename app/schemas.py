from pydantic import BaseModel

class ThumbnailResponse(BaseModel):
    file_key: str
    url: str