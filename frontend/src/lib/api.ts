/* ── API client — all calls to the FastAPI backend ── */

import axios from "axios";
import type {
  CrawlJob,
  CrawlStartResponse,
  StatusResponse,
  FacultyListResponse,
  SearchResponse,
  AnalyticsData,
  ResultsResponse,
} from "@/types";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 30000,
});

/* ── Crawl ────────────────────────────────────────────────────── */

export async function startCrawl(url: string, maxPages: number = 50): Promise<CrawlStartResponse> {
  const { data } = await api.post<CrawlStartResponse>("/api/crawl", {
    url,
    max_pages: maxPages,
  });
  return data;
}

export async function getCrawlStatus(jobId: number): Promise<StatusResponse> {
  const { data } = await api.get<StatusResponse>(`/api/status/${jobId}`);
  return data;
}

export async function listJobs(): Promise<CrawlJob[]> {
  const { data } = await api.get<CrawlJob[]>("/api/jobs");
  return data;
}

/* ── Faculty ──────────────────────────────────────────────────── */

export async function getFaculty(jobId: number, page = 1, perPage = 50): Promise<FacultyListResponse> {
  const { data } = await api.get<FacultyListResponse>(`/api/faculty/${jobId}`, {
    params: { page, per_page: perPage },
  });
  return data;
}

export async function searchFaculty(query: string, jobId?: number): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>("/api/search", {
    params: { q: query, ...(jobId ? { job_id: jobId } : {}) },
  });
  return data;
}

/* ── Analytics ────────────────────────────────────────────────── */

export async function getAnalytics(jobId: number): Promise<AnalyticsData> {
  const { data } = await api.get<AnalyticsData>(`/api/analytics/${jobId}`);
  return data;
}

/* ── Results ──────────────────────────────────────────────────── */

export async function getResults(jobId: number): Promise<ResultsResponse> {
  const { data } = await api.get<ResultsResponse>(`/api/results/${jobId}`);
  return data;
}

/* ── Export ────────────────────────────────────────────────────── */

export function getExportUrl(jobId: number, format: "csv" | "xlsx" | "json" | "pdf"): string {
  return `http://localhost:8000/api/export/${jobId}?format=${format}`;
}
