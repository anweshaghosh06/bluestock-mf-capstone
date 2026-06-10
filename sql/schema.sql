-- DIMENSION TABLES

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code              INTEGER PRIMARY KEY,
    fund_house             TEXT NOT NULL,
    scheme_name            TEXT NOT NULL,
    category               TEXT,
    sub_category           TEXT,
    plan                   TEXT,
    launch_date            TEXT,
    benchmark              TEXT,
    expense_ratio_pct      REAL,
    exit_load_pct          REAL,
    min_sip_amount         REAL,
    min_lumpsum_amount     REAL,
    fund_manager           TEXT,
    risk_category          TEXT,
    sebi_category_code     TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id         TEXT PRIMARY KEY,
    year            INTEGER,
    month           INTEGER,
    quarter         INTEGER,
    week            INTEGER,
    day_of_week     INTEGER,
    is_weekend      INTEGER
);

--------------------------------------------------
-- FACT NAV
--------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_nav (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER NOT NULL,
    date_id         TEXT NOT NULL,
    nav             REAL NOT NULL,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

--------------------------------------------------
-- FACT TRANSACTIONS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_transactions (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,

    investor_id             TEXT,
    amfi_code               INTEGER NOT NULL,
    date_id                 TEXT NOT NULL,

    transaction_type        TEXT
        CHECK(transaction_type IN ('SIP','Lumpsum','Redemption')),

    amount_inr              REAL NOT NULL
        CHECK(amount_inr > 0),

    state                   TEXT,
    city                    TEXT,
    city_tier               TEXT,
    age_group               TEXT,
    gender                  TEXT,

    annual_income_lakh      REAL,
    payment_mode            TEXT,

    kyc_status              TEXT
        CHECK(kyc_status IN ('Verified','Pending','Failed')),

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

--------------------------------------------------
-- FACT PERFORMANCE
--------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_performance (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,

    amfi_code               INTEGER NOT NULL,

    return_1yr_pct          REAL,
    return_3yr_pct          REAL,
    return_5yr_pct          REAL,

    benchmark_3yr_pct       REAL,

    alpha                   REAL,
    beta                    REAL,

    sharpe_ratio            REAL,
    sortino_ratio           REAL,

    std_dev_ann_pct         REAL,
    max_drawdown_pct        REAL,

    aum_crore               REAL,
    expense_ratio_pct       REAL,

    morningstar_rating      INTEGER,
    risk_grade              TEXT,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code)
);

--------------------------------------------------
-- FACT AUM
--------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_aum (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    fund_house      TEXT NOT NULL,
    month           TEXT NOT NULL,
    aum_cr          REAL NOT NULL
);