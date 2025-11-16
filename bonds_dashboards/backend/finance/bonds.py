import datetime
from dateutil.relativedelta import relativedelta
from yield_curve import YieldCurve, curve


"""
This is a bonds class that has issuing date, face value, coupon rate and maturity. It calculates cash flow on a semi-annual basis.

Present value of a bond is the sum of all future cash flows (coupons + principal) discounted at the appropriate 
discount rate (yield to maturity or spot rate)

DV01 (dollar value of a basis point) is the difference between present value with a bump in interest rate and present value

Macaulay duration is the weighted average time until you receive the bond's cash flow
"""


class Bonds:
    def __init__(self, issuing_date, face_value, bond_interest, maturity):
        self.issuing_date = issuing_date
        self.face_value: float = face_value
        self.bond_interest: float = bond_interest
        self.maturity: int = maturity

    def cash_flows(self) -> list:
        fv = []
        for i in range(1, 2*self.maturity+1):
            fv.append({'date': self.issuing_date + relativedelta(months=6*i), 
               'value': self.face_value*self.bond_interest/2})
            
        fv[-1]['value'] += self.face_value
        return fv
    
    @property
    def label(self):
        return f"U.S. {self.bond_interest*100:.2f}% {self.maturity}Y"
    
    def present_value(self, yield_curve=None):
        if yield_curve is None:
            # Fallback to flat rate if no curve provided
            return self.fallback_present_value(curve.rates[curve.maturities.index(self.maturity)])
        
        cash_flows = self.cash_flows()
        present_values = []
        
        for cf in cash_flows:
            days = (cf['date'] - datetime.date.today()).days
            if days >= 0:
                years = days / 365.25
                discount_rate = yield_curve.interpolate_rate(years)
                pv = cf['value'] / ((1 + discount_rate / 100) ** years)
                present_values.append(pv)
            else:
                present_values.append(0)
                
        return sum(present_values)
    
    def fallback_present_value(self, interest_rates, day_count=365.25):
        cash_flows = self.cash_flows()
        present_values = []
        for i in cash_flows:
            days = (i['date'] - datetime.date.today()).days
            if days >= 0:
                pv = i['value'] / (1 + (interest_rates / 100) * days / day_count)
                present_values.append(pv)
            else:
                present_values.append(0)
        return sum(present_values) 
    
    def fallback_dv01(self, interest_rates, bp=1.0, day_count=360):
        bump = bp/10000.0
        cash_flows = self.cash_flows()
        present_values = []
        for i in cash_flows:
            days = (i['date'] - datetime.date.today()).days
            if days >= 0:
                pv = i['value'] / (1 + (interest_rates / 100 + bump) * days / day_count)
                present_values.append(pv)
            else:
                present_values.append(0)

        pv1 = self.fallback_present_value(interest_rates)
        return sum(present_values) - pv1
    
    def dv01(self, yield_curve=None, bp=1.0):
        if yield_curve is None:
            return self.fallback_dv01(curve.rates[curve.maturities.index(self.maturity)])
        
        bump = bp / 10000.0  
        cash_flows = self.cash_flows()
        bumped_present_values = []
        
        for cf in cash_flows:
            days = (cf['date'] - datetime.date.today()).days
            if days >= 0:
                years = days / 365.25
                rate = yield_curve.interpolate_rate(years) / 100  
                bumped_rate = rate + bump
                pv = cf['value'] / ((1 + bumped_rate) ** years)  
                bumped_present_values.append(pv)
            else:
                bumped_present_values.append(0)

        original_pv = self.present_value(yield_curve)
        bumped_pv = sum(bumped_present_values)
        return bumped_pv - original_pv
    
    def macaulay_duration(self, interest_rates, day_count=360):
        cash_flows = self.cash_flows()
        durations = []
        present_values = []
        for i in cash_flows:
            days = (i['date'] - datetime.date.today()).days
            years_to_payment = days / 365.25
            if days >= 0:
                pv = i['value'] / (1 + interest_rates / 100  * days / day_count)
                present_values.append(pv)
            else:
                present_values.append(0)
        for i in range(len(present_values)):
            days = (cash_flows[i]['date'] - datetime.date.today()).days / 365.25
            duration = present_values[i] / sum(present_values) * days
            durations.append(duration)
        return sum(durations)

    def modified_duration(self, interest_rates, day_count=360):
        """Modified Duration = Macaulay Duration / (1 + yield/frequency)"""
        mac_duration = self.macaulay_duration(interest_rates, day_count)
        
        # Approximate yield from interest rates (simplified)
        avg_yield = sum(interest_rates) / len(interest_rates)
        frequency = 2  # Semi-annual payments
        
        mod_duration = mac_duration / (1 + avg_yield / frequency)
        return mod_duration
    
curve = YieldCurve()
curve.fetch_treasury_rates()

bond_issuing_date = datetime.date.today() - relativedelta(years=4)

b1 = Bonds(bond_issuing_date, 1000, 0.04, 10)

b2 = Bonds(datetime.date.today() - relativedelta(months=1), 1000, 0.05, 1)
b3 = Bonds(datetime.date.today(), 1000, 0.1, 3)

print(b1.present_value(curve))

# print(b1.dv01(curve))
# print(b1.fallback_dv01(curve.rates[curve.maturities.index(b1.maturity)]))


   # def macaulay_duration(self, interest_rates, day_count=360):
    #     cash_flows = self.cash_flows()
    #     weighted_times = []
    #     present_values = []
        
    #     # Calculate present value of each cash flow
    #     for i in range(len(cash_flows)):
    #         days = (cash_flows[i]['date'] - datetime.date.today()).days
    #         if days >= 0:
    #             pv = cash_flows[i]['value'] / (1 + interest_rates[i] * days / day_count)
    #             present_values.append(pv)
                
    #             # Calculate time in years for this cash flow
    #             time_in_years = days / 365.25  # More accurate than days/360
                
    #             # Weight = (PV of this cash flow / Total PV) * Time
    #             weighted_time = pv * time_in_years  # We'll divide by total PV later
    #             weighted_times.append(weighted_time)
    #         else:
    #             present_values.append(0)
    #             weighted_times.append(0)
        
    #     total_pv = sum(present_values)
    #     if total_pv == 0:
    #         return 0
        
    #     # Macaulay Duration = Sum of (PV_i * Time_i) / Total_PV
    #     macaulay_duration = sum(weighted_times) / total_pv
        
    #     return macaulay_duration