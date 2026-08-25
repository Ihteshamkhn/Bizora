# 🚀 Bizora — AI Business Manager

A web-based AI Business Manager SaaS for small-business owners:
**Create account → Add business → Upload CSVs → Get dashboard → Chat with your AI Manager.**

The owner never touches Python, databases, or terminals.

---

## Architecture

```
Next.js Frontend  ──HTTPS──▶  FastAPI Backend
                                ├── Auth (JWT, bcrypt)
                                ├── CSV Import (pandas cleaning engine)
                                ├── Analytics Engine (all facts computed in Python)
                                ├── Forecasting (trend + stockout prediction)
                                ├── Recommendations / Insights / Health Score
                                └── AI Agent (Groq LLM — interprets facts only)
                                        │
                                   PostgreSQL (per-business data isolation)
```

**Golden rule:** Python/database calculates the numbers. The LLM only explains them.

## Project structure

```
backend/
├── main.py                  # FastAPI app entrypoint
├── config.py                # Settings from .env
├── api/
│   ├── deps.py              # Auth + business-isolation dependencies
│   ├── auth.py              # Signup / login (JWT)
│   ├── businesses.py        # Business CRUD
│   ├── upload.py            # CSV preview → confirm import
│   └── analytics.py         # Dashboard, KPIs, forecast, insights endpoints
├── services/
│   ├── data_cleaner.py      # Column detection, dedup, type/date/price fixes
│   ├── analytics.py         # Sales/profit/products/inventory/customers/health score
│   ├── forecasting.py       # Sales forecast + stockout prediction
│   └── recommendations.py   # Proactive insights + recommendations
├── ai/
│   ├── agent.py             # Intent → tools → facts → LLM interpretation
│   ├── tools.py             # get_sales, get_profit, get_low_stock, ...
│   ├── prompts.py           # System prompts
│   └── routes.py            # /api/chat endpoint
└── database/
    ├── connection.py
    └── models.py            # User, Business, Product, Sale, Customer, Expense, AiInsight

frontend/
├── app/
│   ├── page.tsx             # Landing page
│   ├── login/ · signup/     # Auth pages
│   ├── dashboard/           # KPIs, health score, sales chart, alerts
│   ├── upload/              # Drag & drop import with validation report
│   └── chat/                # AI manager chat
├── components/AuthForm.tsx
└── lib/api.ts               # Typed API client
```

## Quick start

### 1. Database

```bash
docker compose up db -d          # starts PostgreSQL on :5432
```

(or point `DATABASE_URL` at any PostgreSQL instance)

### 2. Backend

```bash
cd backend
python -m venv venv && venv\Scripts\activate     # Windows
pip install -r requirements.txt
copy ..\.env.example .env                        # then edit values
uvicorn main:app --reload                        # http://localhost:8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev                                      # http://localhost:3000
```

### Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Long random string for token signing |
| `GROQ_API_KEY` | Groq API key for the AI manager |
| `GROQ_MODEL` | e.g. `llama-3.3-70b-versatile` |

Or run everything with: `docker compose up --build`

## Key features

- **CSV import with validation report** — column auto-detection via aliases,
  duplicate removal, price/date/quantity repair; the owner sees a friendly
  summary like *"Your file contains 4,281 valid sales records."*
- **Analytics engine** — revenue, profit & margins, top/worst products,
  inventory velocity & stockout dates, customer concentration.
- **Business Health Score (0–100)** — weighted: Sales 25% · Profit 25% ·
  Inventory 20% · Customers 15% · Expenses 15%, with per-driver trends.
- **Proactive insights** — severity-tagged alerts *with actionable
  recommendations and priorities* ("Restock Mouse immediately — HIGH").
- **Forecasting** — next-30-day revenue projection + stockout prediction
  vs supplier lead time.
- **AI Manager chat** — the agent selects tools, Python computes facts from
  the owner's own data, the LLM explains. Facts are never hallucinated.
- **Data isolation** — every query is scoped by `business_id`, enforced by
  the `get_business_owned` dependency.

## Roadmap

- [x] Phase 1–3: import → clean → analytics → AI agent
- [x] Phase 4: forecasting, health score, proactive alerts
- [ ] Phase 5: Alembic migrations, rate limiting, tests, monitoring
- [ ] Phase 6: subscriptions & billing
- [ ] Phase 7: Shopify/WooCommerce/POS integrations
