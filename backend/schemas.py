"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, HttpUrl


# ── Request schemas ──────────────────────────────────────────────

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 50


# ── Response schemas ─────────────────────────────────────────────

class CrawlJobResponse(BaseModel):
    id: int
    url: str
    status: str
    progress: float
    pages_crawled: int
    total_faculty_found: int
    max_pages: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FacultyContactResponse(BaseModel):
    id: int
    job_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractedItemResponse(BaseModel):
    id: int
    job_id: int
    type: str
    value: str
    metadata_: Optional[Any] = None
    source_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CrawlStartResponse(BaseModel):
    job_id: int
    message: str


class StatusResponse(BaseModel):
    job_id: int
    status: str
    progress: float
    pages_crawled: int
    total_faculty_found: int


class FacultyListResponse(BaseModel):
    job_id: int
    total: int
    faculty: List[FacultyContactResponse]


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[FacultyContactResponse]


class AnalyticsResponse(BaseModel):
    job_id: int
    total_faculty: int
    total_emails: int
    total_phones: int
    departments: List[dict]
    designations: List[dict]
    pages_crawled: int


class ResultsResponse(BaseModel):
    job_id: int
    emails: List[ExtractedItemResponse]
    phones: List[ExtractedItemResponse]
    names: List[ExtractedItemResponse]
