from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
import os
from app.config import get_settings
from app.services.database import Database
from app.routes.diagnosis import router as diagnosis_router
from app.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await Database.connect(settings.mongodb_uri)
    yield
    await Database.disconnect()


app = FastAPI(
    title="AgroSentinel API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnosis_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Serve frontend static files in production
FRONTEND_BUILD = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_BUILD.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_BUILD / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve index.html for SPA routes
        file_path = FRONTEND_BUILD / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_BUILD / "index.html")
