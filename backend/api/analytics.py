"""Analytics + dashboard API. All numbers computed by services/analytics.py."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_business_owned
from database.connection import get_db
from database.models import Business
from services import analytics, forecasting, recommendations

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/{business_id}/overview")
def overview(business: Business = Depends(get_business_owned),
             db: Session = Depends(get_db)):
    """Main dashboard numbers."""
    return {
        "sales": analytics.get_sales_summary(db, business.id),
        "profit": analytics.get_profit_summary(db, business.id),
        "inventory": analytics.get_inventory_status(db, business.id),
        "customers": analytics.get_customers_summary(db, business.id),
    }


@router.get("/{business_id}/sales/daily")
def daily_sales(days: int = Query(30, ge=1, le=365),
                business: Business = Depends(get_business_owned),
                db: Session = Depends(get_db)):
    return analytics.get_daily_sales(db, business.id, days)


@router.get("/{business_id}/sales/monthly")
def monthly_sales(months: int = Query(12, ge=1, le=60),
                  business: Business = Depends(get_business_owned),
                  db: Session = Depends(get_db)):
    return analytics.get_monthly_sales(db, business.id, months)


@router.get("/{business_id}/products/top")
def top_products(limit: int = Query(10, ge=1, le=50),
                 worst: bool = False,
                 business: Business = Depends(get_business_owned),
                 db: Session = Depends(get_db)):
    return analytics.get_top_products(db, business.id, limit, worst)


@router.get("/{business_id}/products/margins")
def product_margins(business: Business = Depends(get_business_owned),
                    db: Session = Depends(get_db)):
    return analytics.get_product_margins(db, business.id)


@router.get("/{business_id}/inventory")
def inventory(business: Business = Depends(get_business_owned),
              db: Session = Depends(get_db)):
    return analytics.get_inventory_status(db, business.id)


@router.get("/{business_id}/customers")
def customers(business: Business = Depends(get_business_owned),
              db: Session = Depends(get_db)):
    return analytics.get_customers_summary(db, business.id)


@router.get("/{business_id}/expenses")
def expenses(business: Business = Depends(get_business_owned),
             db: Session = Depends(get_db)):
    return analytics.get_expenses_summary(db, business.id)


@router.get("/{business_id}/health-score")
def health_score(business: Business = Depends(get_business_owned),
                 db: Session = Depends(get_db)):
    return analytics.get_business_health_score(db, business.id)


@router.get("/{business_id}/forecast")
def forecast(horizon_days: int = Query(30, ge=7, le=90),
             business: Business = Depends(get_business_owned),
             db: Session = Depends(get_db)):
    return forecasting.forecast_sales(db, business.id, horizon_days)


@router.get("/{business_id}/stockout-predictions")
def stockouts(business: Business = Depends(get_business_owned),
              db: Session = Depends(get_db)):
    return forecasting.predict_stockouts(db, business.id)


@router.post("/{business_id}/insights/generate")
def generate_insights(business: Business = Depends(get_business_owned),
                      db: Session = Depends(get_db)):
    return recommendations.generate_insights(db, business.id)


@router.get("/{business_id}/briefing")
def briefing(business: Business = Depends(get_business_owned),
             db: Session = Depends(get_db)):
    return recommendations.health_briefing(db, business.id)
