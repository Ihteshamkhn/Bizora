"""
Data Cleaning Engine.

Takes a raw uploaded CSV (as a DataFrame), detects columns, validates
structure, and returns (clean_df, report). The business owner only ever
sees the human-friendly `report`.
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class CleanReport:
    file_type: str = ""
    total_rows: int = 0
    valid_rows: int = 0
    duplicates_removed: int = 0
    missing_values_fixed: int = 0
    invalid_dates_fixed: int = 0
    invalid_prices_fixed: int = 0
    invalid_quantities_fixed: int = 0
    detected_columns: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def summary(self) -> str:
        if self.errors:
            return f"Import failed: {'; '.join(self.errors)}"
        msg = (
            f"Your file contains {self.valid_rows:,} valid {self.file_type} records "
            f"(out of {self.total_rows:,} rows)."
        )
        if self.duplicates_removed:
            msg += f" {self.duplicates_removed} duplicate records were removed."
        for w in self.warnings:
            msg += f" ⚠ {w}"
        return msg


# Column aliases per dataset type — makes imports resilient to messy headers.
COLUMN_ALIASES = {
    "sales": {
        "order_id": ["order_id", "orderid", "order", "invoice", "invoice_no", "transaction_id"],
        "product_name": ["product_name", "product", "item", "item_name", "sku_name", "description"],
        "customer_name": ["customer_name", "customer", "buyer", "client"],
        "quantity": ["quantity", "qty", "units", "units_sold", "amount_sold"],
        "unit_price": ["unit_price", "price", "price_per_unit", "rate", "selling_price"],
        "total_amount": ["total_amount", "total", "revenue", "amount", "sale_amount", "subtotal"],
        "sale_date": ["sale_date", "date", "order_date", "transaction_date", "timestamp"],
    },
    "inventory": {
        "name": ["name", "product_name", "product", "item", "item_name"],
        "sku": ["sku", "code", "product_code", "item_code"],
        "category": ["category", "type", "product_category"],
        "cost_price": ["cost_price", "cost", "purchase_price", "buy_price"],
        "selling_price": ["selling_price", "price", "sale_price", "retail_price"],
        "stock_quantity": ["stock_quantity", "stock", "quantity", "qty", "current_stock", "on_hand"],
        "reorder_level": ["reorder_level", "reorder_point", "min_stock", "minimum_stock"],
    },
    "customers": {
        "name": ["name", "customer_name", "customer", "full_name"],
        "email": ["email", "email_address", "e_mail"],
        "phone": ["phone", "phone_number", "mobile", "contact"],
        "city": ["city", "town"],
        "region": ["region", "state", "province", "area"],
        "total_spent": ["total_spent", "total_spend", "lifetime_value", "ltv", "spent"],
        "orders_count": ["orders_count", "orders", "num_orders", "order_count"],
    },
    "expenses": {
        "description": ["description", "details", "note", "notes", "expense"],
        "category": ["category", "expense_category", "type", "expense_type"],
        "amount": ["amount", "cost", "value", "total", "expense_amount"],
        "expense_date": ["expense_date", "date", "paid_on", "transaction_date"],
    },
}

REQUIRED_COLUMNS = {
    "sales": [("product_name", "quantity"), ("product_name", "unit_price"), ("product_name", "sale_date")],
    "inventory": [("name",)],
    "customers": [("name",)],
    "expenses": [("amount",), ("expense_date",)],
}


def _normalize(text) -> str:
    return str(text).strip().lower().replace(" ", "_").replace("-", "_")


def detect_columns(df: pd.DataFrame, file_type: str) -> dict:
    """Map actual dataframe columns to canonical names using aliases."""
    mapping = {}
    normalized = {_normalize(c): c for c in df.columns}
    for canonical, aliases in COLUMN_ALIASES[file_type].items():
        for alias in [canonical] + aliases:
            if alias in normalized:
                mapping[canonical] = normalized[alias]
                break
    return mapping


def clean_dataframe(df: pd.DataFrame, file_type: str) -> tuple[Optional[pd.DataFrame], CleanReport]:
    """Clean an uploaded CSV. Returns (clean_dataframe_or_None, report)."""
    report = CleanReport(file_type=file_type, total_rows=len(df))
    df = df.copy()
    df.columns = [_normalize(c) for c in df.columns]

    # 1. Column detection -------------------------------------------------
    mapping = detect_columns(df, file_type)
    report.detected_columns = mapping

    missing_required = [
        req for reqs in REQUIRED_COLUMNS[file_type] for req in reqs if req not in mapping
    ]
    if len(missing_required) == len(REQUIRED_COLUMNS[file_type][0]) or not mapping:
        report.errors.append(
            f"Could not recognize required columns. Detected: {list(df.columns)}. "
            f"Expected something like: {list(COLUMN_ALIASES[file_type].keys())}"
        )
        return None, report

    df = df.rename(columns={v: k for k, v in mapping.items()})
    keep = list(mapping.keys())
    df = df[keep]

    # 2. Drop fully-empty rows & exact duplicates -------------------------
    df = df.dropna(how="all")
    before = len(df)
    df = df.drop_duplicates()
    report.duplicates_removed = before - len(df)

    # 3. Type fixes --------------------------------------------------------
    for col in ("quantity", "stock_quantity", "reorder_level", "orders_count"):
        if col in df.columns:
            original_non_null = df[col].notna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            fixed = int(original_non_null - df[col].notna().sum())
            if fixed:
                report.invalid_quantities_fixed += fixed
                report.warnings.append(f"{fixed} rows had invalid '{col}' values.")
            df[col] = df[col].fillna(0).astype(int)

    for col in ("unit_price", "total_amount", "cost_price", "selling_price", "amount", "total_spent"):
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[^\d.\-]", "", regex=True)  # strip currency symbols / commas
                .replace("", np.nan)
            )
            original_non_null = df[col].notna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            bad = int(original_non_null - df[col].notna().sum())
            negative = int(((df[col] < 0)).sum())
            if bad:
                report.invalid_prices_fixed += bad
                report.warnings.append(f"{bad} rows had invalid '{col}' values.")
            if negative:
                df.loc[df[col] < 0, col] = abs(df[col])
                report.warnings.append(f"{negative} negative '{col}' values were corrected.")

    # 4. Dates --------------------------------------------------------------
    date_col = "sale_date" if "sale_date" in df.columns else (
        "expense_date" if "expense_date" in df.columns else None
    )
    if date_col:
        original_non_null = df[date_col].notna().sum()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=False)
        bad_dates = int(original_non_null - df[date_col].notna().sum())
        if bad_dates:
            report.invalid_dates_fixed += bad_dates
            report.warnings.append(f"{bad_dates} rows had unparseable dates and were dropped.")
        df = df.dropna(subset=[date_col])
        df[date_col] = df[date_col].dt.date

    # 5. Missing text values -------------------------------------------------
    text_cols = [c for c in df.columns if df[c].dtype == object]
    for col in text_cols:
        n_missing = int(df[col].isna().sum())
        if n_missing:
            report.missing_values_fixed += n_missing
            df[col] = df[col].fillna("Unknown")

    # 6. Drop rows that are still unusable ------------------------------------
    if file_type == "sales":
        df = df[df["product_name"].astype(str).str.strip() != ""]
        if "unit_price" in df.columns:
            df["unit_price"] = df["unit_price"].fillna(0)
        if "total_amount" not in df.columns and "unit_price" in df.columns:
            qty = df["quantity"] if "quantity" in df.columns else 1
            df["total_amount"] = df["unit_price"] * qty
        elif "total_amount" in df.columns:
            df["total_amount"] = df["total_amount"].fillna(0)
    if file_type == "expenses":
        df = df.dropna(subset=["amount"])

    report.valid_rows = len(df)
    if report.valid_rows == 0:
        report.errors.append("No valid records remained after cleaning.")
        return None, report

    return df.reset_index(drop=True), report
