from .bonds import Bonds, b1, bond_issuing_date, b2
from .yield_curve import YieldCurve

class Portfolio:
    def __init__(self):
        self.bonds: list[Bonds] = []
        self.usd_amount = []

    @property
    def print_bonds(self):
        return [f"{j.label} ${self.usd_amount[b]:,.0f}" for b, j in enumerate(self.bonds)]

    def add_bond(self, bond, dollar_amount):
        if dollar_amount <= 0:
            raise ValueError("Dollar amount must be positive")
        self.bonds.append(bond)
        self.usd_amount.append(dollar_amount)
    
    @property
    def total_value(self):
        s = sum(self.usd_amount)
        return s
    
    @property
    def weights(self):
        total = self.total_value
        return [amount/total for amount in self.usd_amount]
    
    # def portfolio_present_value(self, interest_rates):
    #     pv = 0
    #     for i in range(0, len(self.bonds)):
    #         pv += self.bonds[i].present_value(interest_rates) * self.usd_amount[i] / self.bonds[i].face_value
    #     return pv
    
    def portfolio_present_value(self, yield_curve=None):
        total_pv = 0
        for i, bond in enumerate(self.bonds):
            bond_pv = bond.present_value(yield_curve)
            investment_pv = bond_pv * self.usd_amount[i] / bond.face_value
            total_pv += investment_pv
        return total_pv
    
    def portfolio_dv01(self, yield_curve=None):
        pv = 0
        for i in range(0, len(self.bonds)):
            pv += self.bonds[i].dv01(yield_curve) * self.usd_amount[i] / self.bonds[i].face_value
        return pv
    
    def portfolio_duration(self, interest_rates):
        port_dur = 0
        for i in range(0, len(self.bonds)):
           port_dur += self.bonds[i].macaulay_duration(interest_rates) * self.weights[i]
        return port_dur
    
    # def scenario_analysis(self, rate_scenarios):
    #     """Analyze portfolio performance across different rate scenarios"""
    #     results = {}
    #     base_pv = self.portfolio_present_value(interest_rate)  # Assuming this is base case
        
    #     for scenario_name, rates in rate_scenarios.items():
    #         scenario_pv = self.portfolio_present_value(rates)
    #         pnl = scenario_pv - base_pv
    #         pnl_pct = (pnl / base_pv) * 100 if base_pv != 0 else 0
            
    #         results[scenario_name] = {
    #             'present_value': scenario_pv,
    #             'pnl_dollar': pnl,
    #             'pnl_percent': pnl_pct,
    #             'dv01': self.portfolio_dv01(rates),
    #             'duration': self.portfolio_duration(rates)
    #         }
    #     return results

    def get_portfolio_summary(self, interest_rates):
        """Get complete portfolio summary for API"""
        return {
            'portfolio_present_value': self.portfolio_present_value(interest_rates),
            'portfolio_dv01': round(self.portfolio_dv01(interest_rates)),
            'portfolio_duration': self.portfolio_duration(interest_rates),
            'total_dollar_amount': self.total_value,
            #'total_face_value': sum([bond.face_value * weight / bond.face_value for bond, weight in zip(self.bonds, self.usd_amount)]),
            'number_of_bonds': len(self.bonds),
            'bonds_detail': self.print_bonds,
            'average_coupon': sum([bond.bond_interest * weight for bond, weight in zip(self.bonds, self.weights)]),
            'average_maturity': sum([bond.maturity * weight for bond, weight in zip(self.bonds, self.weights)])
        }


curve = YieldCurve()
curve.fetch_treasury_rates()
p1 = Portfolio()
p1.add_bond(b1, 400000)
p1.add_bond(b2, 500000)

if __name__ == '__main__':
    print(p1.weights)
    print(p1.bonds[1].present_value())
    print(p1.portfolio_present_value())

# Test scenario analysis
# rate_scenarios = {
#     'base': interest_rate,
#     'fed_hike_100bp': [r + 0.01 for r in interest_rate],
#     'fed_cut_50bp': [r - 0.005 for r in interest_rate]
# }

# scenarios = p1.scenario_analysis(rate_scenarios)
# for scenario, results in scenarios.items():
#     print(f"{scenario}: PnL = ${results['pnl_dollar']:,.2f} ({results['pnl_percent']:.2f}%)")


"""
Time Series ML Applications:
1. Interest Rate Forecasting with Neural Networks

LSTM/GRU networks to predict Treasury yield movements
Compare against Vasicek model predictions
Feature engineering: Fed speeches, economic indicators, yield curve shapes
Rolling window validation on historical data

2. Regime Detection in Bond Markets

Hidden Markov Models or clustering to identify market regimes (bull/bear, high/low volatility)
Use regime states to adjust portfolio allocation dynamically
Bayesian learning to update regime probabilities

Collaborative Filtering for Portfolio Construction:
3. Bond Recommendation System

Treat institutional portfolios as "users" and bonds as "items"
Matrix factorization to find similar portfolio strategies
Cold start problem: recommend bonds for new portfolio mandates

Bayesian Learning & Monte Carlo:
4. Bayesian Portfolio Optimization

Bayesian updating of expected returns as new data arrives
MCMC sampling for portfolio allocation under parameter uncertainty
Compare frequentist vs Bayesian risk estimates

5. Monte Carlo for Credit Risk

Simulate correlated default events across bond portfolio
Copula models for dependency structure
Stress testing under tail scenarios

Neural Networks for News/Market Signals:
6. Sentiment-Driven Yield Prediction

NLP on Fed minutes, economic news
Attention mechanisms to weight different news sources
Real-time prediction of bond price movements

7. Multimodal Learning

Combine numerical market data with textual news data
Transformer architecture for joint embedding
Predict portfolio performance from mixed signals

Recommended Approach:
Start with time series forecasting using LSTMs for interest rates - 
it's directly applicable to your bond dashboard and covers neural networks + time series from your syllabus. 
Then add Bayesian portfolio optimization as a second component to cover Bayesian learning and Monte Carlo methods.
"""