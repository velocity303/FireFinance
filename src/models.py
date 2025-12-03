from dataclasses import dataclass, field
from typing import List, Literal, Tuple

@dataclass
class Milestone:
    name: str
    amount: float
    year_offset: int
    duration: int = 1
    currency: Literal["USD", "BTC"] = "USD"

@dataclass
class Asset:
    name: str
    balance: float
    currency: Literal["USD", "BTC", "STX"]
    apy: float = 0.0
    is_real_estate: bool = False
    # New Field: Determines which tax rate applies to the APY earnings
    tax_treatment: Literal["Capital Gains", "Ordinary Income"] = "Capital Gains"

@dataclass
class Stream:
    name: str
    amount: float
    currency: Literal["USD", "BTC"]
    frequency: Literal["Monthly", "Yearly"]
    is_income: bool

@dataclass
class FinanceData:
    currency_preference: str = "USD"
    display_currency: str = "USD"
    btc_price: float = 95000.00
    stx_price: float = 2.50

    tax_rate_income: float = 0.25
    tax_rate_property: float = 0.015
    tax_rate_cap_gains: float = 0.15

    assets: List[Asset] = field(default_factory=list)
    streams: List[Stream] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)

    def get_converted_value(self, amount: float, from_currency: str) -> float:
        usd_value = 0.0
        if from_currency == "USD": usd_value = amount
        elif from_currency == "BTC": usd_value = amount * self.btc_price
        elif from_currency == "STX": usd_value = amount * self.stx_price

        if self.display_currency == "USD": return usd_value
        elif self.display_currency == "BTC": return usd_value / self.btc_price
        return usd_value

    @property
    def net_worth(self) -> float:
        return sum(self.get_converted_value(a.balance, a.currency) for a in self.assets)

    @property
    def weighted_apy(self) -> float:
        total_usd = 0.0
        weighted_sum = 0.0
        for asset in self.assets:
            val_usd = self.get_converted_value(asset.balance, asset.currency)
            if self.display_currency == "BTC": val_usd = val_usd * self.btc_price
            total_usd += val_usd
            weighted_sum += (val_usd * asset.apy)
        return (weighted_sum / total_usd) if total_usd > 0 else 0.0

    @property
    def annual_income_gross(self) -> float:
        return sum(self.get_converted_value(s.amount, s.currency) * (12 if s.frequency == "Monthly" else 1) for s in self.streams if s.is_income)

    @property
    def annual_expenses_base(self) -> float:
        return sum(self.get_converted_value(s.amount, s.currency) * (12 if s.frequency == "Monthly" else 1) for s in self.streams if not s.is_income)

    @property
    def annual_burn_rate(self) -> float:
        return self.annual_income_gross - self.annual_expenses_base

    @property
    def annual_net_flow_post_tax(self) -> float:
        """
        Net Annual Change taking into account specific tax treatments of assets.
        """
        gross_salary = self.annual_income_gross
        expenses = self.annual_expenses_base

        # Calculate Investment Income separated by Tax Treatment
        inv_income_ordinary = 0.0
        inv_income_cap_gains = 0.0

        for a in self.assets:
            growth = self.get_converted_value(a.balance, a.currency) * a.apy
            if a.tax_treatment == "Ordinary Income":
                inv_income_ordinary += growth
            else:
                inv_income_cap_gains += growth

        # Tax Calculation
        # 1. Ordinary Income Bucket (Salary + Ordinary Investment Income)
        total_ordinary_income = gross_salary + inv_income_ordinary
        tax_ordinary = total_ordinary_income * self.tax_rate_income

        # 2. Capital Gains Bucket
        tax_cap_gains = inv_income_cap_gains * self.tax_rate_cap_gains

        # 3. Property Tax
        prop_val = sum(self.get_converted_value(a.balance, a.currency) for a in self.assets if a.is_real_estate)
        tax_prop = prop_val * self.tax_rate_property

        # Result: (All Income) - (All Taxes) - Expenses
        total_income = gross_salary + inv_income_ordinary + inv_income_cap_gains
        total_taxes = tax_ordinary + tax_cap_gains + tax_prop

        return total_income - total_taxes - expenses

    def get_projection(self, years=30) -> List[float]:
        values = []
        running_balance = self.net_worth

        gross_salary = self.annual_income_gross
        base_expenses = self.annual_expenses_base

        # Determine "Blended Tax Rate on Growth" for the projection
        # This keeps the projection loop fast while respecting the portfolio composition
        total_growth_potential = 0.0
        total_tax_on_growth = 0.0

        for a in self.assets:
            val = self.get_converted_value(a.balance, a.currency)
            growth = val * a.apy

            rate = self.tax_rate_income if a.tax_treatment == "Ordinary Income" else self.tax_rate_cap_gains

            total_growth_potential += growth
            total_tax_on_growth += (growth * rate)

        # Effective tax rate on the portfolio's APY
        effective_growth_tax_rate = 0.0
        if total_growth_potential > 0:
            effective_growth_tax_rate = total_tax_on_growth / total_growth_potential

        avg_apy = self.weighted_apy

        # Ratio of Real Estate to Total (for estimating future property tax)
        re_ratio = 0.0
        if self.net_worth > 0:
            re_val = sum(self.get_converted_value(a.balance, a.currency) for a in self.assets if a.is_real_estate)
            re_ratio = re_val / self.net_worth

        for year in range(years):
            # 1. Income Tax (Salary only here, growth tax handled below)
            salary_tax = gross_salary * self.tax_rate_income

            # 2. Property Tax (Based on projected portfolio size * real estate ratio)
            curr_prop_val = running_balance * re_ratio
            prop_tax = curr_prop_val * self.tax_rate_property

            # 3. Growth & Growth Tax
            growth = running_balance * avg_apy
            growth_tax = growth * effective_growth_tax_rate

            # 4. Milestones
            milestone_costs = 0.0
            for m in self.milestones:
                if m.year_offset <= year < (m.year_offset + m.duration):
                    milestone_costs += self.get_converted_value(m.amount, m.currency)

            # 5. Net Flow
            # (Salary - SalTax) + (Growth - GrowthTax) - (Expenses + Milestones + PropTax)
            net_flow = (gross_salary - salary_tax) + (growth - growth_tax) - (base_expenses + milestone_costs + prop_tax)

            running_balance += net_flow
            values.append(running_balance)

        return values
