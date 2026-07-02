"use client";

import { useState, useEffect } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export default function SearchBar({ onSearch, placeholder = "Search by name, email, department..." }: SearchBarProps) {
  const [query, setQuery] = useState("");

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      onSearch(query);
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [query, onSearch]);

  return (
    <div style={{ position: "relative", width: "100%", maxWidth: 600 }}>
      <span style={{ position: "absolute", left: 14, top: 14, fontSize: 16 }}>🔍</span>
      <input
        type="text"
        className="input-glass"
        style={{ paddingLeft: 42 }}
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
    </div>
  );
}
