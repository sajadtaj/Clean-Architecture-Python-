# core/entities/option/etf_option.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.entities.option.option import AbstractOption
from core.entities.asset.etf_asset import ETFAsset
from core.entities.enum.enums import OptionType


@dataclass
class ETFOption(AbstractOption):
    underlying_asset: ETFAsset
    benchmark_index: Optional[str] = None  # مثلاً "S&P 500", "شاخص هم‌وزن"
    nav_deviation: Optional[float] = None  # اختلاف قیمت بازار با NAV

    def calculate_raw_payoff(self, spot_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0.0, spot_price - self.strike_price)
        return max(0.0, self.strike_price - spot_price)

    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        spot = spot_price or self.spot_price
        raw_payoff_per_unit = self.calculate_raw_payoff(spot)

        # ✅ هزینه‌ها برای یک واحد
        fee_per_unit = (self.transaction_fee / 100 * spot) if self.transaction_fee else 0
        settle_per_unit = (self.settlement_cost / 100 * spot) if self.settlement_cost else 0



        total_cost_per_unit = self.premium + fee_per_unit + settle_per_unit
        return (raw_payoff_per_unit - total_cost_per_unit) * self.contract_size

    def get_break_even_price(self) -> float:
        fee = (self.transaction_fee / 100 * self.strike_price) if self.transaction_fee else 0
        settle = (self.settlement_cost / 100 * self.strike_price) if self.settlement_cost else 0
        return self.strike_price + self.premium + fee + settle


    def is_liquid(self) -> bool:
        """
        بررسی نقدشوندگی: اگر اسپرد خیلی زیاد باشد، نقدشوندگی پایین است.
        """
        spread = self.underlying_asset.get_spread()
        if spread is None:
            return False
        return spread / self.underlying_asset.last_price < 0.02  # کمتر از ۲٪

    def has_nav_deviation(self, nav_price: float) -> bool:
        """
        بررسی انحراف قیمت نسبت به NAV
        """
        deviation = abs(self.spot_price - nav_price) / nav_price
        self.nav_deviation = deviation
        return deviation > 0.03  # بیشتر از ۳٪
