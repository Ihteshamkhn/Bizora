"""
Business Analytics Engine.

All raw business numbers are calculated HERE (Python + SQL), never by the LLM.
Every function takes a SQLAlchemy Session and a business_id so data isolation
is enforced at the query level.
"""

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import Sale, Product, Customer, Expense


# ---------------------------------------------------------------- helpers

def _month_start(d: date) -> date:
    return d.replace(day=1)


def _prev_month_range(today: date):
    start = _month_start(today)
    end = start - timedelta(days=1)          # last day of previous month
    return _month_start(end), end


def _sales_query(db: Session, business_id: int):
    return db.query(Sale).filter(Sale.business_id == business_id)


# ---------------------------------------------------------------- sales

def get_sales_summary(db: Session, business_id: int, start: date | None = None,
                      end: date | None = None) -> dict:
    q = _sales_query(db, business_id)
    if start:
        q = q.filter(Sale.sale_date >= start)
    if end:
        q = q.filter(Sale.sale_date <= end)

    revenue = db.query(func.coalesce(func.sum(Sale.total_amount), 0.0)).filter(
        Sale.business_id == business_id,
        *[Sale.sale_date >= start] if start else [],
        *[Sale.sale_date <= end] if end else [],
    ).scalar() or 0.0

    orders = q.distinct(Sale.order_id).count() if start or end else \
        db.query(func.count(func.distinct(Sale.order_id))).filter(
            Sale.business_id == business_id).scalar()
    units = q.with_entities(func.coalesce(func.sum(Sale.quantity), 0)).scalar() or 0
    rows = q.count()

    return {
        "revenue": round(float(revenue), 2),
        "orders": int(orders or 0),
        "units_sold": int(units),
        "transactions": rows,
        "avg_order_value": round(float(revenue) / orders, 2) if orders else 0.0,
    }


def get_daily_sales(db: Session, business_id: int, days: int = 30) -> list[dict]:
    since = date.today() - timedelta(days=days)
    rows = (
        db.query(Sale.sale_date, func.sum(Sale.total_amount))
        .filter(Sale.business_id == business_id, Sale.sale_date >= since)
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
        .all()
    )
    return [{"date": str(d), "revenue": float(v)} for d, v in rows]


def get_monthly_sales(db: Session, business_id: int, months: int = 12) -> list[dict]:
    from database.connection import engine

    if engine.dialect.name == "postgresql":
        month_expr = func.date_trunc("month", Sale.sale_date)
    else:  # SQLite: format date as YYYY-MM
        month_expr = func.strftime("%Y-%m", Sale.sale_date)

    rows = (
        db.query(month_expr.label("m"), func.sum(Sale.total_amount))
        .filter(Sale.business_id == business_id)
        .group_by("m").order_by("m").all()
    )
    out = [{"month": str(m), "revenue": float(v)} for m, v in rows]
    return out[-months:]


def calculate_growth(current: float, previous: float) -> float | None:
    """Percent change; None when previous period had no data."""
    if not previous:
        return None
    return round((current - previous) / previous * 100, 1)


# ---------------------------------------------------------------- profit

def get_profit_summary(db: Session, business_id: int, start: date | None = None,
                       end: date | None = None) -> dict:
    sales = get_sales_summary(db, business_id, start, end)

    exp_q = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.business_id == business_id)
    if start:
        exp_q = exp_q.filter(Expense.expense_date >= start)
    if end:
        exp_q = exp_q.filter(Expense.expense_date <= end)
    expenses = float(exp_q.scalar() or 0.0)

    # Cost of goods: join sales to products on name for cost price.
    cogs_q = (
        db.query(func.coalesce(func.sum(Sale.quantity * Product.cost_price), 0.0))
        .join(Product, (Product.business_id == Sale.business_id) &
              (Product.name == Sale.product_name))
        .filter(Sale.business_id == business_id)
    )
    if start:
        cogs_q = cogs_q.filter(Sale.sale_date >= start)
    if end:
        cogs_q = cogs_q.filter(Sale.sale_date <= end)
    cogs = float(cogs_q.scalar() or 0.0)

    gross_profit = sales["revenue"] - cogs
    net_profit = gross_profit - expenses
    margin = (net_profit / sales["revenue"] * 100) if sales["revenue"] else 0.0

    return {
        "revenue": sales["revenue"],
        "cogs": round(cogs, 2),
        "expenses": round(expenses, 2),
        "gross_profit": round(gross_profit, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round(margin, 1),
    }


# ---------------------------------------------------------------- products

def get_top_products(db: Session, business_id: int, limit: int = 10,
                     worst: bool = False) -> list[dict]:
    rows = (
        db.query(
            Sale.product_name,
            func.sum(Sale.total_amount).label("revenue"),
            func.sum(Sale.quantity).label("units"),
        )
        .filter(Sale.business_id == business_id)
        .group_by(Sale.product_name)
        .order_by(func.sum(Sale.total_amount).asc() if worst
                  else func.sum(Sale.total_amount).desc())
        .limit(limit)
        .all()
    )
    return [{"product": n, "revenue": float(r), "units": int(u)} for n, r, u in rows]


def get_product_margins(db: Session, business_id: int, limit: int = 10) -> list[dict]:
    """Lowest-margin products that actually sold."""
    rows = (
        db.query(
            Product.name,
            Product.cost_price,
            Product.selling_price,
            func.sum(Sale.quantity).label("units"),
        )
        .join(Product, (Product.business_id == Sale.business_id) &
              (Product.name == Sale.product_name))
        .filter(Sale.business_id == business_id, Product.selling_price > 0)
        .group_by(Product.name, Product.cost_price, Product.selling_price)
        .all()
    )
    items = []
    for name, cost, sell, units in rows:
        margin_pct = (sell - cost) / sell * 100 if cost is not None else None
        items.append({
            "product": name,
            "cost_price": float(cost or 0),
            "selling_price": float(sell),
            "margin_pct": round(margin_pct, 1) if margin_pct is not None else None,
            "units_sold": int(units or 0),
        })
    items.sort(key=lambda x: (x["margin_pct"] is None, x["margin_pct"]))
    return items[:limit]


# ---------------------------------------------------------------- inventory

def get_inventory_status(db: Session, business_id: int) -> dict:
    products = db.query(Product).filter(Product.business_id == business_id).all()
    low, out = [], []
    for p in products:
        if p.stock_quantity <= 0:
            out.append(p)
        elif p.stock_quantity <= p.reorder_level:
            low.append(p)

    # Sales velocity (avg daily units over last 30 days) → stockout estimate.
    since = date.today() - timedelta(days=30)
    vel_rows = (
        db.query(Sale.product_name, func.sum(Sale.quantity))
        .filter(Sale.business_id == business_id, Sale.sale_date >= since)
        .group_by(Sale.product_name)
        .all()
    )
    velocity = {n: u / 30.0 for n, u in vel_rows}

    alerts = []
    for p in low + out:
        v = velocity.get(p.name, 0.0)
        days_left = (p.stock_quantity / v) if v > 0 else None
        alerts.append({
            "product": p.name,
            "stock": p.stock_quantity,
            "reorder_level": p.reorder_level,
            "daily_velocity": round(v, 2),
            "estimated_stockout_date": str(date.today() + timedelta(days=int(days_left)))
                if days_left else None,
            "status": "out_of_stock" if p.stock_quantity <= 0 else "low_stock",
        })
    alerts.sort(key=lambda a: a["stock"])

    return {
        "total_products": len(products),
        "low_stock_count": len(low),
        "out_of_stock_count": len(out),
        "alerts": alerts[:20],
    }


# ---------------------------------------------------------------- customers

def get_customers_summary(db: Session, business_id: int) -> dict:
    total = db.query(func.count(Customer.id)).filter(
        Customer.business_id == business_id).scalar() or 0
    repeat = db.query(func.count(Customer.id)).filter(
        Customer.business_id == business_id, Customer.orders_count > 1).scalar() or 0

    top = (
        db.query(Customer.name, Customer.total_spent, Customer.orders_count)
        .filter(Customer.business_id == business_id)
        .order_by(Customer.total_spent.desc())
        .limit(10)
        .all()
    )

    total_revenue = db.query(func.coalesce(func.sum(Sale.total_amount), 0.0)).filter(
        Sale.business_id == business_id).scalar() or 0.0
    top10_revenue = sum(float(t[1] or 0) for t in top)

    return {
        "total_customers": int(total),
        "repeat_customers": int(repeat),
        "repeat_rate_pct": round(repeat / total * 100, 1) if total else 0.0,
        "top_customers": [
            {"name": n, "total_spent": float(s or 0), "orders": int(o or 0)}
            for n, s, o in top
        ],
        "top10_revenue_share_pct":
            round(top10_revenue / total_revenue * 100, 1) if total_revenue else 0.0,
    }


# ---------------------------------------------------------------- expenses

def get_expenses_summary(db: Session, business_id: int, months: int = 6) -> dict:
    by_cat = (
        db.query(Expense.category, func.sum(Expense.amount))
        .filter(Expense.business_id == business_id)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    from database.connection import engine

    if engine.dialect.name == "postgresql":
        month_expr = func.date_trunc("month", Expense.expense_date)
    else:
        month_expr = func.strftime("%Y-%m", Expense.expense_date)

    monthly = (
        db.query(month_expr.label("m"), func.sum(Expense.amount))
        .filter(Expense.business_id == business_id)
        .group_by("m").order_by("m").all()
    )
    return {
        "by_category": [
            {"category": c or "Uncategorized", "amount": float(a or 0)}
            for c, a in by_cat
        ],
        "monthly": [
            {"month": str(m), "amount": float(a or 0)}
            for m, a in monthly
        ][-months:],
    }


# ---------------------------------------------------------------- health score

def get_business_health_score(db: Session, business_id: int) -> dict:
    """
    Weighted 0-100 score:
      Sales 25% · Profit 25% · Inventory 20% · Customers 15% · Expenses 15%
    """
    today = date.today()
    cur_start, prev_start, prev_end = _month_start(today), *_prev_month_range(today)

    sales_cur = get_sales_summary(db, business_id, cur_start, today)["revenue"]
    sales_prev = get_sales_summary(db, business_id, prev_start, prev_end)["revenue"]
    growth = calculate_growth(sales_cur, sales_prev)

    profit = get_profit_summary(db, business_id, cur_start, today)
    inv = get_inventory_status(db, business_id)
    cust = get_customers_summary(db, business_id)
    exp = get_expenses_summary(db, business_id)

    # --- component scores (each 0-100)
    sales_score = max(0, min(100, 50 + (growth or 0) * 2.5))

    margin = profit["profit_margin_pct"]
    profit_score = max(0, min(100, margin * 4))          # 25% margin => 100

    problem_ratio = ((inv["low_stock_count"] + inv["out_of_stock_count"] * 2)
                     / max(inv["total_products"], 1))
    inventory_score = max(0, min(100, 100 - problem_ratio * 200))

    cust_score = max(0, min(100, cust["repeat_rate_pct"] * 2))

    # expense efficiency: expenses vs revenue this month
    exp_this_month = next(
        (m["amount"] for m in exp["monthly"]
         if m["month"] == today.strftime("%Y-%m")), 0.0)
    exp_ratio = exp_this_month / sales_cur if sales_cur else 1.0
    expense_score = max(0, min(100, 100 - exp_ratio * 100))

    overall = round(
        sales_score * 0.25 + profit_score * 0.25 + inventory_score * 0.20 +
        cust_score * 0.15 + expense_score * 0.15
    )

    drivers = {
        "Sales": {"score": round(sales_score), "weight": "25%",
                  "trend": "up" if (growth or 0) >= 0 else "down"},
        "Profit": {"score": round(profit_score), "weight": "25%",
                   "trend": "up" if margin >= 10 else "down"},
        "Inventory": {"score": round(inventory_score), "weight": "20%",
                      "trend": "up" if inventory_score >= 70 else "down"},
        "Customers": {"score": round(cust_score), "weight": "15%",
                      "trend": "up" if cust_score >= 50 else "down"},
        "Expenses": {"score": round(expense_score), "weight": "15%",
                     "trend": "up" if expense_score >= 60 else "down"},
    }

    return {
        "score": overall,
        "drivers": drivers,
        "month_over_month_sales_growth_pct": growth,
    }
