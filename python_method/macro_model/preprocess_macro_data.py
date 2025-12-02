# preprocess_macro_data.py
#
# take macro_raw.csv (pulled from FRED) and turn it into something that
# we can use for the model of yield curve

import pandas as pd
import numpy as np

RAW_PATH = "macro_raw.csv"
OUT_PATH = "macro_monthly_clean.csv"


def load_raw_data(path=RAW_PATH):
    """load the raw csv and run checks"""
    df = pd.read_csv(path, index_col=0)
    # make sure its datetime
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    print("raw shape:", df.shape)
    print("raw head:")
    print(df.head())
    print("\nraw tail:")
    print(df.tail())

    print("\nmissing values per column (raw):")
    print(df.isna().sum())

    return df


def resample_to_monthly(df):
    """
    FRED series can be daily, monthly, quarterly, etc.
    For now, we will look at everything monthly

    - for daily stuff (yields) -> last value of the month
    - for monthly OR quarterly -> last available value that month
    """
    monthly = df.resample("M").last()

    print("\nmonthly shape:", monthly.shape)
    print("monthly head:")
    print(monthly.head())

    return monthly


def clean_missing_values(monthly):
    """
    Missing value strategy:
    - forward fill first (since macro series can be slow to move)
    - then backfill for any gaps at the beginning
    - after that, rows with too many NaNs need to be dropped
    """

    before_na = monthly.isna().sum()
    print("\nmissing values per column (before):")
    print(before_na)

    # forward fill to backfill
    filled = monthly.ffill().bfill()

    after_na = filled.isna().sum()
    print("\nmissing values per column (after):")
    print(after_na)

    # drop rows where majority is NaN
    na_counts = monthly.isna().sum(axis=1)
    cutoff = monthly.shape[1] / 2
    mask_keep = na_counts <= cutoff
    cleaned = filled[mask_keep]

    print(f"\nrows before dropping high-Na months: {filled.shape[0]}")
    print(f"rows after dropping high-Na months: {cleaned.shape[0]}")

    return cleaned


def basic_checks(df):
    """quick checks"""
    print("\n=== BASIC STATS ===")
    print(df.describe().T)

    print("\ncorrelation matrix (first few rows):")
    # dont print if too big
    corr = df.corr()
    print(corr.head())

    # check for specific columns
    for col in ["treasury_1y", "treasury_2y", "treasury_5y", "treasury_10y", "cpi", "unemployment"]:
        if col in df.columns:
            print(f"\n{col} sample:")
            print(df[col].tail())
        else:
            print(f"\nWARNING: {col} not in columns")


def main():
    try:
        raw = load_raw_data()
    except FileNotFoundError:
        print(f"could not find {RAW_PATH}, did you run fetch_macro_data.py first?")
        return

    monthly = resample_to_monthly(raw)
    clean = clean_missing_values(monthly)

    basic_checks(clean)

    # save to csv
    clean.to_csv(OUT_PATH)
    print(f"\n>>> saved cleaned monthly data to {OUT_PATH}")


if __name__ == "__main__":
    main()