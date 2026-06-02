import pandas as pd
from pathlib import Path

DATA_RAW = Path("data/raw")

DATASETS = {
    "fund_master":       "01_fund_master.csv",
    "nav_history":       "02_nav_history.csv",
    "aum_fund_house":    "03_aum_by_fund_house.csv",
    "monthly_sip":       "04_monthly_sip_inflows.csv",
    "category_inflows":  "05_category_inflows.csv",
    "folio_count":       "06_industry_folio_count.csv",
    "scheme_perf":       "07_scheme_performance.csv",
    "investor_txn":      "08_investor_transactions.csv",
    "portfolio":         "09_portfolio_holdings.csv",
    "benchmark":         "10_benchmark_indices.csv",
}

dfs = {}
for name, fname in DATASETS.items():
    df = pd.read_csv(DATA_RAW / fname)
    dfs[name] = df
    print(f"\n{'='*50}")
    print(f"  {name}  |  shape: {df.shape}")
    print(f"  dtypes: {df.dtypes.to_dict()}")
    print(df.head(3).to_string())

print("\n✅ All 10 datasets loaded successfully")

import pandas as pd
from pathlib import Path

DATA_RAW = Path("data/raw")

fund_master = pd.read_csv(DATA_RAW / "01_fund_master.csv")
nav_history  = pd.read_csv(DATA_RAW / "02_nav_history.csv")

master_codes = set(fund_master["amfi_code"].astype(str))
nav_codes    = set(nav_history["amfi_code"].astype(str))

missing_in_nav    = master_codes - nav_codes
extra_in_nav      = nav_codes - master_codes

print("=== DATA QUALITY REPORT ===")
print(f"fund_master codes:  {len(master_codes)}")
print(f"nav_history codes:  {len(nav_codes)}")
print(f"Missing in nav_history: {missing_in_nav or 'None — all good ✅'}")
print(f"Extra in nav_history:   {extra_in_nav or 'None ✅'}")

# Count NAV records per scheme
records_per_scheme = nav_history.groupby("amfi_code").size()
print(f"\nNAV records per scheme — min: {records_per_scheme.min()}, max: {records_per_scheme.max()}, mean: {records_per_scheme.mean():.0f}")