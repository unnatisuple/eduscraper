"""
Faculty routes — retrieve and search faculty contacts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import CrawlJob, FacultyContact, ExtractedItem
from schemas import (
    FacultyListResponse, FacultyContactResponse,
    SearchResponse, ResultsResponse, ExtractedItemResponse,
)

router = APIRouter(prefix="/api", tags=["faculty"])


@router.get("/faculty/{job_id}", response_model=FacultyListResponse)
async def get_faculty(
    job_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    """Get all faculty contacts for a crawl job, with pagination."""
    # Check job exists
    result = await session.execute(select(CrawlJob).where(CrawlJob.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    # Count total
    count_result = await session.execute(
        select(func.count(FacultyContact.id)).where(FacultyContact.job_id == job_id)
    )
    total = count_result.scalar() or 0

    # Paginated query
    offset = (page - 1) * per_page
    result = await session.execute(
        select(FacultyContact)
        .where(FacultyContact.job_id == job_id)
        .order_by(FacultyContact.id)
        .offset(offset)
        .limit(per_page)
    )
    faculty = result.scalars().all()

    return FacultyListResponse(
        job_id=job_id,
        total=total,
        faculty=[FacultyContactResponse.model_validate(f) for f in faculty],
    )


@router.get("/results/{job_id}", response_model=ResultsResponse)
async def get_results(job_id: int, session: AsyncSession = Depends(get_session)):
    """Get all extracted items grouped by type."""
    result = await session.execute(select(CrawlJob).where(CrawlJob.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    all_items = await session.execute(
        select(ExtractedItem).where(ExtractedItem.job_id == job_id).order_by(ExtractedItem.id)
    )
    items = all_items.scalars().all()

    emails = [ExtractedItemResponse.model_validate(i) for i in items if i.type == "email"]
    phones = [ExtractedItemResponse.model_validate(i) for i in items if i.type == "phone"]
    names = [ExtractedItemResponse.model_validate(i) for i in items if i.type == "name"]

    return ResultsResponse(job_id=job_id, emails=emails, phones=phones, names=names)


@router.get("/search", response_model=SearchResponse)
async def search_faculty(
    q: str = Query(..., min_length=1),
    job_id: int = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Search faculty contacts using full-text search or LIKE fallback."""
    query_term = q.strip()

    try:
        # Try FTS5 first
        fts_query = f'"{query_term}"'
        if job_id:
            fts_sql = text(
                "SELECT fc.* FROM faculty_contacts fc "
                "JOIN faculty_fts ON fc.id = faculty_fts.rowid "
                "WHERE faculty_fts MATCH :query AND fc.job_id = :job_id "
                "LIMIT 100"
            )
            result = await session.execute(fts_sql, {"query": fts_query, "job_id": job_id})
        else:
            fts_sql = text(
                "SELECT fc.* FROM faculty_contacts fc "
                "JOIN faculty_fts ON fc.id = faculty_fts.rowid "
                "WHERE faculty_fts MATCH :query "
                "LIMIT 100"
            )
            result = await session.execute(fts_sql, {"query": fts_query})

        rows = result.fetchall()
        faculty = [
            FacultyContactResponse(
                id=r[0], job_id=r[1], name=r[2], email=r[3],
                phone=r[4], department=r[5], designation=r[6],
                source_url=r[7], created_at=r[8],
            )
            for r in rows
        ]
    except Exception:
        # Fallback to LIKE search
        like_term = f"%{query_term}%"
        stmt = select(FacultyContact).where(
            (FacultyContact.name.ilike(like_term)) |
            (FacultyContact.email.ilike(like_term)) |
            (FacultyContact.department.ilike(like_term)) |
            (FacultyContact.designation.ilike(like_term))
        )
        if job_id:
            stmt = stmt.where(FacultyContact.job_id == job_id)
        stmt = stmt.limit(100)

        result = await session.execute(stmt)
        rows = result.scalars().all()
        faculty = [FacultyContactResponse.model_validate(r) for r in rows]

    return SearchResponse(query=query_term, total=len(faculty), results=faculty)
