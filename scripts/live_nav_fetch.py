import requests
import pandas as pd
from pathlib import Path

DATA_RAW = Path("data/raw")

def fetch_nav(scheme_code: int, scheme_name: str) -> pd.DataFrame:
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching: {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    
    # 'data' key has list of {date, nav} dicts
    df = pd.DataFrame(data["data"])
    df["amfi_code"] = scheme_code
    df["scheme_name"] = scheme_name
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = pd.to_numeric(df["nav"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


SCHEMES = {
    119551: "SBI Bluechip Direct",
    120503: "ICICI Pru Bluechip Direct",
    118632: "Nippon India Large Cap Direct",
    119092: "Axis Bluechip Direct",
    120841: "Kotak Bluechip Direct",
}

if __name__ == "__main__":
    all_dfs = []
    for code, name in SCHEMES.items():
        try:
            df = fetch_nav(code, name)
            fname = f"live_{name.lower().replace(' ', '_')}.csv"
            df.to_csv(DATA_RAW / fname, index=False)
            print(f"✅ {name}: {len(df)} rows")
            all_dfs.append(df)
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    # Combine all into one master file
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(DATA_RAW / "live_nav_all_5_schemes.csv", index=False)
    print(f"\nCombined: {combined.shape}")