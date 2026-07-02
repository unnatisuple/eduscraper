"""
EduScraper — FastAPI entry point.
Run with: python main.py
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes.crawl import router as crawl_router
from routes.faculty import router as faculty_router
from routes.analytics import router as analytics_router
from routes.export import router as export_router

# ── Logging ──────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-20s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("eduscraper")

# ── App ──────────────────────────────────────────────────────────

app = FastAPI(
    title="EduScraper API",
    description="Intelligent Faculty Contact Extractor — crawls university websites and extracts faculty info.",
    version="1.0.0",
)

# CORS — allow frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(crawl_router)
app.include_router(faculty_router)
app.include_router(analytics_router)
app.include_router(export_router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    logger.info("🎓 EduScraper starting up...")
    await init_db()
    logger.info("✅ Database initialized (eduscraper.db)")
    logger.info("🚀 API ready at http://localhost:8000")
    logger.info("📖 Docs at http://localhost:8000/docs")


@app.get("/")
async def root():
    return {
        "app": "EduScraper",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
