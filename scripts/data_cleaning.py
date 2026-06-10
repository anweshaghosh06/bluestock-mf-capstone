import pandas as pd
from pathlib import Path

# Paths
RAW = Path("data/raw")
PROC = Path("data/processed")

# Ensure output folder exists
PROC.mkdir(parents=True, exist_ok=True)


def clean_nav_history():
    """Clean NAV history dataset."""
    df = pd.read_csv(RAW / "02_nav_history.csv")
    print(f"Raw shape: {df.shape}")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    # Sort
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")
    print(f"Duplicates removed: {before - len(df)}")

    # Daily resampling + forward fill
    df = (
        df.set_index("date")
          .groupby("amfi_code")["nav"]
          .resample("D")
          .last()
          .ffill()
          .reset_index()
    )

    # Validate NAV > 0
    df = df[df["nav"] > 0]

    # Save
    df.to_csv(PROC / "02_nav_history_clean.csv", index=False)

    print(f"Clean shape: {df.shape}")
    print("✅ nav_history cleaned")

    return df


def clean_investor_transactions():
    """Clean investor transactions dataset."""
    df = pd.read_csv(RAW / "08_investor_transactions.csv")
    print(f"Raw shape: {df.shape}")

    # Standardize transaction type
    df["transaction_type"] = (
        df["transaction_type"]
        .astype(str)
        .str.strip()
    )

    valid_types = {"SIP", "Lumpsum", "Redemption"}

    invalid_types = (
        ~df["transaction_type"].isin(valid_types)
    ).sum()

    print(f"Unmapped transaction types: {invalid_types}")

    df = df[df["transaction_type"].isin(valid_types)]

    # Validate amount
    df["amount_inr"] = pd.to_numeric(
        df["amount_inr"],
        errors="coerce"
    )

    df = df[df["amount_inr"] > 0]

    # Parse dates
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    df = df.dropna(subset=["transaction_date"])

    # Validate KYC
    valid_kyc = {"Verified", "Pending", "Failed"}

    bad_kyc = df.loc[
        ~df["kyc_status"].isin(valid_kyc),
        "kyc_status"
    ].unique()

    print(f"Invalid KYC values: {list(bad_kyc)}")

    df = df[df["kyc_status"].isin(valid_kyc)]

    # Save
    df.to_csv(
        PROC / "08_investor_transactions_clean.csv",
        index=False
    )

    print(f"Clean shape: {df.shape}")
    print("✅ investor_transactions cleaned")

    return df

def clean_scheme_performance():
    df = pd.read_csv(RAW / "07_scheme_performance.csv")
    print(f"Raw shape: {df.shape}")

    return_cols = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct"
    ]

    # Convert return columns to numeric
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag unrealistic returns
    for col in return_cols:
        anomalies = ((df[col] > 200) | (df[col] < -100)).sum()

        print(f"Anomalies in {col}: {anomalies} rows")

        df.loc[
            (df[col] > 200) | (df[col] < -100),
            col
        ] = None

    # Validate expense ratio
    df["expense_ratio_pct"] = pd.to_numeric(
        df["expense_ratio_pct"],
        errors="coerce"
    )

    bad_exp = (
        (df["expense_ratio_pct"] < 0.1)
        | (df["expense_ratio_pct"] > 2.5)
    ).sum()

    print(f"expense_ratio out of range: {bad_exp} rows")

    df.loc[
        (df["expense_ratio_pct"] < 0.1)
        | (df["expense_ratio_pct"] > 2.5),
        "expense_ratio_pct"
    ] = None

    # Save cleaned file
    df.to_csv(
        PROC / "07_scheme_performance_clean.csv",
        index=False
    )

    print(f"Clean shape: {df.shape}")
    print("✅ scheme_performance cleaned")

    return df

if __name__ == "__main__":
    print("\n=== Cleaning NAV History ===")
    clean_nav_history()

    print("\n=== Cleaning Investor Transactions ===")
    clean_investor_transactions()

    print("\n=== Cleaning Scheme Performance ===")
    clean_scheme_performance()

    print("\n✅ All cleaning complete!")