"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { CrawlJob } from "@/types";

export default function JobCard({ job }: { job: CrawlJob }) {
  const getStatusColor = () => {
    switch (job.status) {
      case "pending": return "#fbbf24";
      case "running": return "#06d6a0";
      case "completed": return "#3b82f6";
      case "failed": return "#ef4444";
      default: return "#94a3b8";
    }
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="glass-card"
      style={{ padding: "20px", display: "flex", flexDirection: "column", gap: 16 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ overflow: "hidden" }}>
          <p
            style={{
              fontSize: 12,
              color: "var(--text-muted)",
              margin: "0 0 4px 0",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            Job #{job.id}
          </p>
          <h3
            style={{
              fontSize: 16,
              fontWeight: 600,
              margin: 0,
              color: "var(--text-primary)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
            title={job.url}
          >
            {job.url.replace(/^https?:\/\//, "")}
          </h3>
        </div>
        <span className={`badge badge-${job.status}`}>
          {job.status === "running" && (
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: "currentColor",
                display: "inline-block",
                boxShadow: "0 0 8px currentColor",
              }}
              className="pulse-glow"
            />
          )}
          {job.status}
        </span>
      </div>

      <div style={{ display: "flex", gap: 24 }}>
        <div>
          <p style={{ fontSize: 20, fontWeight: 700, margin: 0, color: getStatusColor() }}>
            {job.total_faculty_found}
          </p>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: 0 }}>Faculty Found</p>
        </div>
        <div>
          <p style={{ fontSize: 20, fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
            {job.pages_crawled} <span style={{ fontSize: 14, color: "var(--text-muted)", fontWeight: 500 }}>/ {job.max_pages}</span>
          </p>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: 0 }}>Pages Crawled</p>
        </div>
      </div>

      {job.status === "running" && (
        <div style={{ marginTop: 4 }}>
          <div className="progress-track" style={{ height: 4 }}>
            <div
              className="progress-fill"
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      )}

      <div style={{ marginTop: "auto", paddingTop: 8 }}>
        <Link
          href={`/jobs/${job.id}`}
          style={{
            display: "block",
            textAlign: "center",
            padding: "10px",
            background: "rgba(15, 23, 55, 0.8)",
            borderRadius: 8,
            color: "var(--text-primary)",
            textDecoration: "none",
            fontSize: 14,
            fontWeight: 500,
            transition: "all 0.2s",
            border: "1px solid var(--border-color)",
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = "rgba(6, 214, 160, 0.1)";
            e.currentTarget.style.borderColor = "rgba(6, 214, 160, 0.3)";
            e.currentTarget.style.color = "#06d6a0";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = "rgba(15, 23, 55, 0.8)";
            e.currentTarget.style.borderColor = "var(--border-color)";
            e.currentTarget.style.color = "var(--text-primary)";
          }}
        >
          View Details →
        </Link>
      </div>
    </motion.div>
  );
}
