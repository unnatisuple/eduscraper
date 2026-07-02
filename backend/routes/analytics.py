"""
Analytics routes — aggregated stats and chart-ready data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import CrawlJob, FacultyContact, ExtractedItem
from schemas import AnalyticsResponse

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics/{job_id}", response_model=AnalyticsResponse)
async def get_analytics(job_id: int, session: AsyncSession = Depends(get_session)):
    """Return aggregated stats and chart data for a crawl job."""
    # Check job exists
    result = await session.execute(select(CrawlJob).where(CrawlJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Total faculty
    total_result = await session.execute(
        select(func.count(FacultyContact.id)).where(FacultyContact.job_id == job_id)
    )
    total_faculty = total_result.scalar() or 0

    # Emails found
    emails_result = await session.execute(
        select(func.count(FacultyContact.id)).where(
            FacultyContact.job_id == job_id,
            FacultyContact.email.isnot(None),
            FacultyContact.email != "",
        )
    )
    total_emails = emails_result.scalar() or 0

    # Phones found
    phones_result = await session.execute(
        select(func.count(FacultyContact.id)).where(
            FacultyContact.job_id == job_id,
            FacultyContact.phone.isnot(None),
            FacultyContact.phone != "",
        )
    )
    total_phones = phones_result.scalar() or 0

    # Department distribution
    dept_result = await session.execute(
        select(FacultyContact.department, func.count(FacultyContact.id).label("count"))
        .where(
            FacultyContact.job_id == job_id,
            FacultyContact.department.isnot(None),
            FacultyContact.department != "",
        )
        .group_by(FacultyContact.department)
        .order_by(func.count(FacultyContact.id).desc())
        .limit(20)
    )
    departments = [{"name": row[0], "count": row[1]} for row in dept_result.fetchall()]

    # Designation distribution
    desig_result = await session.execute(
        select(FacultyContact.designation, func.count(FacultyContact.id).label("count"))
        .where(
            FacultyContact.job_id == job_id,
            FacultyContact.designation.isnot(None),
            FacultyContact.designation != "",
        )
        .group_by(FacultyContact.designation)
        .order_by(func.count(FacultyContact.id).desc())
        .limit(20)
    )
    designations = [{"name": row[0], "count": row[1]} for row in desig_result.fetchall()]

    return AnalyticsResponse(
        job_id=job_id,
        total_faculty=total_faculty,
        total_emails=total_emails,
        total_phones=total_phones,
        departments=departments,
        designations=designations,
        pages_crawled=job.pages_crawled,
    )
