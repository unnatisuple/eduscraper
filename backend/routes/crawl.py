"""
Crawl routes — start crawls and check progress.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import CrawlJob
from schemas import CrawlRequest, CrawlStartResponse, StatusResponse, CrawlJobResponse
from crawler import AsyncCrawler

router = APIRouter(prefix="/api", tags=["crawl"])


@router.post("/crawl", response_model=CrawlStartResponse)
async def start_crawl(req: CrawlRequest, session: AsyncSession = Depends(get_session)):
    """Start a new crawl job."""
    # Validate URL
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Create job record
    job = CrawlJob(
        url=url,
        status="pending",
        max_pages=min(req.max_pages, 200),  # Hard cap at 200
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Launch crawler as background task
    crawler = AsyncCrawler(
        job_id=job.id,
        start_url=url,
        max_pages=job.max_pages,
    )
    asyncio.create_task(crawler.crawl())

    return CrawlStartResponse(
        job_id=job.id,
        message=f"Crawl started for {url} (max {job.max_pages} pages)",
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: int, session: AsyncSession = Depends(get_session)):
    """Get crawl job progress."""
    result = await session.execute(select(CrawlJob).where(CrawlJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return StatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        pages_crawled=job.pages_crawled,
        total_faculty_found=job.total_faculty_found,
    )


@router.get("/jobs", response_model=list[CrawlJobResponse])
async def list_jobs(session: AsyncSession = Depends(get_session)):
    """List all crawl jobs, most recent first."""
    result = await session.execute(
        select(CrawlJob).order_by(CrawlJob.created_at.desc()).limit(50)
    )
    jobs = result.scalars().all()
    return [CrawlJobResponse.model_validate(j) for j in jobs]
