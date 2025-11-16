from fredapi import Fred
import numpy as np, pandas as pd, os
from dotenv import load_dotenv

load_dotenv(override=True)
FRED_KEY = os.getenv('FRED_KEY')
fred = Fred(api_key=FRED_KEY)

class InterestRatesModel:
    def __init__(self, initial_rate):
        self.initial_rate = initial_rate
    
    def vasicek_simulation(self, a=0.2, b=0.04, sigma=0.01, n_simulations=1000, n_periods=20, dt=0.5):
        """
        a: mean reversion speed (0.1-0.5 typical)
        b: long-term mean rate (0.03-0.06 typical)  
        sigma: volatility (0.005-0.02 typical)
        """
        import numpy as np
        
        simulations = np.zeros((n_simulations, n_periods + 1))
        simulations[:, 0] = self.initial_rate  # Starting rate for all simulations
        
        for i in range(n_periods):
            # Current rate for all simulations
            r_current = simulations[:, i]
            
            # Generate random shocks
            dW = np.random.normal(0, np.sqrt(dt), n_simulations)
            
            # Apply Vasicek equation
            dr = a * (b - r_current) * dt + sigma * dW
            simulations[:, i + 1] = r_current + dr
            
            # Keep rates non-negative (optional constraint)
            simulations[:, i + 1] = np.maximum(simulations[:, i + 1], 0.001)
        
        return simulations
        
    def generate_yield_curves(self, n_simulations=1000):
        # Generate full yield curves, not single rates
        pass

# irm = InterestRatesModel()
# print(irm.vasicek_simulation())