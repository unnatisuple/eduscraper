"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getCrawlStatus } from "@/lib/api";
import type { StatusResponse } from "@/types";

interface ProgressTrackerProps {
  jobId: number;
  initialStatus: string;
  onComplete?: () => void;
}

export default function ProgressTracker({ jobId, initialStatus, onComplete }: ProgressTrackerProps) {
  const [status, setStatus] = useState<StatusResponse | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      try {
        const data = await getCrawlStatus(jobId);
        setStatus(data);
        if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval);
          if (data.status === "completed" && onComplete) {
            onComplete();
          }
        }
      } catch (err) {
        console.error("Failed to fetch status:", err);
      }
    };

    fetchStatus();

    if (initialStatus === "pending" || initialStatus === "running") {
      interval = setInterval(fetchStatus, 2000);
    }

    return () => clearInterval(interval);
  }, [jobId, initialStatus, onComplete]);

  if (!status) return null;

  return (
    <div className="glass-card" style={{ padding: "24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: "0 0 4px 0", fontSize: 18, fontWeight: 600 }}>Crawl Progress</h3>
          <p style={{ margin: 0, fontSize: 14, color: "var(--text-secondary)" }}>
            Job #{jobId}
          </p>
        </div>
        <span className={`badge badge-${status.status}`}>
          {status.status}
        </span>
      </div>

      <div className="progress-track" style={{ marginBottom: 16 }}>
        <div
          className="progress-fill"
          style={{ width: `${status.progress}%` }}
        />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, color: "var(--text-secondary)" }}>
        <span>Pages: {status.pages_crawled}</span>
        <span>Faculty Found: <strong style={{ color: "var(--accent-cyan)" }}>{status.total_faculty_found}</strong></span>
        <span>{status.progress.toFixed(1)}%</span>
      </div>
    </div>
  );
}
