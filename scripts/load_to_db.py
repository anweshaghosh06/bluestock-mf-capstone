# scripts/load_to_db.py

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# ==================================================
# Paths
# ==================================================

DB_PATH = Path("data/db/bluestock_mf.db")
RAW = Path("data/raw")
PROC = Path("data/processed")
SQL_DIR = Path("sql")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")

# ==================================================
# Create Schema
# ==================================================

with engine.connect() as conn:
    schema_sql = (SQL_DIR / "schema.sql").read_text()

    for stmt in schema_sql.split(";"):
        stmt = stmt.strip()

        if stmt:
            conn.execute(text(stmt))

    conn.commit()

print("✅ Schema created")

# ==================================================
# Files to Load
# ==================================================

LOADS = [
    ("01_fund_master.csv", "dim_fund", RAW),
    ("02_nav_history_clean.csv", "fact_nav", PROC),
    ("08_investor_transactions_clean.csv", "fact_transactions", PROC),
    ("07_scheme_performance_clean.csv", "fact_performance", PROC),
    ("03_aum_by_fund_house.csv", "fact_aum", RAW),
]

# ==================================================
# Load Data
# ==================================================

for fname, table, source_dir in LOADS:

    fpath = source_dir / fname
    df = pd.read_csv(fpath)

    # -------------------------
    # fact_nav
    # -------------------------
    if table == "fact_nav":

        df = df.rename(columns={
            "date": "date_id"
        })

        df = df[
            ["amfi_code", "date_id", "nav"]
        ]

    # -------------------------
    # fact_transactions
    # -------------------------
    elif table == "fact_transactions":

        df = df.rename(columns={
            "transaction_date": "date_id"
        })

        df = df[
            [
                "investor_id",
                "amfi_code",
                "date_id",
                "transaction_type",
                "amount_inr",
                "state",
                "city",
                "city_tier",
                "age_group",
                "gender",
                "annual_income_lakh",
                "payment_mode",
                "kyc_status"
            ]
        ]

    # -------------------------
    # fact_performance
    # -------------------------
    elif table == "fact_performance":

        df = df[
            [
                "amfi_code",
                "return_1yr_pct",
                "return_3yr_pct",
                "return_5yr_pct",
                "benchmark_3yr_pct",
                "alpha",
                "beta",
                "sharpe_ratio",
                "sortino_ratio",
                "std_dev_ann_pct",
                "max_drawdown_pct",
                "aum_crore",
                "expense_ratio_pct",
                "morningstar_rating",
                "risk_grade"
            ]
        ]

    # -------------------------
    # fact_aum
    # -------------------------
    elif table == "fact_aum":

        df = df.rename(columns={
        "date": "month",
        "aum_crore": "aum_cr"
    })

        df = df[
        [
            "fund_house",
            "month",
            "aum_cr"
        ]
    ]

    df.to_sql(
        table,
        engine,
        if_exists="append",
        index=False
    )

    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()

    print(f"{table}: {count} rows (✅)")

print("\n✅ All data loaded into bluestock_mf.db")