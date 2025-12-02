# fetch_macro_data.py
#
# pull some macro indicators from FRED
# will be adjusted in the future, baseline

import os
import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

FRED_KEY = os.getenv("FRED_KEY")
fred = Fred(api_key=FRED_KEY)

series_ids = {
    "cpi": "CPIAUCSL",               # consumer price index
    "unemployment": "UNRATE",        # unemployment %
    "gdp": "GDP",                    # quarterly GDP
    "industrial_prod": "INDPRO",     # industrial production index
    "fed_funds": "FEDFUNDS",         # federal funds rate
    "personal_income": "PI",         # personal income
    "retail_sales": "RSAFS",         # retail and food services
    "housing_starts": "HOUST",       # housing starts

    # yields
    "treasury_1y": "DGS1",           # 1 year Treasury
    "treasury_2y": "DGS2",           # 2 year Treasury
    "treasury_5y": "DGS5",           # 5 year Treasury
    "treasury_10y": "DGS10",         # 10 year Treasury
}

def fetch_series(sid):
    """pull a single series safely."""
    try:
        s = fred.get_series(sid)
        return s
    except Exception as e:
        print(f"error fetching {sid}: {e}")
        return None

def build_macro_df():
    # store all time series
    data = {}
    for name, sid in series_ids.items():
        s = fetch_series(sid)
        if s is not None:
            data[name] = s

    # make into one dataframe
    df = pd.DataFrame(data)

    # ensure datetime
    df.index = pd.to_datetime(df.index)

    # sort unordered data
    df = df.sort_index()

    return df

if __name__ == "__main__":
    df = build_macro_df()
    print(df.tail())

    # early version save
    out_path = "macro_raw.csv"
    df.to_csv(out_path)
    print(f"saved raw macro data to {out_path}")