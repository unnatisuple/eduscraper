"use client";

import { useState } from "react";
import { getExportUrl } from "@/lib/api";

interface ExportMenuProps {
  jobId: number;
}

export default function ExportMenu({ jobId }: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="export-menu">
      <button
        className="btn-gradient"
        onClick={() => setIsOpen(!isOpen)}
        style={{ padding: "8px 16px", fontSize: 14 }}
      >
        📥 Export Results
      </button>
      
      {isOpen && (
        <div className="export-dropdown">
          <a href={getExportUrl(jobId, "csv")} className="export-item" download>
            <span>📊</span> CSV File
          </a>
          <a href={getExportUrl(jobId, "xlsx")} className="export-item" download>
            <span>📈</span> Excel (XLSX)
          </a>
          <a href={getExportUrl(jobId, "json")} className="export-item" download>
            <span>'{ }'</span> JSON Data
          </a>
          <a href={getExportUrl(jobId, "pdf")} className="export-item" download>
            <span>📄</span> PDF Report
          </a>
        </div>
      )}
    </div>
  );
}
