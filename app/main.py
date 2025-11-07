from fastapi import FastAPI
from .database import startup, shutdown
from .routers import thumbnails

app = FastAPI(title="Image Upload API")

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

app.include_router(thumbnails.router, prefix="/api/v1", tags=["Thumbnails"])

@app.get("/health", tags=["Monitoring"])
def health_check():
    """A public endpoint to check if the API is running."""
    return {"status": "ok"}