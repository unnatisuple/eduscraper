"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { startCrawl } from "@/lib/api";

interface CrawlFormProps {
  onCrawlStarted: (jobId: number) => void;
}

export default function CrawlForm({ onCrawlStarted }: CrawlFormProps) {
  const [url, setUrl] = useState("");
  const [maxPages, setMaxPages] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError("");

    try {
      const result = await startCrawl(url.trim(), maxPages);
      onCrawlStarted(result.job_id);
      setUrl("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to start crawl";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="glass-card"
      style={{ padding: "36px", maxWidth: 720, margin: "0 auto" }}
    >
      <div style={{ marginBottom: 24 }}>
        <h2
          style={{
            fontSize: 20,
            fontWeight: 700,
            margin: "0 0 6px 0",
            color: "var(--text-primary)",
          }}
        >
          Start a New Crawl
        </h2>
        <p
          style={{
            fontSize: 14,
            color: "var(--text-secondary)",
            margin: 0,
          }}
        >
          Enter a university or college website URL to extract faculty contacts
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
          <div style={{ flex: 1 }}>
            <input
              id="crawl-url-input"
              type="text"
              className="input-glass"
              placeholder="https://cs.stanford.edu/people/faculty"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <motion.button
            type="submit"
            className="btn-gradient"
            disabled={loading || !url.trim()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={{ whiteSpace: "nowrap" }}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <motion.span
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  style={{ display: "inline-block" }}
                >
                  ⏳
                </motion.span>
                Starting...
              </span>
            ) : (
              "🔍 Start Crawl"
            )}
          </motion.button>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <label
            style={{
              fontSize: 13,
              color: "var(--text-secondary)",
              whiteSpace: "nowrap",
              fontWeight: 500,
            }}
          >
            Max Pages:
          </label>
          <input
            id="max-pages-slider"
            type="range"
            min={5}
            max={200}
            step={5}
            value={maxPages}
            onChange={(e) => setMaxPages(Number(e.target.value))}
            disabled={loading}
            style={{
              flex: 1,
              height: 4,
              borderRadius: 999,
              appearance: "none",
              background: "rgba(148, 163, 184, 0.2)",
              outline: "none",
              cursor: "pointer",
              accentColor: "#06d6a0",
            }}
          />
          <span
            style={{
              fontSize: 14,
              fontWeight: 600,
              color: "var(--accent-cyan)",
              minWidth: 32,
              textAlign: "right",
            }}
          >
            {maxPages}
          </span>
        </div>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              color: "#ef4444",
              fontSize: 13,
              marginTop: 12,
              padding: "8px 12px",
              background: "rgba(239, 68, 68, 0.1)",
              borderRadius: 8,
              border: "1px solid rgba(239, 68, 68, 0.2)",
            }}
          >
            {error}
          </motion.p>
        )}
      </form>
    </motion.div>
  );
}
