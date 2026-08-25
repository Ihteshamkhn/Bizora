"""
Forecasting service.

Simple, dependency-light statistical forecasting (moving average + linear
trend). Python calculates the numbers; the LLM only explains them.
"""

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import Sale, Product


def forecast_sales(db: Session, business_id: int, horizon_days: int = 30) -> dict:
    """
    Forecast next `horizon_days` of revenue using daily history:
    linear trend fitted on the last 90 days + recent-average smoothing.
    """
    since = date.today() - timedelta(days=90)
    rows = (
        db.query(Sale.sale_date, func.sum(Sale.total_amount))
        .filter(Sale.business_id == business_id, Sale.sale_date >= since)
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
        .all()
    )
    if len(rows) < 7:
        return {
            "forecast": None,
            "message": "Not enough sales history to forecast (need at least 7 days of data).",
        }

    # Fill missing days with 0 so the trend isn't skewed.
    by_day = {d: float(v or 0) for d, v in rows}
    start, end = rows[0][0], rows[-1][0]
    series = []
    d = start
    while d <= end:
        series.append(by_day.get(d, 0.0))
        d += timedelta(days=1)

    n = len(series)
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(series) / n
    denom = sum((x - mean_x) ** 2 for x in xs)
    slope = (sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series)) / denom) \
        if denom else 0.0
    intercept = mean_y - slope * mean_x

    # Blend trend projection with last-14-day average for stability.
    recent_avg = sum(series[-14:]) / min(14, n)
    daily_forecast = []
    for i in range(1, horizon_days + 1):
        trend_val = intercept + slope * (n - 1 + i)
        blended = max(0.0, 0.6 * trend_val + 0.4 * recent_avg)
        daily_forecast.append(round(blended, 2))

    total = round(sum(daily_forecast), 2)
    return {
        "forecast": {
            "horizon_days": horizon_days,
            "projected_revenue": total,
            "avg_daily_revenue": round(total / horizon_days, 2),
            "daily": [
                {"date": str(date.today() + timedelta(days=i)), "revenue": v}
                for i, v in enumerate(daily_forecast, start=1)
            ],
        },
        "message": f"Expected next-{horizon_days}-day revenue: approximately {total:,.0f}.",
    }


def predict_stockouts(db: Session, business_id: int,
                      lead_time_days: int = 7) -> list[dict]:
    """
    Stockout prediction = current stock ÷ sales velocity vs supplier lead time.
    """
    products = db.query(Product).filter(Product.business_id == business_id).all()
    since = date.today() - timedelta(days=30)
    vel_rows = (
        db.query(Sale.product_name, func.sum(Sale.quantity))
        .filter(Sale.business_id == business_id, Sale.sale_date >= since)
        .group_by(Sale.product_name)
        .all()
    )
    velocity = {n: u / 30.0 for n, u in vel_rows}

    predictions = []
    for p in products:
        v = velocity.get(p.name, 0.0)
        if p.stock_quantity <= 0:
            predictions.append({
                "product": p.name, "stock": 0, "daily_velocity": round(v, 2),
                "days_until_stockout": 0,
                "stockout_date": str(date.today()),
                "urgent": True,
            })
        elif v > 0:
            days_left = p.stock_quantity / v
            if days_left <= lead_time_days * 2:      # only flag near-term risks
                predictions.append({
                    "product": p.name,
                    "stock": p.stock_quantity,
                    "daily_velocity": round(v, 2),
                    "days_until_stockout": round(days_left, 1),
                    "stockout_date": str(date.today() + timedelta(days=int(days_left))),
                    "urgent": days_left <= lead_time_days,
                })
    predictions.sort(key=lambda x: x["days_until_stockout"])
    return predictions
