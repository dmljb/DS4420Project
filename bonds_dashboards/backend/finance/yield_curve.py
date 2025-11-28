import requests, os
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from fredapi import Fred
from .interest_models import InterestRatesModel


load_dotenv(override=True)
FRED_KEY = os.getenv('FRED_KEY')
fred = Fred(api_key=FRED_KEY)

class YieldCurve:
    def __init__(self):
        self.maturities = []  
        self.rates = []      
        
    def fetch_treasury_rates(self):
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

            for maturity, rate in latest_rates.items():
                self.maturities.append(maturity)
                self.rates.append(rate)
        except Exception as e:
            print(f"FRED API failed: {e}")
            self.fetch_treasury_rates_backup()

    def fetch_treasury_rates_backup(self):
        self.maturities = [1, 2, 5, 10] 
        self.rates = [3.8461, 3.6736, 3.7759, 4.312]
        
    def interpolate_rate(self, maturity_years):
        """Interpolate rate for any maturity using cubic spline"""
        if not self.rates:
            raise ValueError("No yield curve data loaded")
            
        spline = CubicSpline(self.maturities, self.rates)
        return float(spline(maturity_years))
    
    def get_discount_rates_for_bond(self, bond):
        """Return array of discount rates for each cash flow"""
        cash_flows = bond.cash_flows()
        discount_rates = []
        
        for cf in cash_flows:
            days_to_payment = (cf['date'] - datetime.date.today()).days
            years_to_payment = days_to_payment / 365.25
            
            if years_to_payment > 0:
                rate = self.interpolate_rate(years_to_payment)
                discount_rates.append(rate)
            else:
                discount_rates.append(0)
                
        return discount_rates
    
    # def vasicek_prediction(self):
    #     scenarios = {}

    #     for i, maturity in enumerate(self.maturities):

    #         model = InterestRatesModel(initial_rate=self.rates[i]/100)

    #         # Different parameters for different maturities
    #         if maturity <= 2:
    #             a, b, sigma = 0.5, 0.03, 0.008  # Short rates more volatile
    #         else:
    #             a, b, sigma = 0.2, 0.04, 0.012  # Long rates more stable
                
    #         # Generate rate paths for this maturity
    #         rate_paths = model.vasicek_simulation(
    #             a=a, b=b, sigma=sigma, 
    #             # n_simulations=n_simulations,
    #             # n_periods=time_horizon_months,
    #             dt=1/12  # Monthly steps
    #         )
            
    #         scenarios[f'{maturity}Y'] = rate_paths
            
    #     return scenarios

curve = YieldCurve()
curve.fetch_treasury_rates()

if __name__ == '__main__':
    print(curve.rates)
    print(curve.interpolate_rate(6.7))