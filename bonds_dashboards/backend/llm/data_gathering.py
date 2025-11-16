import requests, os
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from fredapi import Fred
import re

load_dotenv(override=True)
FRED_KEY = os.getenv('FRED_KEY')
fred = Fred(api_key=FRED_KEY)

def fetch_treasury_rates():
        """Fetch current Treasury zero rates from FRED"""
        series_ids = {
            # 1: "DGS1",     # 1-Year Treasury
            # 2: "DGS2",     # 2-Year Treasury  
            # 5: "DGS5",     # 5-Year Treasury
            # 10: "DGS10",   # 10-Year Treasury
            # 30: "DGS30"    # 30-Year Treasury
            1: "THREEFY1",
            2: "THREEFY2",
            5: "THREEFY5",
            10: "THREEFY10",
        }
        try:
            df = pd.DataFrame({m: fred.get_series(sid) for m, sid in series_ids.items()})
            latest_rates = df.iloc[-1].dropna()  
        except Exception as e:
            print(f"FRED API failed: {e}")
        
        return latest_rates

def parse_first_day(date_str: str) -> pd.Timestamp:
    """
    Returns the first day as a normalized pd.Timestamp.
    Examples:
      "January 25-26, 2022" -> 2022-01-25
      "January 31-February 1, 2023" -> 2023-01-31
      "March 15, 2022" -> 2022-03-15
    """
    pattern = r'^\s*([A-Za-z]+)\s+(\d{1,2})(?:-(?:[A-Za-z]+\s+)?\d{1,2})?,\s*(\d{4})\s*$'
    m = re.match(pattern, date_str)
    if not m:
        raise ValueError(f"Unrecognized date format: {date_str}")
    month1, day1, year = m.groups()
    return pd.to_datetime(f"{month1} {day1} {year}").normalize()


def fetch_macro_indicators(meeting_date: str | pd.Timestamp):
    d = parse_first_day(meeting_date)
    md = pd.to_datetime(d).normalize()
    series_ids = {
        "unemployement": "UNRATE",
        'core_cpi': 'CPILFESL',
        'gdp' : 'GDP',
        'ten_two_spread': 'T10Y2Y',
        'fed_funds' : 'FEDFUNDS',
        'vix' : 'VIXCLS',
        'md' : ''
        }
    data = {}
    for name, sid in series_ids.items():
        try:
            # Limit to observations up to the meeting date
            s = fred.get_series(sid, observation_end=md)
            s = s.dropna()
            data[name] = s.iloc[-1] if not s.empty else pd.NA
        except Exception as e:
            print(f"{name} ({sid}) failed: {e}")
            data[name] = pd.NA

    return pd.Series(data, name=md.date())

