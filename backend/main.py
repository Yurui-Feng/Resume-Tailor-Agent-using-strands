"""
Resume Tailor API - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
import logging

from backend.config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    ALLOWED_ORIGINS, FRONTEND_DIR
)
from backend.api.routes import router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes FIRST (important for proper routing)
app.include_router(router)


# Mount frontend static files LAST (if directory exists)
# Note: Static files are mounted after API routes to ensure API routes take precedence
if FRONTEND_DIR.exists():
    # Use a more specific mount to avoid conflicts with /api routes
    from fastapi.responses import HTMLResponse
    import mimetypes

    @app.get("/")
    async def serve_index():
        """Serve the main index.html"""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return HTMLResponse(content=index_path.read_text(encoding='utf-8'))
        return RedirectResponse(url="/docs")

    # Mount static files for assets (js, css, etc)
    @app.get("/{file_path:path}")
    async def serve_static(file_path: str):
        """Serve static files, but not if they conflict with API routes"""
        # Skip if this is an API route
        if file_path.startswith("api/") or file_path.startswith("docs") or file_path.startswith("redoc"):
            raise HTTPException(status_code=404)

        static_file = FRONTEND_DIR / file_path
        if static_file.exists() and static_file.is_file():
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(static_file))
            return FileResponse(
                path=static_file,
                media_type=content_type
            )

        # If file not found and not an API route, serve index.html (for SPA routing)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return HTMLResponse(content=index_path.read_text(encoding='utf-8'))

        raise HTTPException(status_code=404, detail="File not found")

    logger.info(f"Frontend mounted from {FRONTEND_DIR}")
else:
    logger.warning(f"Frontend directory not found: {FRONTEND_DIR}")

    # If no frontend, redirect root to API docs
    @app.get("/")
    async def root():
        """Redirect to API documentation"""
        return RedirectResponse(url="/docs")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"🚀 {API_TITLE} v{API_VERSION} starting up...")
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    logger.info(f"🎨 Frontend: http://localhost:8000/")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"👋 {API_TITLE} shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
