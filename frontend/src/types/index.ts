/* ── TypeScript interfaces matching the backend Pydantic schemas ── */

export interface CrawlJob {
  id: number;
  url: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  pages_crawled: number;
  total_faculty_found: number;
  max_pages: number;
  error_message?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface FacultyContact {
  id: number;
  job_id: number;
  name: string | null;
  email: string | null;
  phone: string | null;
  department: string | null;
  designation: string | null;
  source_url: string | null;
  created_at: string;
}

export interface ExtractedItem {
  id: number;
  job_id: number;
  type: "email" | "phone" | "name";
  value: string;
  metadata_: Record<string, unknown> | null;
  source_url: string | null;
  created_at: string;
}

export interface CrawlStartResponse {
  job_id: number;
  message: string;
}

export interface StatusResponse {
  job_id: number;
  status: string;
  progress: number;
  pages_crawled: number;
  total_faculty_found: number;
}

export interface FacultyListResponse {
  job_id: number;
  total: number;
  faculty: FacultyContact[];
}

export interface SearchResponse {
  query: string;
  total: number;
  results: FacultyContact[];
}

export interface AnalyticsData {
  job_id: number;
  total_faculty: number;
  total_emails: number;
  total_phones: number;
  departments: { name: string; count: number }[];
  designations: { name: string; count: number }[];
  pages_crawled: number;
}

export interface ResultsResponse {
  job_id: number;
  emails: ExtractedItem[];
  phones: ExtractedItem[];
  names: ExtractedItem[];
}
