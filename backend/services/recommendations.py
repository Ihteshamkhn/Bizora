"""
Recommendations + proactive insights engine.

Turns raw analytics numbers into human-friendly insights and actionable
recommendations (with priority). Optionally uses the LLM for phrasing, but
every fact comes from Python calculations.
"""

from datetime import date

from sqlalchemy.orm import Session

from database.models import AiInsight
from services import analytics, forecasting


def _insight(severity: str, category: str, title: str, message: str,
             recommendation: str | None = None,
             priority: str = "MEDIUM") -> dict:
    return {
        "severity": severity,          # critical / warning / info / success
        "category": category,          # inventory / sales / expenses / customers
        "title": title,
        "message": message,
        "recommendation": recommendation,
        "priority": priority,
    }


def collect_insights(db: Session, business_id: int) -> list[dict]:
    """Scan the business data and produce proactive insights + recommendations."""
    today = date.today()
    month_start = today.replace(day=1)

    insights: list[dict] = []

    # ---------------- Inventory
    inv = analytics.get_inventory_status(db, business_id)
    for a in inv["alerts"][:5]:
        if a["status"] == "out_of_stock":
            insights.append(_insight(
                "critical", "inventory",
                f"{a['product']} is out of stock",
                f"{a['product']} has 0 units left. Every day without stock is lost revenue.",
                f"Restock {a['product']} immediately — it was selling "
                f"{a['daily_velocity']} units/day.", priority="HIGH"))
        else:
            when = (f", and may run out around {a['estimated_stockout_date']}"
                    if a["estimated_stockout_date"] else "")
            insights.append(_insight(
                "warning", "inventory",
                f"{a['product']} inventory is low",
                f"{a['product']} has {a['stock']} units left (reorder level: "
                f"{a['reorder_level']}){when}.",
                f"Restock {a['product']} soon. Suggested quantity: "
                f"{max(50, int(a['daily_velocity'] * 30))} units.",
                priority="HIGH" if a["estimated_stockout_date"] else "MEDIUM"))

    # ---------------- Sales trend
    sales_cur = analytics.get_sales_summary(db, business_id, month_start, today)
    prev_start, prev_end = analytics._prev_month_range(today)
    sales_prev = analytics.get_sales_summary(db, business_id, prev_start, prev_end)
    growth = analytics.calculate_growth(sales_cur["revenue"], sales_prev["revenue"])

    if growth is not None:
        if growth >= 0:
            insights.append(_insight(
                "success", "sales", "Revenue is growing",
                f"Revenue increased {growth}% compared with last month "
                f"({sales_cur['revenue']:,.0f} vs {sales_prev['revenue']:,.0f}).",
                None, priority="LOW"))
        else:
            insights.append(_insight(
                "warning", "sales", "Revenue declined this month",
                f"Revenue fell {abs(growth)}% compared with last month.",
                "Check which products slowed down and whether marketing spend changed.",
                priority="HIGH"))

    # ---------------- Expenses vs revenue
    profit = analytics.get_profit_summary(db, business_id, month_start, today)
    exp_prev = analytics.get_profit_summary(db, business_id, prev_start, prev_end)
    exp_growth = analytics.calculate_growth(profit["expenses"], exp_prev["expenses"])
    if exp_growth is not None and exp_growth > 10 and (growth or 0) < exp_growth:
        insights.append(_insight(
            "warning", "expenses", "Expenses rising faster than revenue",
            f"Expenses increased {exp_growth}%, while revenue changed only "
            f"{growth if growth is not None else 0}%.",
            "Review the largest expense categories before increasing spending further.",
            priority="MEDIUM"))

    # ---------------- Profit margin
    if profit["revenue"] > 0:
        margin = profit["profit_margin_pct"]
        if margin < 5:
            insights.append(_insight(
                "critical", "expenses", "Profit margin is very thin",
                f"Net margin is only {margin}% this month.",
                "Identify low-margin products and renegotiate costs or adjust prices.",
                priority="HIGH"))

    # ---------------- Customers
    cust = analytics.get_customers_summary(db, business_id)
    if cust["total_customers"] >= 10 and cust["top10_revenue_share_pct"] >= 30:
        insights.append(_insight(
            "info", "customers", "Revenue concentrated in few customers",
            f"Your top 10 customers generated {cust['top10_revenue_share_pct']}% "
            f"of total revenue.",
            "Consider a loyalty or retention plan for these high-value customers.",
            priority="LOW"))

    # ---------------- Stockout forecast
    stockouts = forecasting.predict_stockouts(db, business_id)
    urgent = [s for s in stockouts if s["urgent"]]
    if urgent:
        names = ", ".join(s["product"] for s in urgent[:3])
        insights.append(_insight(
            "warning", "inventory", "Stockouts predicted within lead time",
            f"{names} may run out within your supplier lead time.",
            "Place purchase orders now to avoid losing sales.", priority="HIGH"))

    # Persist so the dashboard can show read/unread state.
    for i in insights:
        db.add(AiInsight(business_id=business_id, **i))
    db.commit()
    return insights


def generate_insights(db: Session, business_id: int) -> list[dict]:
    """Collect insights AND persist them as AiInsight records."""
    insights = collect_insights(db, business_id)
    for i in insights:
        db.add(AiInsight(business_id=business_id, **i))
    db.commit()
    return insights


def health_briefing(db: Session, business_id: int) -> dict:
    """The proactive 'Good Morning' summary shown on the dashboard."""
    score = analytics.get_business_health_score(db, business_id)
    insights = collect_insights(db, business_id)   # no persistence here
    needs_attention = [i for i in insights if i["priority"] == "HIGH"]
    return {
        "health_score": score["score"],
        "drivers": score["drivers"],
        "needs_attention_count": len(needs_attention),
        "attention": needs_attention[:3],
        "briefing": (
            f"Business Health: {score['score']}/100. "
            f"{len(needs_attention)} things need attention. "
            f"Sales growth month-over-month: "
            f"{score['month_over_month_sales_growth_pct']}%."
        ),
    }
