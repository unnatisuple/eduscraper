"use client";

import { motion } from "framer-motion";

interface StatsCardProps {
  label: string;
  value: number | string;
  icon: string;
  color?: string;
  delay?: number;
}

export default function StatsCard({
  label,
  value,
  icon,
  color = "#06d6a0",
  delay = 0,
}: StatsCardProps) {
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay }}
      className="glass-card"
      style={{
        padding: "24px",
        display: "flex",
        alignItems: "center",
        gap: 18,
      }}
    >
      <div
        style={{
          width: 52,
          height: 52,
          borderRadius: 14,
          background: `${color}15`,
          border: `1px solid ${color}30`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 24,
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
      <div>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + 0.3 }}
          style={{
            fontSize: 28,
            fontWeight: 800,
            margin: 0,
            color,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
          }}
        >
          {typeof value === "number" ? value.toLocaleString() : value}
        </motion.p>
        <p
          style={{
            fontSize: 12,
            color: "var(--text-muted)",
            margin: "4px 0 0 0",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            fontWeight: 600,
          }}
        >
          {label}
        </p>
      </div>
    </motion.div>
  );
}
