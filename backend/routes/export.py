"""
Export routes — download crawl results as CSV, XLSX, JSON, or PDF.
"""

import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import pandas as pd
from fpdf import FPDF

from database import get_session
from models import CrawlJob, FacultyContact

router = APIRouter(prefix="/api", tags=["export"])


async def _get_faculty_df(job_id: int, session: AsyncSession) -> pd.DataFrame:
    """Load faculty contacts as a pandas DataFrame."""
    result = await session.execute(
        select(FacultyContact)
        .where(FacultyContact.job_id == job_id)
        .order_by(FacultyContact.id)
    )
    contacts = result.scalars().all()

    data = []
    for c in contacts:
        data.append({
            "Name": c.name or "",
            "Email": c.email or "",
            "Phone": c.phone or "",
            "Department": c.department or "",
            "Designation": c.designation or "",
            "Source URL": c.source_url or "",
        })

    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["Name", "Email", "Phone", "Department", "Designation", "Source URL"]
    )


@router.get("/export/{job_id}")
async def export_data(
    job_id: int,
    format: str = Query("csv", regex="^(csv|xlsx|json|pdf)$"),
    session: AsyncSession = Depends(get_session),
):
    """Export faculty contacts in the requested format."""
    # Check job exists
    result = await session.execute(select(CrawlJob).where(CrawlJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    df = await _get_faculty_df(job_id, session)
    filename_base = f"eduscraper_job_{job_id}"

    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"},
        )

    elif format == "xlsx":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Faculty Contacts")
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.xlsx"},
        )

    elif format == "json":
        data = df.to_dict(orient="records")
        json_str = json.dumps(data, indent=2, default=str)
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.json"},
        )

    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page(orientation="L")
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"EduScraper - Faculty Contacts (Job #{job_id})", ln=True, align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"Source: {job.url}", ln=True, align="C")
        pdf.cell(0, 6, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
        pdf.ln(5)

        # Table header
        cols = ["Name", "Email", "Phone", "Department", "Designation"]
        col_widths = [55, 65, 40, 55, 55]

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(41, 50, 80)
        pdf.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            pdf.cell(col_widths[i], 7, col, border=1, fill=True, align="C")
        pdf.ln()

        # Table rows
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(0, 0, 0)
        for _, row in df.iterrows():
            max_height = 7
            for i, col in enumerate(cols):
                value = str(row.get(col, ""))[:40]
                pdf.cell(col_widths[i], max_height, value, border=1)
            pdf.ln()

        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.pdf"},
        )
