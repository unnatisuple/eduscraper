"""
Faculty information extractor — 3-method smart extraction from HTML pages.

Method 1: Structured tags (faculty/staff/team class/id patterns)
Method 2: Email regex + surrounding context
Method 3: Phone regex + surrounding context
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from bs4 import BeautifulSoup, Tag


@dataclass
class FacultyRecord:
    """A single extracted faculty contact."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    source_url: Optional[str] = None

    def is_valid(self) -> bool:
        """At least an email or a name must be present."""
        return bool(self.email) or bool(self.name)

    def merge(self, other: "FacultyRecord"):
        """Merge another record into this one, filling blanks."""
        if not self.name and other.name:
            self.name = other.name
        if not self.email and other.email:
            self.email = other.email
        if not self.phone and other.phone:
            self.phone = other.phone
        if not self.department and other.department:
            self.department = other.department
        if not self.designation and other.designation:
            self.designation = other.designation


# ── Regex patterns ───────────────────────────────────────────────

EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
)

PHONE_PATTERNS = [
    re.compile(r'\+91[\s\-]?\d{5}[\s\-]?\d{5}'),
    re.compile(r'\(\d{3}\)\s?\d{3}[\-.\s]?\d{4}'),
    re.compile(r'\b\d{3}[\-.\s]\d{3}[\-.\s]\d{4}\b'),
    re.compile(r'\+\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}'),
    re.compile(r'\b\d{10}\b'),
]

FACULTY_KEYWORDS = [
    "faculty", "staff", "team", "people", "member",
    "professor", "doctor", "lecturer", "instructor",
    "directory", "personnel",
]

DEPARTMENT_KEYWORDS = [
    "department of", "dept. of", "dept of", "school of",
    "faculty of", "division of", "college of", "center for",
    "centre for", "institute of",
]

DESIGNATION_KEYWORDS = [
    "professor", "assistant professor", "associate professor",
    "asst. prof", "assoc. prof",
    "dr.", "ph.d", "phd", "hod", "head of department",
    "dean", "director", "lecturer", "senior lecturer",
    "instructor", "emeritus", "adjunct", "visiting",
    "chair", "coordinator",
]

# Emails to exclude (generic / non-faculty)
EXCLUDED_EMAIL_PATTERNS = [
    "noreply", "no-reply", "info@", "admin@", "webmaster@",
    "support@", "contact@", "help@", "office@", "hr@",
    "admissions@", "marketing@", "sales@", "press@",
    "media@", "feedback@", "enquiry@", "inquiry@",
]


def _is_excluded_email(email: str) -> bool:
    email_lower = email.lower()
    return any(pattern in email_lower for pattern in EXCLUDED_EMAIL_PATTERNS)


def _clean_text(text: str) -> str:
    """Normalize whitespace in extracted text."""
    return re.sub(r'\s+', ' ', text).strip()


def _extract_name_from_context(context: str) -> Optional[str]:
    """
    Try to extract a person's name from surrounding context.
    Looks for capitalized word sequences (2-4 words).
    """
    # Look for patterns like "Dr. John Smith" or "John A. Smith"
    name_patterns = [
        # Dr./Prof. FirstName LastName
        re.compile(r'(?:Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+){1,3})'),
        # Two or three capitalized words in a row (likely a name)
        re.compile(r'\b([A-Z][a-z]{1,20}(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]{1,20}){1,3})\b'),
    ]
    for pattern in name_patterns:
        match = pattern.search(context)
        if match:
            name = _clean_text(match.group(1) if match.lastindex else match.group(0))
            # Filter out common false positives
            lower = name.lower()
            if any(w in lower for w in [
                "university", "college", "department", "school",
                "faculty", "office", "building", "room", "phone",
                "email", "address", "contact", "click", "view",
                "read", "more", "page", "home", "about",
            ]):
                continue
            if len(name.split()) >= 2:
                return name[:200]
    return None


def _extract_department(context: str) -> Optional[str]:
    """Extract department from surrounding context."""
    context_lower = context.lower()
    for kw in DEPARTMENT_KEYWORDS:
        idx = context_lower.find(kw)
        if idx != -1:
            # Extract the phrase after the keyword
            start = idx
            # Find the end — stop at punctuation or newline
            rest = context[start:start + 150]
            # Take until newline, comma, pipe, <, or end
            match = re.match(r'([^\n<|,;]{10,120})', rest)
            if match:
                return _clean_text(match.group(1))[:256]
    return None


def _extract_designation(context: str) -> Optional[str]:
    """Extract designation/title from surrounding context."""
    context_lower = context.lower()
    best_match = None
    best_len = 0
    for kw in DESIGNATION_KEYWORDS:
        idx = context_lower.find(kw)
        if idx != -1:
            # Extract a reasonable chunk around the keyword
            start = max(0, idx)
            segment = context[start:start + 60]
            # Clean it
            match = re.match(r'([A-Za-z.\s]+)', segment)
            if match:
                designation = _clean_text(match.group(1))
                if len(designation) > best_len:
                    best_match = designation[:128]
                    best_len = len(designation)
    return best_match


def _extract_phone_from_context(context: str) -> Optional[str]:
    """Find a phone number in the given context string."""
    for pattern in PHONE_PATTERNS:
        match = pattern.search(context)
        if match:
            return _clean_text(match.group(0))
    return None


class FacultyExtractor:
    """
    Extracts faculty contact info from a single HTML page.
    Runs three methods and merges results by email.
    """

    def __init__(self, html: str, page_url: str):
        self.html = html
        self.page_url = page_url
        self.soup = BeautifulSoup(html, "lxml")
        self.full_text = self.soup.get_text(separator=" ", strip=True)
        self._records: Dict[str, FacultyRecord] = {}  # keyed by email
        self._no_email_records: List[FacultyRecord] = []

    def extract_all(self) -> List[FacultyRecord]:
        """Run all extraction methods and return merged results."""
        self._method1_structured_tags()
        self._method2_email_regex()
        self._method3_phone_regex()

        results = list(self._records.values())
        results.extend(self._no_email_records)
        return [r for r in results if r.is_valid()]

    def _add_record(self, record: FacultyRecord):
        """Add or merge a record, keyed by email."""
        if record.email:
            key = record.email.lower()
            if key in self._records:
                self._records[key].merge(record)
            else:
                self._records[key] = record
        elif record.name:
            # Check if we already have this name
            for existing in self._no_email_records:
                if existing.name and existing.name.lower() == record.name.lower():
                    existing.merge(record)
                    return
            self._no_email_records.append(record)

    # ── Method 1: Structured Tags ────────────────────────────────

    def _method1_structured_tags(self):
        """Look for elements with faculty-related classes/IDs."""
        candidates: List[Tag] = []

        for tag in self.soup.find_all(True):
            classes = " ".join(tag.get("class", []))
            tag_id = tag.get("id", "")
            combined = f"{classes} {tag_id}".lower()

            if any(kw in combined for kw in FACULTY_KEYWORDS):
                candidates.append(tag)

        for element in candidates:
            text = element.get_text(separator=" ", strip=True)
            if len(text) < 10:
                continue

            record = FacultyRecord(source_url=self.page_url)

            # Extract email
            email_match = EMAIL_PATTERN.search(text)
            if email_match and not _is_excluded_email(email_match.group(0)):
                record.email = email_match.group(0)

            # Extract name from headings inside element
            for heading in element.find_all(["h2", "h3", "h4", "h5", "strong", "b", "a"]):
                heading_text = heading.get_text(strip=True)
                if heading_text and 2 <= len(heading_text.split()) <= 5:
                    # Looks like a name
                    if not any(w in heading_text.lower() for w in [
                        "department", "contact", "email", "phone", "faculty", "staff",
                        "university", "college", "school", "office"
                    ]):
                        record.name = heading_text[:200]
                        break

            # Fallback name from context
            if not record.name:
                record.name = _extract_name_from_context(text)

            record.department = _extract_department(text)
            record.designation = _extract_designation(text)
            record.phone = _extract_phone_from_context(text)

            if record.is_valid():
                self._add_record(record)

    # ── Method 2: Email Regex ────────────────────────────────────

    def _method2_email_regex(self):
        """Find all emails and extract context from surrounding text."""
        for match in EMAIL_PATTERN.finditer(self.full_text):
            email = match.group(0)
            if _is_excluded_email(email):
                continue

            # Get surrounding context (±500 chars)
            start = max(0, match.start() - 500)
            end = min(len(self.full_text), match.end() + 500)
            context = self.full_text[start:end]

            record = FacultyRecord(
                email=email,
                source_url=self.page_url,
            )
            record.name = _extract_name_from_context(context)
            record.department = _extract_department(context)
            record.designation = _extract_designation(context)
            record.phone = _extract_phone_from_context(context)

            self._add_record(record)

    # ── Method 3: Phone Regex ────────────────────────────────────

    def _method3_phone_regex(self):
        """Find all phones and extract context from surrounding text."""
        seen_phones: Set[str] = set()

        for pattern in PHONE_PATTERNS:
            for match in pattern.finditer(self.full_text):
                phone = _clean_text(match.group(0))
                if phone in seen_phones:
                    continue
                seen_phones.add(phone)

                # Get surrounding context
                start = max(0, match.start() - 500)
                end = min(len(self.full_text), match.end() + 500)
                context = self.full_text[start:end]

                # Check if there is an email nearby — if so, skip (Method 2 handles it)
                if EMAIL_PATTERN.search(context):
                    continue

                record = FacultyRecord(
                    phone=phone,
                    source_url=self.page_url,
                )
                record.name = _extract_name_from_context(context)
                record.department = _extract_department(context)
                record.designation = _extract_designation(context)

                if record.name:
                    self._add_record(record)
