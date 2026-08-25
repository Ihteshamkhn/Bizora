"""CSV upload + import API.

Flow: validate file -> clean with pandas -> preview report -> confirm import
into PostgreSQL. The owner only ever sees the human-friendly report.
"""

import io

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.deps import get_business_owned
from config import settings
from database.connection import get_db
from database.models import Business, Customer, Expense, Product, Sale
from services.data_cleaner import CleanReport, clean_dataframe

router = APIRouter(prefix="/api/import", tags=["import"])

ALLOWED_TYPES = {"sales", "inventory", "customers", "expenses"}


def _read_csv(file: UploadFile) -> pd.DataFrame:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only .csv files are supported")
    content = file.file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(413,
                            f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit")
    try:
        return pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(400, "Could not parse the file as CSV")


def _store(db: Session, business_id: int, file_type: str, df: pd.DataFrame):
    """Bulk-insert cleaned rows into the business's isolated tables."""
    records = df.to_dict("records")
    if file_type == "sales":
        db.add_all([Sale(business_id=business_id,
                         order_id=str(r.get("order_id")) if r.get("order_id") else None,
                         product_name=r["product_name"],
                         customer_name=r.get("customer_name"),
                         quantity=int(r.get("quantity", 1)),
                         unit_price=float(r.get("unit_price", 0)),
                         total_amount=float(r.get("total_amount", 0)),
                         sale_date=r["sale_date"]) for r in records])
    elif file_type == "inventory":
        # Upsert products by name (case-insensitive).
        existing = {p.name.lower(): p for p in
                    db.query(Product).filter(Product.business_id == business_id)}
        for r in records:
            name = str(r["name"]).strip()
            p = existing.get(name.lower())
            if p:
                p.stock_quantity = int(r.get("stock_quantity", p.stock_quantity))
                p.cost_price = float(r.get("cost_price", p.cost_price or 0))
                p.selling_price = float(r.get("selling_price", p.selling_price or 0))
                p.reorder_level = int(r.get("reorder_level", p.reorder_level))
                p.category = r.get("category", p.category)
            else:
                p = Product(business_id=business_id, name=name,
                            sku=r.get("sku"), category=r.get("category"),
                            cost_price=float(r.get("cost_price", 0)),
                            selling_price=float(r.get("selling_price", 0)),
                            stock_quantity=int(r.get("stock_quantity", 0)),
                            reorder_level=int(r.get("reorder_level", 10)))
                existing[name.lower()] = p
                db.add(p)
    elif file_type == "customers":
        db.add_all([Customer(business_id=business_id, name=r["name"],
                             email=r.get("email"), phone=r.get("phone"),
                             city=r.get("city"), region=r.get("region"),
                             total_spent=float(r.get("total_spent", 0)),
                             orders_count=int(r.get("orders_count", 0)))
                    for r in records])
    elif file_type == "expenses":
        db.add_all([Expense(business_id=business_id,
                            description=r.get("description"),
                            category=r.get("category"),
                            amount=float(r.get("amount", 0)),
                            expense_date=r["expense_date"]) for r in records])


@router.post("/{business_id}/{file_type}/preview")
async def preview_upload(business_id: int, file_type: str,
                         file: UploadFile,
                         business: Business = Depends(get_business_owned)):
    """Step 1: clean and return a human-friendly report + sample rows."""
    if file_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"file_type must be one of {sorted(ALLOWED_TYPES)}")
    df = await _read_csv(file)
    clean_df, report = clean_dataframe(df, file_type)

    response = {
        "report": {
            "file_type": report.file_type,
            "total_rows": report.total_rows,
            "valid_rows": report.valid_rows,
            "duplicates_removed": report.duplicates_removed,
            "warnings": report.warnings,
            "errors": report.errors,
            "summary": report.summary(),
            "detected_columns": report.detected_columns,
        },
        "sample": [],
    }
    if clean_df is not None:
        response["sample"] = clean_df.head(5).astype(str).to_dict("records")
    return response


@router.post("/{business_id}/{file_type}/confirm")
async def confirm_import(business_id: int, file_type: str,
                         file: UploadFile,
                         db: Session = Depends(get_db),
                         business: Business = Depends(get_business_owned)):
    """Step 2: re-clean and actually store the data."""
    if file_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"file_type must be one of {sorted(ALLOWED_TYPES)}")
    df = await _read_csv(file)
    clean_df, report = clean_dataframe(df, file_type)
    if clean_df is None:
        raise HTTPException(422, detail=report.summary())
    _store(db, business_id, file_type, clean_df)
    db.commit()
    return {"status": "imported",
            "records_imported": report.valid_rows,
            "message": report.summary()}
