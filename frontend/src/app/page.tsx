"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Header from "@/components/Header";
import CrawlForm from "@/components/CrawlForm";
import JobCard from "@/components/JobCard";
import StatsCard from "@/components/StatsCard";
import { listJobs } from "@/lib/api";
import type { CrawlJob } from "@/types";

export default function Home() {
  const router = useRouter();
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = async () => {
    try {
      const data = await listJobs();
      setJobs(data);
    } catch (err) {
      console.error("Failed to load jobs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCrawlStarted = (jobId: number) => {
    router.push(`/jobs/${jobId}`);
  };

  // Calculate quick stats
  const totalFacultyFound = jobs.reduce((sum, job) => sum + job.total_faculty_found, 0);
  const totalJobsCompleted = jobs.filter(j => j.status === 'completed').length;
  const activeJobs = jobs.filter(j => j.status === 'running').length;

  return (
    <>
      <Header />
      
      <main style={{ padding: "40px", maxWidth: 1200, margin: "0 auto" }}>
        
        {/* Hero Section */}
        <div style={{ textAlign: "center", marginBottom: 60, marginTop: 40 }}>
          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
            style={{ fontSize: 48, fontWeight: 900, marginBottom: 16, letterSpacing: "-0.03em" }}
          >
            Uncover <span className="gradient-text">Academic Connections</span>
          </motion.h1>
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            style={{ fontSize: 18, color: "var(--text-secondary)", maxWidth: 600, margin: "0 auto" }}
          >
            Intelligently crawl university directories to extract faculty names, emails, phones, and departments.
          </motion.p>
        </div>

        <CrawlForm onCrawlStarted={handleCrawlStarted} />

        {/* Quick Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 24, marginTop: 60, marginBottom: 60 }}>
          <StatsCard label="Total Faculty Found" value={totalFacultyFound} icon="👥" color="#06d6a0" delay={0.3} />
          <StatsCard label="Successful Crawls" value={totalJobsCompleted} icon="✅" color="#3b82f6" delay={0.4} />
          <StatsCard label="Active Crawls" value={activeJobs} icon="🚀" color="#8b5cf6" delay={0.5} />
        </div>

        {/* Recent Jobs */}
        <div>
          <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24, display: "flex", alignItems: "center", gap: 12 }}>
            Recent Crawl Jobs
            {loading && <span style={{ fontSize: 14, color: "var(--text-muted)", fontWeight: 500 }}>Loading...</span>}
          </h2>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 24 }}>
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
            {!loading && jobs.length === 0 && (
              <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: 60, background: "rgba(15,23,55,0.4)", borderRadius: 16, border: "1px dashed var(--border-color)" }}>
                <p style={{ fontSize: 18, color: "var(--text-muted)", margin: 0 }}>No crawl jobs yet. Start one above!</p>
              </div>
            )}
          </div>
        </div>

      </main>
    </>
  );
}
