import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api import auth, chats, media, websocket
from app.db.database import engine
from app.models.models import Base


# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="Snack Chat Service",
    description="A self-hosted chat service with end-to-end encryption",
    version="1.0.0",
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(chats.router, prefix="/api/v1", tags=["chats"])
app.include_router(media.router, prefix="/api/v1", tags=["media"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    # In production, use Alembic migrations instead
    # Base.metadata.create_all(bind=engine)
    pass


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Snack Chat Service",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )