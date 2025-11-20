
class PremiumCalculator:

    #base rate = 4%
    #monthly rate = base rate / 12

    def __init__(self,base_percent_annual=4):
        self.base_percent_annual = base_percent_annual

    def calculate_premium(self,declared_value,cover_months):
        if declared_value <=0:
            raise ValueError("declared value must be positive")
        if cover_months <=0:
            raise ValueError("cover months must be positive")
        
        base_annual = (self.base_percent_annual/100)*declared_value
        monthly = base_annual/12
        total = monthly * cover_months

        #simple discount 2% off if cover >=12 months and 5% off if >=24
        if cover_months >=24:
            discount = 0.05
        elif cover_months >=12:
            discount = 0.02
        else:
            discount = 0.0

        return round(total * (1-discount),2)