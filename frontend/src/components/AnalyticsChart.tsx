"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

interface ChartData {
  name: string;
  count: number;
}

interface AnalyticsChartProps {
  data: ChartData[];
  type: 'pie' | 'bar';
  title: string;
}

const COLORS = ['#06d6a0', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#6366f1', '#14b8a6', '#f43f5e', '#84cc16'];

export default function AnalyticsChart({ data, type, title }: AnalyticsChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "24px", height: 350, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>{title}</h3>
        <p style={{ color: "var(--text-muted)" }}>Not enough data to generate chart.</p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: "24px", height: 350, display: "flex", flexDirection: "column" }}>
      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>{title}</h3>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          {type === 'pie' ? (
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="count"
                stroke="rgba(15, 23, 55, 0.8)"
                strokeWidth={2}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ background: "rgba(15, 23, 55, 0.9)", border: "1px solid var(--border-color)", borderRadius: 8, color: "var(--text-primary)" }}
                itemStyle={{ color: "var(--text-primary)" }}
              />
            </PieChart>
          ) : (
            <BarChart data={data.slice(0, 8)} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
              <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickMargin={10} angle={-45} textAnchor="end" height={60} />
              <YAxis stroke="var(--text-muted)" fontSize={12} allowDecimals={false} />
              <Tooltip
                cursor={{ fill: "rgba(6, 214, 160, 0.05)" }}
                contentStyle={{ background: "rgba(15, 23, 55, 0.9)", border: "1px solid var(--border-color)", borderRadius: 8, color: "var(--text-primary)" }}
              />
              <Bar dataKey="count" fill="url(#colorGradient)" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
