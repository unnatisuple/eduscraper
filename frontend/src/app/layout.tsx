import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EduScraper — Faculty Contact Extractor",
  description:
    "Intelligent faculty contact extractor and search dashboard. Crawl university websites and extract names, emails, phone numbers, departments, and designations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div
          style={{
            minHeight: "100vh",
            background: "var(--bg-primary)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Ambient background glow */}
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "var(--gradient-hero)",
              pointerEvents: "none",
              zIndex: 0,
            }}
          />
          <div style={{ position: "relative", zIndex: 1 }}>{children}</div>
        </div>
      </body>
    </html>
  );
}
