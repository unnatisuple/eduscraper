"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Header from "@/components/Header";
import ProgressTracker from "@/components/ProgressTracker";
import FacultyTable from "@/components/FacultyTable";
import SearchBar from "@/components/SearchBar";
import AnalyticsChart from "@/components/AnalyticsChart";
import ExportMenu from "@/components/ExportMenu";
import StatsCard from "@/components/StatsCard";
import { getCrawlStatus, getFaculty, searchFaculty, getAnalytics } from "@/lib/api";
import type { StatusResponse, FacultyContact, AnalyticsData } from "@/types";

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = Number(params.id);

  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [faculty, setFaculty] = useState<FacultyContact[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  
  // Pagination (simplified for now)
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const loadData = async () => {
    try {
      const statusData = await getCrawlStatus(jobId);
      setStatus(statusData);

      if (searchQuery) {
        const searchData = await searchFaculty(searchQuery, jobId);
        setFaculty(searchData.results);
        setTotal(searchData.total);
      } else {
        const facultyData = await getFaculty(jobId, page, 100);
        setFaculty(facultyData.faculty);
        setTotal(facultyData.total);
      }

      if (statusData.status === "completed" || statusData.total_faculty_found > 0) {
        const analyticsData = await getAnalytics(jobId);
        setAnalytics(analyticsData);
      }
    } catch (err) {
      console.error("Failed to load job data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Poll data occasionally while running
    let interval: NodeJS.Timeout;
    if (status?.status === "running" || status?.status === "pending") {
       interval = setInterval(loadData, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId, page, searchQuery, status?.status]);


  if (loading && !status) {
    return (
      <>
        <Header />
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "50vh" }}>
          <p style={{ color: "var(--text-muted)" }}>Loading Job Details...</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <main style={{ padding: "40px", maxWidth: 1400, margin: "0 auto" }}>
        
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
          <div>
            <button 
              onClick={() => router.push('/')}
              style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", display: "flex", alignItems: "center", gap: 8, padding: 0, marginBottom: 12, fontSize: 14 }}
            >
              ← Back to Dashboard
            </button>
            <h1 style={{ fontSize: 32, fontWeight: 800, margin: 0 }}>Job Details <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>#{jobId}</span></h1>
          </div>
          
          <ExportMenu jobId={jobId} />
        </div>

        {status && (
          <div style={{ marginBottom: 40 }}>
            <ProgressTracker 
              jobId={jobId} 
              initialStatus={status.status} 
              onComplete={loadData}
            />
          </div>
        )}

        {analytics && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 24, marginBottom: 40 }}>
            <StatsCard label="Total Extracted" value={analytics.total_faculty} icon="👥" color="#06d6a0" />
            <StatsCard label="Emails Found" value={analytics.total_emails} icon="📧" color="#3b82f6" delay={0.1} />
            <StatsCard label="Phones Found" value={analytics.total_phones} icon="📱" color="#8b5cf6" delay={0.2} />
            <StatsCard label="Pages Crawled" value={analytics.pages_crawled} icon="📄" color="#ec4899" delay={0.3} />
          </div>
        )}

        {analytics && (
           <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: 24, marginBottom: 40 }}>
             <AnalyticsChart data={analytics.departments} type="pie" title="Department Distribution" />
             <AnalyticsChart data={analytics.designations} type="bar" title="Top Designations" />
           </div>
        )}

        <div className="glass-card" style={{ padding: "24px" }}>
           <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, flexWrap: "wrap", gap: 16 }}>
             <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Extracted Contacts ({total})</h2>
             <SearchBar onSearch={setSearchQuery} />
           </div>
           
           <FacultyTable faculty={faculty} />
           
           {/* Simple pagination controls */}
           {total > 100 && !searchQuery && (
             <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 24 }}>
               <button 
                  disabled={page === 1} 
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  className="btn-gradient"
                  style={{ opacity: page === 1 ? 0.5 : 1, padding: "8px 16px" }}
                >
                  Previous
                </button>
                <span style={{ display: "flex", alignItems: "center", color: "var(--text-muted)" }}>Page {page}</span>
                <button 
                  disabled={faculty.length < 100} 
                  onClick={() => setPage(p => p + 1)}
                  className="btn-gradient"
                  style={{ opacity: faculty.length < 100 ? 0.5 : 1, padding: "8px 16px" }}
                >
                  Next
                </button>
             </div>
           )}
        </div>
      </main>
    </>
  );
}
