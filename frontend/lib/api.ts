/** Shared API client for the Bizora backend. */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function authHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("bizora_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

// ---------- types ----------
export interface SalesSummary {
  revenue: number; orders: number; units_sold: number;
  transactions: number; avg_order_value: number;
}
export interface ProfitSummary {
  revenue: number; cogs: number; expenses: number; gross_profit: number;
  net_profit: number; profit_margin_pct: number;
}
export interface Overview {
  sales: SalesSummary; profit: ProfitSummary;
  inventory: { total_products: number; low_stock_count: number; out_of_stock_count: number; alerts: InventoryAlert[] };
  customers: { total_customers: number; repeat_customers: number; repeat_rate_pct: number; top_customers: { name: string; total_spent: number }[]; top10_revenue_share_pct: number };
}
export interface InventoryAlert {
  product: string; stock: number; reorder_level: number;
  daily_velocity: number; estimated_stockout_date: string | null;
  status: "low_stock" | "out_of_stock";
}
export interface Briefing {
  health_score: number; drivers: Record<string, { score: number; weight: string; trend: string }>;
  needs_attention_count: number;
  attention: { severity: string; category: string; title: string; message: string; recommendation?: string; priority: string }[];
  briefing: string;
}

// ---------- endpoints ----------
export const api = {
  signup: (email: string, password: string, full_name?: string) =>
    request<{ access_token: string }>("/api/auth/signup", {
      method: "POST", body: JSON.stringify({ email, password, full_name }),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }).toString(),
    }),
  createBusiness: (name: string, business_type?: string) =>
    request<{ id: number; name: string; business_type: string | null; currency: string }>("/api/businesses", {
      method: "POST", body: JSON.stringify({ name, business_type }),
    }),
  listBusinesses: () =>
    request<{ id: number; name: string; business_type: string | null; currency: string }[]>("/api/businesses"),

  overview: (businessId: number) => request<Overview>(`/api/analytics/${businessId}/overview`),
  dailySales: (businessId: number, days = 30) =>
    request<{ date: string; revenue: number }[]>(`/api/analytics/${businessId}/sales/daily?days=${days}`),
  monthlySales: (businessId: number) =>
    request<{ month: string; revenue: number }[]>(`/api/analytics/${businessId}/sales/monthly`),
  topProducts: (businessId: number) =>
    request<{ product: string; revenue: number; units: number }[]>(`/api/analytics/${businessId}/products/top`),
  healthScore: (businessId: number) =>
    request<{ score: number; drivers: Record<string, { score: number; weight: string; trend: string }> }>(
      `/api/analytics/${businessId}/health-score`),
  briefing: (businessId: number) => request<Briefing>(`/api/analytics/${businessId}/briefing`),
  forecast: (businessId: number) =>
    request<{ forecast: { projected_revenue: number; avg_daily_revenue: number } | null; message: string }>(
      `/api/analytics/${businessId}/forecast`),

  previewUpload: (businessId: number, fileType: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${API_URL}/api/import/${businessId}/${fileType}/preview`, {
      method: "POST", body: form, headers: authHeaders(),
    }).then(async (r) => {
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || "Upload failed");
      return r.json();
    });
  },
  confirmImport: (businessId: number, fileType: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${API_URL}/api/import/${businessId}/${fileType}/confirm`, {
      method: "POST", body: form, headers: authHeaders(),
    }).then(async (r) => {
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || "Import failed");
      return r.json() as Promise<{ status: string; records_imported: number; message: string }>;
    });
  },

  chat: (businessId: number, question: string, history?: { role: string; content: string }[]) =>
    request<{ answer: string; tools_used: string[]; facts: unknown }>(`/api/chat/${businessId}`, {
      method: "POST",
      body: JSON.stringify({ question, history }),
    }),
};
