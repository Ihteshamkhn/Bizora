"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip,
} from "recharts";
import { api, Briefing, Overview } from "@/lib/api";

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return n.toLocaleString();
}

export default function Dashboard() {
  const router = useRouter();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [sales, setSales] = useState<{ date: string; revenue: number }[]>([]);
  const [businessId, setBusinessId] = useState<number | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const businesses = await api.listBusinesses();
        let biz = businesses[0];
        if (!biz) {
          biz = await api.createBusiness("My Business");
        }
        setBusinessId(biz.id);
        const [ov, br, ds] = await Promise.all([
          api.overview(biz.id),
          api.briefing(biz.id),
          api.dailySales(biz.id, 30),
        ]);
        setOverview(ov);
        setBriefing(br);
        setSales(ds);
      } catch (err) {
        if (err instanceof Error && err.message.includes("401")) {
          router.push("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      }
    })();
  }, [router]);

  if (error)
    return (
      <main className="p-10 text-center text-red-600">
        {error} —{" "}
        <Link href="/login" className="text-brand-600 underline">
          log in again
        </Link>
      </main>
    );

  if (!overview || !briefing)
    return <main className="p-10 text-center text-gray-500">Loading your business…</main>;

  const s = overview.sales;
  const p = overview.profit;

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Business Overview</h1>
          <p className="text-gray-500">{briefing.briefing}</p>
        </div>
        <nav className="flex gap-3">
          <Link href="/upload" className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
            📥 Import Data
          </Link>
          <Link href="/chat" className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold hover:bg-gray-100">
            💬 AI Manager
          </Link>
        </nav>
      </header>

      {/* KPI cards */}
      <section className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Revenue", value: `₨${fmt(s.revenue)}` },
          { label: "Net Profit", value: `₨${fmt(p.net_profit)}`, sub: `${p.profit_margin_pct}% margin` },
          { label: "Orders", value: s.orders.toLocaleString() },
          { label: "Customers", value: overview.customers.total_customers.toLocaleString() },
        ].map((k) => (
          <div key={k.label} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">{k.label}</p>
            <p className="mt-1 text-2xl font-bold">{k.value}</p>
            {k.sub && <p className="text-xs text-gray-400">{k.sub}</p>}
          </div>
        ))}
      </section>

      {/* Health + chart */}
      <section className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Business Health</h2>
          <p className="mt-2 text-5xl font-extrabold text-brand-600">
            {briefing.health_score}
            <span className="text-lg text-gray-400">/100</span>
          </p>
          <ul className="mt-4 space-y-2 text-sm">
            {Object.entries(briefing.drivers).map(([name, d]) => (
              <li key={name} className="flex items-center justify-between">
                <span>{name}</span>
                <span>
                  {d.trend === "up" ? "↑" : "↓"} {d.score}/100{" "}
                  <span className="text-gray-400">({d.weight})</span>
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="lg:col-span-2 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Sales Trend (30 days)</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sales}>
                <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => fmt(Number(v))} />
                <Tooltip formatter={(v) => [`₨${Number(v).toLocaleString()}`, "Revenue"]} />
                <Area type="monotone" dataKey="revenue" stroke="#4f46e5" fill="#eef2ff" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Alerts + insights */}
      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Inventory Alerts</h2>
          {overview.inventory.alerts.length === 0 ? (
            <p className="mt-3 text-sm text-gray-500">No inventory issues. 🎉</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {overview.inventory.alerts.slice(0, 5).map((a) => (
                <li key={a.product} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm">
                  <span>
                    {a.status === "out_of_stock" ? "🔴" : "🟡"} {a.product}
                  </span>
                  <span className="text-gray-500">
                    {a.stock} left{a.estimated_stockout_date ? ` · out ~${a.estimated_stockout_date}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Needs Attention ({briefing.needs_attention_count})</h2>
          {briefing.attention.length === 0 ? (
            <p className="mt-3 text-sm text-gray-500">Everything looks good. 👍</p>
          ) : (
            <ul className="mt-3 space-y-3">
              {briefing.attention.map((i, idx) => (
                <li key={idx} className="rounded-lg bg-gray-50 px-3 py-2 text-sm">
                  <p className="font-medium">{i.title}</p>
                  <p className="text-gray-600">{i.message}</p>
                  {i.recommendation && (
                    <p className="mt-1 text-brand-700">→ {i.recommendation}</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </main>
  );
}
