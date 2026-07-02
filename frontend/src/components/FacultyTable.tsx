"use client";

import { useState } from "react";
import type { FacultyContact } from "@/types";

interface FacultyTableProps {
  faculty: FacultyContact[];
}

export default function FacultyTable({ faculty }: FacultyTableProps) {
  const [sortField, setSortField] = useState<keyof FacultyContact>("id");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const handleSort = (field: keyof FacultyContact) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  const sortedFaculty = [...faculty].sort((a, b) => {
    const aVal = a[sortField] || "";
    const bVal = b[sortField] || "";
    if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  return (
    <div className="glass-card" style={{ overflow: "hidden" }}>
      <div style={{ overflowX: "auto" }}>
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort("name")} style={{ cursor: "pointer" }}>Name {sortField === "name" && (sortDir === "asc" ? "↑" : "↓")}</th>
              <th onClick={() => handleSort("email")} style={{ cursor: "pointer" }}>Email {sortField === "email" && (sortDir === "asc" ? "↑" : "↓")}</th>
              <th onClick={() => handleSort("phone")} style={{ cursor: "pointer" }}>Phone {sortField === "phone" && (sortDir === "asc" ? "↑" : "↓")}</th>
              <th onClick={() => handleSort("department")} style={{ cursor: "pointer" }}>Department {sortField === "department" && (sortDir === "asc" ? "↑" : "↓")}</th>
              <th onClick={() => handleSort("designation")} style={{ cursor: "pointer" }}>Designation {sortField === "designation" && (sortDir === "asc" ? "↑" : "↓")}</th>
            </tr>
          </thead>
          <tbody>
            {sortedFaculty.map((f) => (
              <tr key={f.id}>
                <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>{f.name || "—"}</td>
                <td>
                  {f.email ? (
                    <a href={`mailto:${f.email}`} style={{ color: "var(--accent-blue)", textDecoration: "none" }}>
                      {f.email}
                    </a>
                  ) : "—"}
                </td>
                <td>{f.phone || "—"}</td>
                <td>{f.department || "—"}</td>
                <td>{f.designation || "—"}</td>
              </tr>
            ))}
            {sortedFaculty.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)" }}>
                  No faculty contacts found yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
