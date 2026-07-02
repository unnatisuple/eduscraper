"""
Async web crawler — BFS crawl of university pages using httpx.
Respects robots.txt, deduplicates URLs, configurable limits.
"""

import asyncio
import re
import logging
from datetime import datetime, timezone
from typing import Set, List, Optional
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from models import CrawlJob, FacultyContact, ExtractedItem
from extractor import FacultyExtractor, EMAIL_PATTERN, PHONE_PATTERNS

logger = logging.getLogger("eduscraper.crawler")


class AsyncCrawler:
    """
    BFS async crawler that processes university pages and extracts
    faculty contact info in real-time.
    """

    def __init__(
        self,
        job_id: int,
        start_url: str,
        max_pages: int = 50,
        crawl_delay: float = 1.0,
    ):
        self.job_id = job_id
        self.start_url = start_url
        self.max_pages = max_pages
        self.crawl_delay = crawl_delay

        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc.lower()
        self.scheme = parsed.scheme or "https"

        self.visited: Set[str] = set()
        self.queue: List[str] = [start_url]
        self.pages_crawled = 0
        self.total_faculty = 0

        try:
            ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            self.user_agent = ua.random
        except Exception:
            self.user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )

        self.robot_parser: Optional[RobotFileParser] = None

    async def _init_robots(self, client: httpx.AsyncClient):
        """Fetch and parse robots.txt."""
        robots_url = f"{self.scheme}://{self.base_domain}/robots.txt"
        try:
            resp = await client.get(robots_url, timeout=10)
            if resp.status_code == 200:
                self.robot_parser = RobotFileParser()
                self.robot_parser.parse(resp.text.splitlines())
                logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")

    def _can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if self.robot_parser is None:
            return True
        try:
            return self.robot_parser.can_fetch("*", url)
        except Exception:
            return True

    def _normalize_url(self, url: str) -> Optional[str]:
        """Normalize and validate a URL — only internal links."""
        url, _ = urldefrag(url)
        url = url.rstrip("/")

        if not url:
            return None

        parsed = urlparse(url)
        if not parsed.netloc:
            return None

        if parsed.netloc.lower() != self.base_domain:
            return None

        # Skip non-HTML resources
        skip_exts = {
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", ".webp",
            ".mp3", ".mp4", ".avi", ".mov", ".zip", ".rar", ".tar",
            ".gz", ".css", ".js", ".woff", ".woff2", ".ttf", ".eot",
        }
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in skip_exts):
            return None

        return url

    def _extract_links(self, html: str, page_url: str) -> List[str]:
        """Extract and normalize all internal links from a page."""
        soup = BeautifulSoup(html, "lxml")
        links = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute = urljoin(page_url, href)
            normalized = self._normalize_url(absolute)
            if normalized and normalized not in self.visited:
                links.append(normalized)
        return links

    async def _update_progress(self):
        """Update crawl job progress in the database."""
        progress = min(100.0, (self.pages_crawled / self.max_pages) * 100)
        async with async_session() as session:
            await session.execute(
                update(CrawlJob)
                .where(CrawlJob.id == self.job_id)
                .values(
                    progress=round(progress, 1),
                    pages_crawled=self.pages_crawled,
                    total_faculty_found=self.total_faculty,
                )
            )
            await session.commit()

    async def _save_faculty(self, records, session: AsyncSession):
        """Save extracted faculty records to the database."""
        for record in records:
            faculty = FacultyContact(
                job_id=self.job_id,
                name=record.name,
                email=record.email,
                phone=record.phone,
                department=record.department,
                designation=record.designation,
                source_url=record.source_url,
            )
            session.add(faculty)

            # Also save as extracted items for the results endpoint
            if record.email:
                session.add(ExtractedItem(
                    job_id=self.job_id,
                    type="email",
                    value=record.email,
                    metadata_={"name": record.name, "department": record.department},
                    source_url=record.source_url,
                ))
            if record.phone:
                session.add(ExtractedItem(
                    job_id=self.job_id,
                    type="phone",
                    value=record.phone,
                    metadata_={"name": record.name, "department": record.department},
                    source_url=record.source_url,
                ))
            if record.name:
                session.add(ExtractedItem(
                    job_id=self.job_id,
                    type="name",
                    value=record.name,
                    metadata_={"email": record.email, "designation": record.designation},
                    source_url=record.source_url,
                ))

        await session.commit()

        # Update FTS index
        for record in records:
            if record.email:
                try:
                    from sqlalchemy import text
                    await session.execute(
                        text(
                            "INSERT INTO faculty_fts(rowid, name, email, department, designation) "
                            "SELECT id, name, email, department, designation "
                            "FROM faculty_contacts WHERE email = :email AND job_id = :job_id "
                            "ORDER BY id DESC LIMIT 1"
                        ),
                        {"email": record.email, "job_id": self.job_id},
                    )
                except Exception:
                    pass  # FTS update is best-effort
            await session.commit()

    async def crawl(self):
        """Main crawl loop — BFS with delay and progress tracking."""
        logger.info(f"Starting crawl job {self.job_id}: {self.start_url} (max {self.max_pages} pages)")

        # Mark job as running
        async with async_session() as session:
            await session.execute(
                update(CrawlJob)
                .where(CrawlJob.id == self.job_id)
                .values(status="running")
            )
            await session.commit()

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        try:
            async with httpx.AsyncClient(
                headers=headers,
                follow_redirects=True,
                timeout=httpx.Timeout(30.0),
                verify=False,
            ) as client:
                await self._init_robots(client)

                while self.queue and self.pages_crawled < self.max_pages:
                    url = self.queue.pop(0)

                    if url in self.visited:
                        continue
                    if not self._can_fetch(url):
                        logger.info(f"Blocked by robots.txt: {url}")
                        continue

                    self.visited.add(url)

                    try:
                        logger.info(f"Crawling [{self.pages_crawled + 1}/{self.max_pages}]: {url}")
                        response = await client.get(url)

                        if response.status_code != 200:
                            logger.warning(f"HTTP {response.status_code}: {url}")
                            continue

                        content_type = response.headers.get("content-type", "")
                        if "text/html" not in content_type and "application/xhtml" not in content_type:
                            continue

                        html = response.text
                        self.pages_crawled += 1

                        # Extract links for BFS
                        new_links = self._extract_links(html, url)
                        self.queue.extend(new_links)

                        # Extract faculty contacts
                        extractor = FacultyExtractor(html, url)
                        records = extractor.extract_all()

                        if records:
                            self.total_faculty += len(records)
                            async with async_session() as session:
                                await self._save_faculty(records, session)
                            logger.info(f"  → Found {len(records)} faculty contacts")

                        # Update progress
                        await self._update_progress()

                        # Crawl delay
                        await asyncio.sleep(self.crawl_delay)

                    except httpx.TimeoutException:
                        logger.warning(f"Timeout: {url}")
                    except Exception as e:
                        logger.error(f"Error crawling {url}: {e}")

            # Mark job completed
            async with async_session() as session:
                await session.execute(
                    update(CrawlJob)
                    .where(CrawlJob.id == self.job_id)
                    .values(
                        status="completed",
                        progress=100.0,
                        pages_crawled=self.pages_crawled,
                        total_faculty_found=self.total_faculty,
                        completed_at=datetime.now(timezone.utc),
                    )
                )
                await session.commit()
            logger.info(f"Crawl job {self.job_id} completed: {self.pages_crawled} pages, {self.total_faculty} faculty")

        except Exception as e:
            logger.error(f"Crawl job {self.job_id} failed: {e}")
            async with async_session() as session:
                await session.execute(
                    update(CrawlJob)
                    .where(CrawlJob.id == self.job_id)
                    .values(
                        status="failed",
                        error_message=str(e)[:500],
                    )
                )
                await session.commit()
