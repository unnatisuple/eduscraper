"""
SQLAlchemy ORM models for EduScraper.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
)
from database import Base


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    progress = Column(Float, nullable=False, default=0.0)
    pages_crawled = Column(Integer, nullable=False, default=0)
    total_faculty_found = Column(Integer, nullable=False, default=0)
    max_pages = Column(Integer, nullable=False, default=50)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class FacultyContact(Base):
    __tablename__ = "faculty_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("crawl_jobs.id"), nullable=False, index=True)
    name = Column(String(512), nullable=True)
    email = Column(String(512), nullable=True)
    phone = Column(String(64), nullable=True)
    department = Column(String(512), nullable=True)
    designation = Column(String(256), nullable=True)
    source_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class ExtractedItem(Base):
    __tablename__ = "extracted_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("crawl_jobs.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # email, phone, name
    value = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    source_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
