"""
Agent tools: the functions the AI agent may call to fetch business facts.

Every tool takes (db, business_id, ...) so data isolation is guaranteed.
Tools return plain dicts of FACTS — the LLM only interprets them.
"""

from sqlalchemy.orm import Session

from services import analytics, forecasting


def get_sales(db: Session, business_id: int) -> dict:
    return analytics.get_sales_summary(db, business_id)


def get_revenue(db: Session, business_id: int) -> dict:
    return {"revenue": analytics.get_sales_summary(db, business_id)["revenue"]}


def get_profit(db: Session, business_id: int) -> dict:
    return analytics.get_profit_summary(db, business_id)


def get_expenses(db: Session, business_id: int) -> dict:
    return analytics.get_expenses_summary(db, business_id)


def get_inventory(db: Session, business_id: int) -> dict:
    return analytics.get_inventory_status(db, business_id)


def get_low_stock(db: Session, business_id: int) -> dict:
    inv = analytics.get_inventory_status(db, business_id)
    return {"alerts": inv["alerts"],
            "low_stock_count": inv["low_stock_count"],
            "out_of_stock_count": inv["out_of_stock_count"]}


def get_customers(db: Session, business_id: int) -> dict:
    return analytics.get_customers_summary(db, business_id)


def get_top_products(db: Session, business_id: int) -> dict:
    return {"products": analytics.get_top_products(db, business_id, 10)}


def calculate_growth(db: Session, business_id: int) -> dict:
    from datetime import date
    today = date.today()
    cur = analytics.get_sales_summary(db, business_id,
                                      today.replace(day=1), today)
    prev_start, prev_end = analytics._prev_month_range(today)
    prev = analytics.get_sales_summary(db, business_id, prev_start, prev_end)
    return {
        "this_month_revenue": cur["revenue"],
        "last_month_revenue": prev["revenue"],
        "growth_pct": analytics.calculate_growth(cur["revenue"], prev["revenue"]),
    }


def calculate_profit_margin(db: Session, business_id: int) -> dict:
    p = analytics.get_profit_summary(db, business_id)
    return {"profit_margin_pct": p["profit_margin_pct"],
            "net_profit": p["net_profit"]}


def forecast_sales_tool(db: Session, business_id: int) -> dict:
    result = forecasting.forecast_sales(db, business_id, 30)
    if result["forecast"] is None:
        return {"message": result["message"]}
    f = result["forecast"]
    return {"projected_next_30d_revenue": f["projected_revenue"],
            "avg_daily_revenue": f["avg_daily_revenue"]}


def predict_stockouts_tool(db: Session, business_id: int) -> dict:
    return {"predictions": forecasting.predict_stockouts(db, business_id)}


# name -> callable; used by the agent's tool-selection step
TOOL_REGISTRY = {
    "get_sales": get_sales,
    "get_revenue": get_revenue,
    "get_profit": get_profit,
    "get_expenses": get_expenses,
    "get_inventory": get_inventory,
    "get_low_stock": get_low_stock,
    "get_customers": get_customers,
    "get_top_products": get_top_products,
    "calculate_growth": calculate_growth,
    "calculate_profit_margin": calculate_profit_margin,
    "forecast_sales": forecast_sales_tool,
    "predict_stockouts": predict_stockouts_tool,
}
